import functools as ft
import hover_game as G
import numpy as np
import pytest


def test_state():
    state = G.State(outcome=G.State.Outcome.Continue,
                    progress=.75,
                    data=np.arange(15, dtype=np.float32))
    assert 'Continue' in str(state)
    assert '.75' in str(state)
    assert '[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]' in str(state)


def _state_eq(left, right):
    return (left.outcome == right.outcome
            and np.allclose(left.progress, right.progress)
            and np.allclose(left.data, right.data))


def test_runner():
    for control in [(False, False), (False, True), (True, False), (True, True)]:
        # runner_1a & runner_1b should always be the same
        # runner_2 should always be different
        runner_1a = G.Runner(seed=100, difficulty=[1])
        runner_1b = G.Runner(seed=100, difficulty=[1])
        runner_2 = G.Runner(seed=200, difficulty=[1])

        assert runner_1a.state().outcome == G.State.Outcome.Continue

        # Initial properties
        old_state_1a = runner_1a.state()
        assert _state_eq(old_state_1a, runner_1a.state())
        assert _state_eq(runner_1a.state(), runner_1b.state())
        assert runner_1a.to_svg() == runner_1b.to_svg()
        assert runner_1a._repr_html_() == runner_1a.to_svg()
        assert not _state_eq(runner_1a.state(), runner_2.state())
        assert runner_1a.to_svg() != runner_2.to_svg()

        for n in range(1000):
            runner_1a.step(control)
            runner_1b.step(control)
            runner_2.step(control)

            # Same state runners should stay the same
            if runner_1a.state().outcome == G.State.Outcome.Continue:
                assert not _state_eq(old_state_1a, runner_1a.state())
                assert _state_eq(runner_1a.state(), runner_1b.state())
                old_state_1a = runner_1a.state()
            assert not _state_eq(runner_1a.state(), runner_2.state())

    assert runner_1a.state().outcome != G.State.Outcome.Continue
    assert runner_2.state().outcome != G.State.Outcome.Continue


def constant_agent(left, right, state):
    """An agent that doesn't do anything."""
    return [left, right]


def pd_landing_agent(state):
    """A hand-tuned agent for winning the 'easy game'"""
    a = state.data[G.State.SHIP_A]
    da = state.data[G.State.SHIP_DA]
    c_right = -(a + .5 * da)
    if .2 < np.abs(c_right):
        return [c_right < 0, 0 < c_right]
    if 8 < -state.data[G.State.SHIP_DY]:
        return [True, True]
    return [False, False]


@pytest.mark.parametrize('agent,min_win_rate,max_win_rate',
                         [(ft.partial(constant_agent, left, right), 0.0, 0.01)
                          for left in [False, True]
                          for right in [False, True]]
                         + [(pd_landing_agent, 0.95, 1.0)])
def test_runner_easy(agent, min_win_rate, max_win_rate):
    runs = 100
    successes = 0
    for seed in range(runs):
        runner = G.Runner(seed=seed, difficulty=[1])
        while True:
            state = runner.state()
            if state.outcome != G.State.Outcome.Continue:
                successes += (state.outcome == G.State.Outcome.Success)
                break
            runner.step(agent(state))
    assert min_win_rate <= successes / runs <= max_win_rate
