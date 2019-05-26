from __future__ import annotations

import collections

import Box2D as B
import numpy as np

from . import render


State = collections.namedtuple('State', ('x', 'y', 'a', 'dx', 'dy', 'da'))


class Game:
    def __init__(self, seed=None):
        self.timestep = 0.01
        self.thrust = 15
        self.hwidth = 0.4
        self.hheight = 2
        self.random = np.random.RandomState(seed)  # pylint: disable=no-member
        self.elapsed = 0

        self.world = B.b2World(gravity=(0, -10))
        self.ground = self.world.CreateStaticBody(
            position=[0, -10],
            shapes=B.b2PolygonShape(box=(50, 10)),
        )
        self.rocket = self.world.CreateDynamicBody(
            position=[0, 15],
            angle=1.0 * (self.random.rand()-0.5)
        )
        self.control = (False, False)
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
    def convert_body(body, color, extra_shapes=()):
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
        ground = self.convert_body(self.ground, 'black')
        rocket = self.convert_body(
            self.rocket, 'blue',
            ((self.left_thruster_shape,) if self.control[0] else ()) +
            ((self.right_thruster_shape,) if self.control[1] else ()))
        return render.draw(
            render.Scene(bounds=(-30, 30, -1, 29),
                         width=800,
                         bodies=(ground, rocket)))

    def _repr_html_(self):
        return self.draw()

    def step(self, thrust_left, thrust_right):
        self.control = (thrust_left, thrust_right)
        thrust_v = self.rocket.GetWorldVector([0, self.rocket.mass * self.thrust])
        if thrust_left:
            self.rocket.ApplyForce(thrust_v, self.rocket.GetWorldPoint([-self.hwidth, -self.hheight]), True)
        if thrust_right:
            self.rocket.ApplyForce(thrust_v, self.rocket.GetWorldPoint([self.hwidth, -self.hheight]), True)
        self.world.Step(self.timestep, 5, 5)
        self.elapsed += self.timestep

    @property
    def state(self):
        """Returns the State tuple, that describes the rocket."""
        position = self.rocket.position
        angle = self.rocket.angle
        dposition = self.rocket.linearVelocity
        dangle = self.rocket.angularVelocity
        return State(position.x, position.y, angle, dposition.x, dposition.y, dangle)


def in_bounds(state):
    return abs(state.x) < 20 and 4 <= state.y < 25 and abs(state.a) < 1.5


def single_game_lifetime(agent, max_time):
    game = Game()
    max_steps = int(np.ceil(max_time / game.timestep))
    for step in range(max_steps):
        state = game.state
        if not in_bounds(state):
            return step * game.timestep
        game.step(*agent(state))
    return max_steps * game.timestep


class IntegratorController:
    """Turn a continuous controller agent into a PWM discrete agent (suitable for the game)."""
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


def constant_agent(left, right):
    return lambda state: (left, right)
