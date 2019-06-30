import hover_game as G
import numpy as np


def test_state():
    state = G.State(G.State.Outcome.Continue,
                    123,
                    2,
                    np.zeros((5, 8), dtype=np.bool),
                    np.array([1, 2, 3, 4, 5, 6], dtype=np.float32))
    assert 'Continue' in str(state)
    assert '123' in str(state)
    assert '2' in str(state)
    assert '00000000' in str(state)
    assert '[1,2,3,4,5,6]' in str(state)
