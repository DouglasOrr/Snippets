"""Simple hand-tuned example agents."""

import numpy as np
import hover_game as G


def constant_agent(left, right):
    """An agent that doesn't do anything."""
    return lambda state: [left, right]


def pd_landing_agent(state):
    """A hand-tuned agent for simply landing the rocket"""
    a = state.data[G.State.SHIP_A]
    da = state.data[G.State.SHIP_DA]
    c_right = -(a + .5 * da)
    if .2 < np.abs(c_right):
        return [c_right < 0, 0 < c_right]
    if 8 < -state.data[G.State.SHIP_DY]:
        return [True, True]
    return [False, False]
