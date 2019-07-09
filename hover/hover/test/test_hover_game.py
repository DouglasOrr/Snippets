import hover_game as G
import numpy as np


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
        runner_1a = G.Runner(G.Runner.Settings(seed=100, difficulty=[1]))
        runner_1b = G.Runner(G.Runner.Settings(seed=100, difficulty=[1]))
        runner_2 = G.Runner(G.Runner.Settings(seed=200, difficulty=[1]))

        assert runner_1a.state().outcome == G.State.Outcome.Continue

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

            if runner_1a.state().outcome == G.State.Outcome.Continue:
                assert not _state_eq(old_state_1a, runner_1a.state())
                assert _state_eq(runner_1a.state(), runner_1b.state())
                old_state_1a = runner_1a.state()
            assert not _state_eq(runner_1a.state(), runner_2.state())

    assert runner_1a.state().outcome != G.State.Outcome.Continue
    assert runner_2.state().outcome != G.State.Outcome.Continue
