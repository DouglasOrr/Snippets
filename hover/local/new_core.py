from contextlib import contextmanager
import glob
import json
import itertools as it
import os
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import torch as T

import hover_game as G


# TODO - change?
class Report:
    ################################################################################
    # Saving

    @staticmethod
    def _evaluate_one(agent):
        runner = G.Runner(None, [1])
        while True:
            state = runner.state()
            if state.outcome != state.Outcome.Continue:
                return dict(outcome=str(state.outcome),
                            elapsed=state.elapsed)
            runner.step(agent(state))

    @staticmethod
    @contextmanager
    def _mapper(nproc):
        if nproc == 1:
            yield map
        else:
            with T.multiprocessing.Pool(nproc) as pool:
                yield pool.map

    @staticmethod
    def _open_write(path, mode='w'):
        parent = os.path.dirname(path)
        if not os.path.isdir(parent):
            os.makedirs(parent)
        return open(path, mode)

    @classmethod
    def about(cls, path, name, kind, **args):
        with cls._open_write(os.path.join(path, 'about.json')) as file:
            json.dump(dict(name=name, kind=kind, **args), file)

    @classmethod
    def test(cls, path, agent, ngames, nproc=T.multiprocessing.cpu_count()):
        with cls._mapper(nproc) as mapper, \
             cls._open_write(os.path.join(path, 'test.jsonl')) as file:
            for result in mapper(cls._evaluate_one, it.repeat(agent, ngames)):
                json.dump(result, file)
                file.write('\n')

    @classmethod
    def agent(cls, path, agent):
        with cls._open_write(os.path.join(path, 'agent.pkl'), 'wb') as file:
            T.save(agent, file)

    class Training:
        def __init__(self, root):
            self._root = root
            self._logs = {}
            self._t0 = time.time()
            if not os.path.isdir(root):
                os.makedirs(root)

        def __enter__(self):
            return self

        def __exit__(self, type, value, traceback):
            self.close()

        def close(self):
            for file in self._logs.values():
                file.close()

        def append(self, name, **row):
            if name not in self._logs:
                self._logs[name] = open(os.path.join(self._root, name + '.jsonl'), 'w')
            log = self._logs[name]
            json.dump(dict(t=time.time()-self._t0, **row), log)
            log.write('\n')

    @classmethod
    def training(cls, path):
        return cls.Training(os.path.join(path, 'training'))

    ################################################################################
    # Loading

    @classmethod
    def load(cls, root):
        parts = []
        keys = set([])
        for about_path in glob.glob(os.path.join(root, '**/about.json')):
            df = pd.read_json(os.path.join(os.path.dirname(about_path), 'test.jsonl'),
                              lines=True)
            with open(about_path) as f:
                about = json.load(f)
                keys |= about.keys()
                for key, value in about.items():
                    df[key] = value
            parts.append(df)
        keys = ['kind', 'name'] + list(sorted(keys - {'kind', 'name'}))
        return cls(pd.concat(parts), keys)

    def __init__(self, data, keys):
        self.data = data
        self.keys = keys

    def _repr_html_(self):
        # *1 is a trick to convert booleans to numeric
        return (self.data * 1).groupby(list(self.keys)).mean()._repr_html_()

    def plot_duration(self):
        plt.figure(figsize=(10, 6))
        bins = np.logspace(np.floor(np.log10(self.data.duration.min())),
                           np.ceil(np.log10(self.data.duration.max())),
                           num=40)
        names = sorted(set(self.data.name))
        for name in names:
            sns.distplot(self.data.duration[self.data.name == name], kde=False, bins=bins)
        plt.gca().set_xscale('log')
        plt.legend(names)
        plt.title('Game duration')
