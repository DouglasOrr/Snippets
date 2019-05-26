from .. import core


def test_in_bounds():
    assert core.in_bounds(core.State(10, 20, 1.2, None, None, None))
    assert not core.in_bounds(core.State(-30, 20, 1.2, None, None, None))
    assert not core.in_bounds(core.State(10, 1, 1.2, None, None, None))
    assert not core.in_bounds(core.State(10, 20, 1.8, None, None, None))
