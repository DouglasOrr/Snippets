import numpy as np
import torch as T

from . import utility


class Trainer:
    """Abstract base for different training methods

    Trainer should be created as `Trainer(model_factory, **args)`.
    """
    def step(self, batch):
        """Advance training by a single batch."""
        raise NotImplementedError

    def trained_model(self):
        """Get the trained model."""
        raise NotImplementedError


class BaseSgdTrainer(Trainer):
    def __init__(self, model_factory, optimizer):
        self._model = model_factory()
        self._opt = optimizer(self._model.parameters())

    def _loss(self, batch):
        raise NotImplementedError

    def step(self, batch):
        self._opt.zero_grad()
        self._loss(batch).backward()
        self._opt.step()

    def trained_model(self):
        return self._model


class CrossEntropyTrainer(BaseSgdTrainer):
    def _loss(self, batch):
        return T.nn.functional.cross_entropy(self._model(batch.x), batch.y)


class NegativeSamplingTrainer(BaseSgdTrainer):
    def __init__(self, model_factory, optimizer, nsamples):
        super().__init__(model_factory, optimizer)
        self.nsamples = nsamples

    def _loss(self, batch):
        scores = self._model(batch.x)
        idx = T.arange(batch.y.shape[0])
        samples_idx = idx.repeat(self.nsamples)
        samples = T.randint(0, scores.shape[-1], (samples_idx.shape[0],))
        positive = -T.nn.functional.logsigmoid(scores[idx, batch.y])
        negative = -T.nn.functional.logsigmoid(-scores[samples_idx, samples])
        return positive.mean() + negative.mean()


class TeacherStudentTrainer(BaseSgdTrainer):
    def __init__(self, model_factory, optimizer, teacher, hard_weight):
        super().__init__(model_factory, optimizer)
        self._teacher = teacher
        self._teacher.eval()
        self.hard_weight = hard_weight

    def _loss(self, batch):
        with T.no_grad():
            teacher_scores = T.nn.functional.softmax(self._teacher(batch.x), -1)
        scores = T.nn.functional.log_softmax(self._model(batch.x), -1)
        loss = T.nn.functional.kl_div(scores, teacher_scores, reduction='batchmean')
        if 0 < self.hard_weight:
            loss += self.hard_weight * T.nn.functional.nll_loss(scores, batch.y)
        return loss


class ValueFunctionTrainer(BaseSgdTrainer):
    """Like Q learning, but without the temporal difference part.

    Tries to predict the value of each action (accuracy).
    """
    def __init__(self, model_factory, optimizer, epsilon):
        super().__init__(model_factory, optimizer)
        self.epsilon = epsilon

    def _loss(self, batch):
        nbatch = batch.y.shape[0]
        values = T.sigmoid(self._model(batch.x))
        with T.no_grad():
            selected = T.where(T.rand(nbatch, device=batch.x.device) < self.epsilon,
                               T.randint(0, values.shape[1], (nbatch,), device=batch.x.device),
                               T.argmax(values, -1))
            reward = (selected == batch.y).float()
        return T.nn.functional.binary_cross_entropy(
            values[T.arange(nbatch), selected], reward
        ).mean()  # TODO..?


class ReinforceTrainer(Trainer):
    def __init__(self, model_factory, optimizer, baseline):
        self.baseline = baseline
        self._model = model_factory(extra_outputs=baseline)
        self._opt = optimizer(self._model.parameters())

    def _update_gradients(self, batch):
        output = self._model(batch.x)
        if self.baseline:
            logp = T.nn.functional.log_softmax(output[..., :-1], -1)
            baseline = T.sigmoid(output[..., -1])
            with T.no_grad():
                actions = utility.sample_multinomial(T.exp(logp))
                reward = (actions == batch.y).float()
                value = reward - baseline
            T.nn.functional.binary_cross_entropy(baseline, reward).backward(retain_graph=True)
        else:
            logp = T.nn.functional.log_softmax(output, -1)
            with T.no_grad():
                actions = utility.sample_multinomial(T.exp(logp))
                value = (actions == batch.y).float()
        grad = value[:, np.newaxis] * T.nn.functional.one_hot(actions, logp.shape[-1])
        logp.backward(-grad / batch.y.shape[0])

    def step(self, batch):
        self._opt.zero_grad()
        self._update_gradients(batch)
        self._opt.step()

    def trained_model(self):
        return utility.SubsetOutputs(self._model, end=-1) if self.baseline else self._model


class EvolutionaryTrainer(Trainer):
    def __init__(self, model_factory, step_size, noise_std, half_nsamples):
        self.step_size = step_size
        self.noise_std = noise_std
        self.half_nsamples = half_nsamples
        self._model = model_factory()
        self._model_params = T.nn.utils.parameters_to_vector(self._model.parameters())
        T.nn.utils.vector_to_parameters(self._model_params, self._model.parameters())
        self._test_model = model_factory()
        self._test_params = T.nn.utils.parameters_to_vector(self._test_model.parameters())
        T.nn.utils.vector_to_parameters(self._test_params, self._test_model.parameters())

    def _returns(self, batch, peturbation):
        self._test_params.data[:] = self._model_params + peturbation
        return (T.argmax(self._test_model(batch.x), -1) == batch.y).float().mean()

    def step(self, batch):
        with T.no_grad():
            step = self.step_size / (self.noise_std * 2 * self.half_nsamples)
            delta = T.zeros_like(self._model_params)
            for _ in range(self.half_nsamples):
                peturbation = T.randn_like(self._model_params).mul_(self.noise_std)
                delta.add_(peturbation, alpha=step * self._returns(batch, peturbation))
                peturbation.mul_(-1)
                delta.add_(peturbation, alpha=step * self._returns(batch, peturbation))
            self._model_params.add_(delta)

    def trained_model(self):
        return self._model
