import glob
import json
import os

import numpy as np
import pandas as pd
import torch as T


def flat_items(d, prefix):
    """Recurses through a dict-of-dicts yielding ((key_0..key_n), value)."""
    if isinstance(d, dict):
        for k, v in d.items():
            yield from flat_items(v, prefix + (k,))
    else:
        yield prefix, d


class Log:
    def __init__(self, path, header):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self._log = open(path, 'w')
        self.write(header, flush=True)

    def write(self, item, flush=False):
        self._log.write(f'{json.dumps(item)}\n')
        if flush:
            self._log.flush()

    @staticmethod
    def load(path):
        def flat_dict(d):
            return {'_'.join(k): v for k, v in flat_items(d, ())}
        with open(path, 'r') as f:
            header = flat_dict(json.loads(next(f)))
            df = pd.DataFrame.from_dict(flat_dict(json.loads(line)) for line in f)
            return df.assign(**header)

    @classmethod
    def load_dir(cls, path):
        return pd.concat([cls.load(f) for f in glob.glob(f'{path}/*')], sort=False).reset_index()


def sample_multinomial(probs):
    """Generate a multinomial sample for each row of `probs`."""
    samples = T.rand(probs.shape[0], device=probs.device)
    indices = (T.cumsum(probs, -1) < samples[:, np.newaxis]).sum(-1)
    return T.clamp(indices, 0, probs.shape[1])


class SubsetOutputs(T.nn.Module):
    def __init__(self, model, start=None, end=None):
        super().__init__()
        self._model = model
        self.start = start
        self.end = end

    def forward(self, x):
        return self._model(x)[..., self.start:self.end]


class Max2d(T.nn.Module):
    def forward(self, x):
        return x.view(*x.shape[:-2], -1).max(-1)[0]


class Avg2d(T.nn.Module):
    def forward(self, x):
        return x.mean((-2, -1))
