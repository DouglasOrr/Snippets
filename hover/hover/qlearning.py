import torch as T
import numpy as np

from . import core


class Model(T.nn.Module):
    def __init__(self, hidden_size):
        super().__init__()
        self.in_features = T.nn.Linear(6, hidden_size)
        d = .2 * (self.in_features.in_features) ** -.5
        T.nn.init.uniform_(self.in_features.weight, -d, d)
        self.predict = T.nn.Linear(hidden_size, 4)

    def forward(self, x):
        h = T.relu(self.in_features(x))
        return self.predict(h)


class Agent:
    def __init__(self):
        # Fixed state (settings)
        self.discount = .95
        self.ticks_per_action = 10
        self.greed = .9
        self.qsteps = 5
        self.max_buffer = 1000
        self.update_sample = 100
        self.actions = [(False, False), (False, True), (True, False), (True, True)]

        # Transient state
        self.model = Model(100)
        self.buffer = []
        self.random = np.random.RandomState()
        self.pre_buffer = []
        self.opt = T.optim.Adam(self.model.parameters())

    def _update(self, log):
        if self.update_sample <= len(self.buffer):
            self.opt.zero_grad()
            indices = self.random.randint(0, len(self.buffer), self.update_sample)
            states = T.FloatTensor([self.buffer[idx][0] for idx in indices])
            actions = T.LongTensor([self.buffer[idx][1] for idx in indices])
            rewards = T.FloatTensor([self.buffer[idx][2] for idx in indices])

            y = self.model(states)[T.arange(self.update_sample), actions]
            loss = (1 - self.discount) * ((y - rewards) ** 2).sum()
            log.append('loss', loss=float(loss))
            loss.backward()
            self.opt.step()

    def _act(self, state, greedy):
        if greedy or self.random.rand() < self.greed:
            return int(T.argmax(self.model(T.FloatTensor(state))))
        else:
            return self.random.randint(len(self.actions))

    def _add_memory(self, state, action, reward, log):
        if self.qsteps == len(self.pre_buffer):
            sar = self.pre_buffer.pop(0)
            sar[2] += (self.discount ** self.qsteps) * float(T.max(self.model(T.FloatTensor(state))))
            self.buffer.append(sar)
        self.pre_buffer.append([state, action, 0])
        for n in range(len(self.pre_buffer)):
            self.pre_buffer[-1 - n][2] += reward * (self.discount ** n)
        self._update(log)

    def _flush_and_trim_buffer(self):
        self.buffer += self.pre_buffer
        self.pre_buffer = []
        self.buffer = self.buffer[-self.max_buffer:]

    def train(self, log):
        """Train the agent on a single game."""
        game = core.Game()
        while True:
            state = game.state
            action = self._act(state, greedy=False)
            outcome = game.step_multi(self.actions[action], self.ticks_per_action)
            self._add_memory(state, action, outcome is None or outcome.success, log)
            if outcome:
                self._flush_and_trim_buffer()
                log.append('outcome', **outcome.to_json())
                return

    def __call__(self, state):
        """Evaluation policy - greedy as anything."""
        return self.actions[self._act(state, greedy=True)]
