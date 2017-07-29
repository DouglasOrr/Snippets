from .. import game
from mbtai.game import v2
import numpy as np
from numpy.testing import assert_array_equal
from nose.tools import eq_


def test_movement():
    spec = game.TankSpec(
        max_hp=1000,
        advance_speed=8,
        reverse_speed=3,
        traverse_speed=1.2,
        turret_traverse_speed=1.5,
        gun_max_ammo=10,
        gun_damage=40,
        gun_reload_time=4,
    )

    # Heading North (+Y)
    a = game.Tank.create(spec, v2(5, 9), 0)

    # no command => no movement
    assert_array_equal(a.state.position, v2(5, 9))
    a.update(game.StateUpdate(dt=0.01))
    assert_array_equal(a.state.position, v2(5, 9))

    # change the command => forward movement
    a.command.advance = 0.9
    a.update(game.StateUpdate(dt=0.01))
    assert_array_equal(a.state.position, v2(5, 9 + 0.01 * 8 * 0.9))
    eq_(a.state.angle, 0)

    # rotate to face east (clockwise)
    a.command = game.TankCommand.none()
    a.command.traverse = 0.6
    time_quarter_turn = (0.5 * np.pi) / (0.6 * spec.traverse_speed)
    a.update(game.StateUpdate(dt=time_quarter_turn))
    eq_(a.state.angle, game.Angle.EAST)
    eq_(a.state.abs_turret_angle, game.Angle.EAST)

    # rotate turret to face north
    a.command = game.TankCommand.none()
    a.command.turret_traverse = -0.6
    time_quarter_turn = (0.5 * np.pi) / (0.6 * spec.turret_traverse_speed)
    a.update(game.StateUpdate(dt=time_quarter_turn))
    eq_(a.state.angle, game.Angle.EAST)
    eq_(a.state.abs_turret_angle, game.Angle.NORTH)
