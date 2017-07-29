'''Core game logic. Everything you need to run a game (except for players).
'''

from mbtai.autoslots import slots
import numpy as np


def v2(x, y):
    return np.array((x, y), dtype=np.float32)


class Angle:
    NORTH = 0.0
    EAST = 0.5 * np.pi
    WEST = -0.5 * np.pi
    SOUTH = np.pi

    @staticmethod
    def unit(angle):
        '''A unit vector at 'angle'.
        '''
        return v2(np.sin(angle), np.cos(angle))


# Immutable game components - these are referentially transparent, as they
# are not modified after being loaded.

@slots(
    'max_hp',
    'advance_speed',
    'reverse_speed',
    'traverse_speed',
    'turret_traverse_speed',
    'gun_max_ammo',
    'gun_damage',
    'gun_reload_time',
)
class TankSpec:
    pass


# State objects - represent the current (mutable) state of objects in the game

@slots(
    ('advance', 'float[-1, 1], ratio max speed forward(+1)/reverse(-1).'),
    ('traverse', 'float[-1, 1], ratio max traverse speed cw(+1)/ccw(-1).'),
    ('turret_traverse', 'float[-1, 1], as `traverse`, but for turret.'),
    ('fire', 'boolean, fire if possible?'),
)
class TankCommand:
    '''The movement and firing instruction for a single tank.
    '''
    @staticmethod
    def none():
        return TankCommand(advance=0, traverse=0, turret_traverse=0,
                           fire=False)

    def clip(self):
        '''Clip the command to the allowed ranges.
        '''
        self.advance = np.clip(self.advance, -1, 1)
        self.traverse = np.clip(self.traverse, -1, 1)
        self.turret_traverse = np.clip(self.turret_traverse, -1, 1)
        self.fire = bool(self.fire)


@slots(
    'dt',
    ('projectiles',
     'a list of projectile launches, processed after objects have been updated',
     lambda: []),
)
class StateUpdate:
    '''A mutable object that provides metadata needed for updating the game
    by one tick.
    '''
    pass


@slots(
    'position',
    'angle',
    'turret_angle',
    'ammo',
    'hp',
    ('reload', "counts down to zero, then we're ready to fire"),
)
class TankState:
    @property
    def abs_turret_angle(self):
        return self.turret_angle + self.angle


@slots(
    'spec',
    'state',
    'command',
)
class Tank:
    @staticmethod
    def create(tank_spec, position, angle,
               turret_angle=0, ammo=None, hp=None, reload=0):
        '''Create a tank from a spec - using default values where appropriate
        (e.g. max. ammo, max. hp, turret pointing forwards).
        '''
        state = TankState(
            position=position,
            angle=angle,
            turret_angle=turret_angle,
            ammo=(ammo if ammo is not None else tank_spec.gun_max_ammo),
            hp=(hp if hp is not None else tank_spec.max_hp),
            reload=reload,
        )
        return Tank(spec=tank_spec, state=state, command=TankCommand.none())

    def update(self, state_update):
        # make sure the command doesn't break any rules
        self.command.clip()

        # advance/reverse
        if 0 < self.command.advance:
            speed = self.command.advance * self.spec.advance_speed
        else:
            speed = self.command.advance * self.spec.reverse_speed
        velocity = speed * Angle.unit(self.state.angle)
        self.state.position += state_update.dt * velocity

        # traverse left/right
        traverse_speed = self.command.traverse * self.spec.traverse_speed
        self.state.angle += state_update.dt * traverse_speed

        # turret traverse left/right
        turret_traverse_speed = \
            self.command.turret_traverse * self.spec.turret_traverse_speed
        self.state.turret_angle += state_update.dt * turret_traverse_speed
