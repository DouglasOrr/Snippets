# Evaluate some RPS strategies

import collections
import itertools as it
import numpy as np

class Strategy(collections.namedtuple("Strategy", ["r", "p", "s"])):
    __slots__ = ()
    def __str__(self):
        return "(R %.3f, P %.3f, S %.3f)" % (self.r, self.p, self.s)

def expected_win(theirs, mine):
    """Compute the expected win rate of my strategy given theirs"""
    assert abs(theirs.r + theirs.p + theirs.s - 1) < 0.001
    assert abs(mine.r + mine.p + mine.s - 1) < 0.001
    wins = theirs.r * mine.p + theirs.p * mine.s + theirs.s * mine.r
    losses = theirs.r * mine.s + theirs.p * mine.r + theirs.s * mine.p
    return wins - losses

def differentially_stable(theirs, mine, delta = 1E-2, epsilon = 1E-8):
    """Step a small amount each side of a supposed optimum - is it differentially stable, w.r.t. my strategy."""
    e_mine = expected_win(theirs, mine)
    for d in it.permutations((-delta, 0, delta)):
        test = Strategy(*(x+y for x,y in zip(mine, d)))
        e_test = expected_win(theirs, test)
        if e_mine + epsilon < e_test:
            return False
    return True

def all_strategies_grid(n):
    """Sample from the space of all possible strategies."""
    rs, step = np.linspace(0, 1, n, retstep=True)
    for r in rs:
        for p in np.arange(0, 1.00000001-r, step):
            s = 1 - r - p
            yield Strategy(r, p, s)

def handicap(strategy, handicap_strategy = Strategy(1, 0, 0), handicap_prob = 0.5):
    """Handicap a strategy, by mixing it with another with a given probability."""
    p_s = 1 - handicap_prob
    p_h = handicap_prob
    return Strategy(p_s * strategy.r + p_h * handicap_strategy.r,
                    p_s * strategy.p + p_h * handicap_strategy.p,
                    p_s * strategy.s + p_h * handicap_strategy.s)

def find_best_strategy(theirs, my_grid):
    """Do a grid search for the best strategy, given their strategy."""
    return max(my_grid, key = lambda mine: expected_win(theirs, mine))

def find_minimax_strategy(their_grid = all_strategies_grid(11), my_grid = all_strategies_grid(11)):
    """Find the strategy that makes our result best, assuming they know what we're going to play."""
    their_strategies = list(their_grid)
    return max(((find_best_strategy(mine, their_strategies), mine) for mine in my_grid),
               key = lambda p: expected_win(p[0], p[1]))

### Script

ngrid = 31
theirs_best, mine_best = find_minimax_strategy(
    my_grid = all_strategies_grid(ngrid),
    their_grid = map(handicap, all_strategies_grid(ngrid)),
)
print("If I 'move' first, and they have the handicap:")
print("   me: %s -> them: %s -> %.3f" % (mine_best, theirs_best, expected_win(theirs_best, mine_best)))

theirs_best, mine_best = find_minimax_strategy(
    my_grid = map(handicap, all_strategies_grid(ngrid)),
    their_grid = all_strategies_grid(ngrid),
)
print("If I 'move' first, and I have the handicap:")
print("   me: %s -> them: %s -> %.3f" % (mine_best, theirs_best, expected_win(theirs_best, mine_best)))
