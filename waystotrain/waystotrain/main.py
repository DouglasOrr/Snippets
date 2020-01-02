import collections
import itertools as it
import sys
import time

import torch as T
import torchvision

from . import utility


Batch = collections.namedtuple('Batch', ('epoch', 'batch', 'example', 'x', 'y'))
Batch.cuda = lambda self: self._replace(x=self.x.cuda(), y=self.y.cuda())


def batches(dataset, batch_size, loop):
    loader = T.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
    batch = 0
    example = 0
    for epoch in it.count():
        for x, y in loader:
            example += len(y)
            batch += 1
            yield Batch(epoch=epoch, batch=batch, example=example, x=x, y=y)
        if not loop:
            break


def evaluate(batches, model):
    errors = 0
    cross_entropy = 0
    samples = 0
    for batch in batches:
        scores = model(batch.x)
        errors += int((scores.argmax(-1) != batch.y).sum())
        cross_entropy += float(T.nn.functional.cross_entropy(scores, batch.y, reduction='sum'))
        samples += len(batch.y)
    return dict(samples=samples,
                error_rate=errors/samples,
                cross_entropy=cross_entropy/samples)


def log_stderr(d):
    n_example = d['total']['example']
    n_batch = d['total']['batch']
    valid_error = d['valid']['error_rate']
    valid_xent = d['valid']['cross_entropy']
    train_error = ('{:.1%}'.format(d['train']['error_rate'])
                   if 'error_rate' in d['train'] else
                   'None')
    sys.stderr.write(f'{n_batch} batches, {n_example:.1e} examples'
                     f', {valid_error:.1%} ({train_error}), {valid_xent:.2f}\n')


def _conv_subnet(nonlinearity, specs, in_channels):
    """Return a list of convolution & nonlinearity modules for the given specs."""
    modules = []
    for kernel_hwidth, out_channels in specs:
        if modules:
            modules.append(nonlinearity())  # only put nonlinearities between convs
        modules.append(T.nn.Conv2d(in_channels, out_channels, 2*kernel_hwidth+1, padding=kernel_hwidth))
        in_channels = out_channels
    return modules


def conv_pool_model(nonlinearity, pooling, final_pooling, levels, dropout,
                    ninput_channels, noutput):
    """Create a flexible convolution-pooling model.

    Inspired by https://arxiv.org/pdf/1505.00853v2.pdf

    nonlinearity -- e.g. T.nn.ReLU

    pooling -- e.g. T.nn.MaxPool2d

    final_pooling -- e.g. Max2d, Avg2d

    levels -- [[(kernel_hwidth, out_channels)]] -- list of layer shapes for each /2 pooling

    dropout -- after every level (except the first)
    """
    modules = []
    modules += _conv_subnet(nonlinearity, levels[0], ninput_channels)
    for prev_level, level in zip(levels, levels[1:]):
        modules.append(pooling(2))
        modules += _conv_subnet(nonlinearity, level, in_channels=prev_level[-1][1])
        modules.append(T.nn.Dropout2d(dropout))
        modules.append(nonlinearity())
    modules.append(T.nn.Conv2d(levels[-1][-1][1], noutput, kernel_size=1))
    modules.append(final_pooling())
    return T.nn.Sequential(*modules)


class Cifar10Experiment:
    DATA_PATH = 'data/cifar10'
    TRANSFORM = torchvision.transforms.ToTensor()

    @classmethod
    def training_data(cls):
        return torchvision.datasets.CIFAR10(cls.DATA_PATH, download=True, transform=cls.TRANSFORM)

    @classmethod
    def test_data(cls):
        return torchvision.datasets.CIFAR10(cls.DATA_PATH, download=True, transform=cls.TRANSFORM,
                                            train=False)

    @staticmethod
    def model(extra_outputs=0):
        return conv_pool_model(
            nonlinearity=T.nn.LeakyReLU,
            pooling=T.nn.MaxPool2d,
            final_pooling=utility.Avg2d,
            levels=[[(1, 64), (1, 64)],
                    [(1, 64), (2, 64), (0, 128)],
                    [(1, 128), (2, 128), (0, 256)]],
            dropout=0.5,
            ninput_channels=3,
            noutput=10 + extra_outputs,
        )


class MnistExperiment:
    DATA_PATH = 'data/mnist'
    TRANSFORM = torchvision.transforms.ToTensor()

    @staticmethod
    def training_settings():
        return dict(
            examples_per_batch=100,
            batches_per_chunk=10,
            chunks_per_run=100,
        )

    @classmethod
    def training_data(cls):
        return torchvision.datasets.MNIST(cls.DATA_PATH, download=True, transform=cls.TRANSFORM)

    @classmethod
    def test_data(cls):
        return torchvision.datasets.MNIST(cls.DATA_PATH, download=True, transform=cls.TRANSFORM,
                                          train=False)

    @staticmethod
    def model(extra_outputs=0):
        return T.nn.Sequential(
            T.nn.Flatten(),
            T.nn.Linear(1 * 28 * 28, 10 + extra_outputs),
        )


class TinyExperiment:
    TARGET_TRANSFORM = T.FloatTensor([[0, 0, 0], [1, 1, -2], [-1, -1, 2], [3, -2, -1]]).T
    DATA_X = T.FloatTensor([[x, y, z]
                            for x in T.linspace(-1, 1, 10)
                            for y in T.linspace(-1, 1, 10)
                            for z in T.linspace(-1, 1, 10)])
    DATA = list(map(tuple, zip(DATA_X, T.argmax(DATA_X @ TARGET_TRANSFORM, -1))))

    @staticmethod
    def training_settings():
        return dict(
            examples_per_batch=1000,
            batches_per_chunk=1,
            chunks_per_run=100,
        )

    @classmethod
    def training_data(cls):
        return cls.DATA

    @classmethod
    def test_data(cls):
        return cls.DATA

    @classmethod
    def model(cls, extra_outputs=0):
        n_input = cls.TARGET_TRANSFORM.shape[0]
        n_output = cls.TARGET_TRANSFORM.shape[1]
        return T.nn.Linear(n_input, n_output + extra_outputs)


def train(experiment, trainer_factory, log, cuda=None):
    if cuda is None:
        cuda = T.cuda.is_available()

    def map_cuda(batches):
        return (b.cuda() for b in batches) if cuda else batches

    def create_model(**args):
        model = experiment.model(**args)
        return model.cuda() if cuda else model
    trainer = trainer_factory(create_model)

    settings = experiment.training_settings()
    valid_batches = list(batches(experiment.test_data(), settings['examples_per_batch'], loop=False))
    t0 = time.time()

    def _eval(train_subset, epoch, batch, example):
        model = trainer.trained_model()
        model.eval()
        log(dict(train={} if train_subset is None else evaluate(map_cuda(train_subset), model),
                 valid=evaluate(map_cuda(valid_batches), model),
                 total=dict(time=time.time()-t0,
                            epoch=epoch,
                            batch=batch,
                            example=example)))
        model.train()

    _eval(None, 0, 0, 0)
    train_batches = batches(experiment.training_data(), settings['examples_per_batch'], loop=True)
    for chunk in it.islice(utility.group_chunks(train_batches, settings['batches_per_chunk']),
                           settings['chunks_per_run']):
        for batch in map_cuda(chunk):
            trainer.step(batch)
        _eval(chunk[-len(valid_batches):], batch.epoch, batch.batch, batch.example)
    return trainer.trained_model()
