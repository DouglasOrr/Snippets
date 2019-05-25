import hover as H


def test_in_bounds():
    assert H.in_bounds(H.State(10, 20, 1.2, None, None, None))
    assert not H.in_bounds(H.State(-30, 20, 1.2, None, None, None))
    assert not H.in_bounds(H.State(10, 1, 1.2, None, None, None))
    assert not H.in_bounds(H.State(10, 20, 1.8, None, None, None))
