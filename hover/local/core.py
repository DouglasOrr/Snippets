import collections
from contextlib import contextmanager
import functools as ft
import glob
import json
import itertools as it
import os
import time

import Box2D as B
import IPython.display
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import torch as T

from . import render


State = collections.namedtuple('State', ('x', 'y', 'a', 'dx', 'dy', 'da'))

@dataclass(frozen=True)
class Outcome:
    kind: str
    success: bool
    duration: float

    def to_json(self):
        return dict(kind=self.kind, success=self.success, duration=self.duration)


class Game:
    def __init__(self, seed=None):
        # Settings
        self.timestep = 0.01
        self.thrust = 15
        self.hwidth = 0.4
        self.hheight = 2
        self.max_time = 20

        # Transient
        self.elapsed_steps = 0
        self.elapsed_time = 0.0
        self.control = (False, False)
        random = np.random.RandomState(seed)  # pylint: disable=no-member

        # Box2D/hover.render
        self.world = B.b2World(gravity=(0, -10))
        self.ground = self.world.CreateStaticBody(
            position=[0, -10],
            shapes=B.b2PolygonShape(box=(50, 10)),
        )
        self.rocket = self.world.CreateDynamicBody(
            position=[0, 15],
            angle=1.0 * (random.rand()-0.5)
        )
        w = self.hwidth
        h = self.hheight
        t = 2 * self.hwidth
        self.rocket.CreatePolygonFixture(
            vertices=[
                (-2*w, -h),
                (2*w, -h),
                (w, t-h),
                (-w, t-h),
            ],
            density=1,
            friction=1,
        )
        self.rocket.CreatePolygonFixture(
            vertices=[
                (-w, t-h),
                (w, t-h),
                (w, h-w),
                (0, h),
                (-w, h-w),
            ],
            density=1,
            friction=1,
        )
        d = 2 * self.hwidth
        self.left_thruster_shape = render.PolygonShape(
            color='orange',
            vertices=(
                (-2*w, -h),
                (-w, -h-d),
                (0, -h),
            ))
        self.right_thruster_shape = render.PolygonShape(
            color='orange',
            vertices=(
                (0, -h),
                (w, -h-d),
                (2*w, -h),
            ))

    @staticmethod
    def _convert_body(body, color, extra_shapes=()):
        return render.Body(
            x=body.position.x,
            y=body.position.y,
            angle=body.angle,
            shapes=tuple(
                render.PolygonShape(vertices=tuple(fixture.shape.vertices), color=color)
                for fixture in body.fixtures
            ) + tuple(extra_shapes)
        )

    def draw(self):
        """Render the game to svg.

        returns -- string -- SVG
        """
        ground = self._convert_body(self.ground, 'black')
        rocket = self._convert_body(
            self.rocket, 'blue',
            ((self.left_thruster_shape,) if self.control[0] else ()) +
            ((self.right_thruster_shape,) if self.control[1] else ()))
        return render.draw(
            render.Scene(bounds=(-30, 30, -1, 29),
                         width=800,
                         bodies=(ground, rocket)))

    def _repr_html_(self):
        return self.draw()

    @property
    def state(self):
        """Returns the State tuple, that describes the rocket."""
        position = self.rocket.position
        angle = self.rocket.angle
        dposition = self.rocket.linearVelocity
        dangle = self.rocket.angularVelocity
        return State(position.x, position.y, angle, dposition.x, dposition.y, dangle)

    def _in_bounds(self):
        position = self.rocket.position
        angle = self.rocket.angle
        return abs(position.x) < 20 and 4 <= position.y < 25 and abs(angle) < 1.5

    def step(self, control):
        """Take a single step in the game.

        control -- (float, float) -- (fire_left, fire_right) -- thrusters

        returns -- Outcome|None -- outcome of the game, if finished
        """
        self.control = control
        thrust_v = self.rocket.GetWorldVector([0, self.rocket.mass * self.thrust])
        if control[0]:
            self.rocket.ApplyForce(thrust_v, self.rocket.GetWorldPoint([-self.hwidth, -self.hheight]), True)
        if control[1]:
            self.rocket.ApplyForce(thrust_v, self.rocket.GetWorldPoint([self.hwidth, -self.hheight]), True)
        self.world.Step(self.timestep, 5, 5)
        self.elapsed_steps += 1
        self.elapsed_time += self.timestep
        if self.max_time <= self.elapsed_time:
            return Outcome('timeout', True, self.elapsed_time)
        if not self._in_bounds():
            return Outcome('outofbounds', False, self.elapsed_time)

    def step_multi(self, control, ticks):
        """Take multiple steps with the same control input.

        returns -- Outcome|None
        """
        for _ in range(ticks):
            outcome = self.step(control)
            if outcome:
                return outcome

    @classmethod
    def play(cls, agent, steps_per_control=1):
        """Play a complete game and return the outcome."""
        game = cls()
        control = agent(game.state)
        while True:
            outcome = game.step(control)
            if outcome:
                return outcome
            if game.elapsed_steps % steps_per_control == 0:
                control = agent(game.state)

    @classmethod
    def play_and_display(cls, agent, steps_per_render=10, steps_per_control=1):
        """Render a game in IPython, as updating HTML."""
        game = cls()
        display = IPython.display.display(game, display_id=True)
        control = agent(game.state)
        while True:
            for _ in range(steps_per_render):
                outcome = game.step(control)
                if outcome:
                    return outcome
                if game.elapsed_steps % steps_per_control == 0:
                    control = agent(game.state)
            display.update(game)
            time.sleep(game.timestep * steps_per_render)


class Report:
    ################################################################################
    # Saving

    @staticmethod
    def _evaluate_one(agent):
        return Game.play(agent).to_json()

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


class IntegratorAgent:
    """Turn a continuous agent into a PWM discrete agent (suitable for the game)."""
    def __init__(self, agent):
        self.agent = agent
        self._left = 0
        self._right = 0

    def __call__(self, state):
        ltarget, rtarget = self.agent(state)
        self._left += ltarget
        self._right += rtarget
        left = (1 <= self._left)
        right = (1 <= self._right)
        self._left -= left
        self._right -= right
        return left, right


def _constant_agent(left, right, state):
    return (left, right)


def constant_agent(left, right):
    """An agent that always returns the same action."""
    return ft.partial(_constant_agent, left, right)
