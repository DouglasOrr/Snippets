import numpy as np
import libpegz


# Utilities

def english_board():
    '''Create a standard English board (mask & pegs).

    returns (mask, start) -- bool(7, 7), bool(7, 7) --
      -- mask -- true if "on-board"
      -- pegs -- true if occupied
    '''
    mask = np.ones((7, 7), dtype=np.bool)
    mask[:2, :2] = False
    mask[:2, -2:] = False
    mask[-2:, :2] = False
    mask[-2:, -2:] = False
    pegs = mask.copy()
    pegs[3, 3] = False
    return mask, pegs


def find_symmetry(a, b):
    '''Find a symmetry that maps a onto b.

    return -- func -- such that func(a) == b
    '''
    return next(
        tx
        for tx in [
            lambda x: x[:, :],
            lambda x: x[::-1, :],
            lambda x: x[:, ::-1],
            lambda x: x[::-1, ::-1],
            lambda x: x.T[:, :],
            lambda x: x.T[::-1, :],
            lambda x: x.T[:, ::-1],
            lambda x: x.T[::-1, ::-1],
        ]
        if (tx(a) == b).all()
    )


def show(mask, state):
    '''Format as a string.'''
    return '\n'.join(
        ' '.join(' ' if not m else ('x' if s else 'o')
                 for m, s in zip(mm, ss))
        for mm, ss in zip(mask, state))


def show_instructions(mask, states):
    '''Yield a sequence of string instructions for a game.
    '''
    yield show(mask, states[0])
    for prev, _next in zip(states[:-1], states[1:]):
        diff = _next.astype(np.int32) - prev.astype(np.int32)
        yield '\n'.join(
            ' '.join(' ' if not m else ('.'
                                        if d == 0 else
                                        ('#' if d < 0 else '+'))
                     for m, d in zip(mm, dd))
            for mm, dd in zip(mask, diff))


def invert(mask, pegs):
    '''Invert a board of pegs.'''
    return ~pegs & mask


def solve(mask, start):
    '''Try to solve the game (finishing in the complement of the starting
    position).

    returns -- generator([state]) -- generator of solutions
    '''
    if start.sum() % 2 != 0:
        raise ValueError('Bidirectional solver does not support non-even'
                         ' starting pieces')

    # Search half of the game tree, with backreferences
    states = [{libpegz.get_symmetric_identifier(start): (start, None)}]
    for _ in range(start.sum() // 2):
        next_states = dict()
        for parent_id, (parent, _) in states[-1].items():
            for child in libpegz.get_moves(mask, parent):
                child_id = libpegz.get_symmetric_identifier(child)
                if child_id not in next_states:
                    next_states[child_id] = (child, parent_id)
        states.append(next_states)

    def backtrace(index, identifier):
        while identifier is not None:
            current, identifier = states[index][identifier]
            yield current
            index -= 1

    # Find states where the inverse has been found in the previous step
    # - as this game is symmetrical (if you reverse time & invert the board,
    #   a legal game remains a legal game), this is an efficient way to brute
    #   force a solution.
    for state_id, (state, _) in states[-1].items():
        inv_id = libpegz.get_symmetric_identifier(invert(mask, state))
        if inv_id in states[-2]:
            forward_trace = list(backtrace(-1, state_id))[::-1]
            backward_trace = list(invert(mask, b)
                                  for b in backtrace(-2, inv_id))
            tx = find_symmetry(backward_trace[0], forward_trace[-1])
            yield forward_trace + list(map(tx, backward_trace[1:]))


if __name__ == '__main__':
    mask, start = english_board()
    solution = next(solve(mask, start))
    for step in show_instructions(mask, solution):
        print(step)
        print()
