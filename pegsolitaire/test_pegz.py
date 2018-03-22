import numpy as np
import libpegz
import pegz


# Refernce implementations

def _get_symmetric_identifier(mask, pegs):
    n = 2 ** np.arange(mask.size).reshape(mask.shape)
    return min(
        (pegs * n[:, :]).sum(),
        (pegs * n[::-1, :]).sum(),
        (pegs * n[:, ::-1]).sum(),
        (pegs * n[::-1, ::-1]).sum(),
        (pegs * n.T[:, :]).sum(),
        (pegs * n.T[::-1, :]).sum(),
        (pegs * n.T[:, ::-1]).sum(),
        (pegs * n.T[::-1, ::-1]).sum(),
    )


def _moves(mask, pegs):
    N = mask.shape[0]
    for i in range(N):
        for j in range(N):
            if pegs[i, j]:
                if (i+2 < N and mask[i+2, j]
                        and pegs[i+1, j] and not pegs[i+2, j]):
                    a = pegs.copy()
                    a[i, j] = False
                    a[i+1, j] = False
                    a[i+2, j] = True
                    yield a
                if (0 <= i-2 and mask[i-2, j]
                        and pegs[i-1, j] and not pegs[i-2, j]):
                    a = pegs.copy()
                    a[i, j] = False
                    a[i-1, j] = False
                    a[i-2, j] = True
                    yield a
                if (j+2 < N and mask[i, j+2]
                        and pegs[i, j+1] and not pegs[i, j+2]):
                    a = pegs.copy()
                    a[i, j] = False
                    a[i, j+1] = False
                    a[i, j+2] = True
                    yield a
                if (0 <= j-2 and mask[i, j-2]
                        and pegs[i, j-1] and not pegs[i, j-2]):
                    a = pegs.copy()
                    a[i, j] = False
                    a[i, j-1] = False
                    a[i, j-2] = True
                    yield a


# Helpers

def _random_pegs(mask, random):
    return mask & (0.5 <= random.rand(*mask.shape))


def _symmetries(state):
    return (
        base[yslice, xslice]
        for base in [state, state.T]
        for xslice in [slice(None), slice(None, None, -1)]
        for yslice in [slice(None), slice(None, None, -1)]
    )


def _examples():
    mask, start = pegz.english_board()
    random = np.random.RandomState(42)
    return mask, [start] + [_random_pegs(mask, random)
                            for _ in range(9)]


# Tests

def test_libpegz_get_symmetric_identifier():
    mask, examples = _examples()
    for state in examples:
        _id = libpegz.get_symmetric_identifier(state)
        assert _id == _get_symmetric_identifier(mask, state)
        for symmetry in _symmetries(state):
            assert _id == libpegz.get_symmetric_identifier(symmetry)


def test_libpegz_moves():
    mask, examples = _examples()
    for state in examples:
        moves = [libpegz.get_symmetric_identifier(move)
                 for move in libpegz.get_moves(mask, state)]
        baseline_moves = [_get_symmetric_identifier(mask, move)
                          for move in _moves(mask, state)]
        assert set(moves) == set(baseline_moves)


def test_english_board():
    mask, start = pegz.english_board()
    assert mask.sum() == 33
    assert start.sum() == 32
    for symmetry in _symmetries(start):
        np.testing.assert_equal(symmetry, start)


def test_find_symmetry():
    mask, examples = _examples()
    for state in examples:
        for symmetry in _symmetries(state):
            tx = pegz.find_symmetry(state, symmetry)
            np.testing.assert_equal(tx(state), symmetry)


def test_invert():
    mask, examples = _examples()
    for state in examples:
        inv = pegz.invert(mask, state)
        assert inv.sum() == mask.sum() - state.sum()
        np.testing.assert_equal(pegz.invert(mask, inv), state)
