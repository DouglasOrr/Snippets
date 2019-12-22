import argparse
import collections
import heapq
import io
import itertools as it
import re
import subprocess

import numpy as np
import pytest


################################################################################
# The game

EMPTY = ' '
WILDCARD = '*'
CHARACTERS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
BOARD_SIZE = 15
N_TILES = 7


def _multiplier_from_pattern(pattern):
    """Use a pattern to create the symmetric score multipliers."""
    pattern = pattern.strip('\n')
    multipliers = np.zeros((BOARD_SIZE, BOARD_SIZE), np.int)
    n = BOARD_SIZE // 2
    multipliers[:n+1, :n+1] = [
        [int(cell) for cell in row.split(' ')]
        for row in pattern.split('\n')]
    multipliers[n+1:] = multipliers[n-1::-1]
    multipliers[:, n+1:] = multipliers[:, n-1::-1]
    return multipliers


class Classic:
    BINGO_SCORE = 50

    POINTS = {
        'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1, 'J': 8,
        'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1, 'P': 3, 'Q': 10, 'R': 1, 'S': 1, 'T': 1,
        'U': 1, 'V': 4, 'W': 4, 'X': 8, 'Y': 4, 'Z': 10, WILDCARD: 0
    }

    WORD_MULTIPLIER = _multiplier_from_pattern("""
3 1 1 1 1 1 1 3
1 2 1 1 1 1 1 1
1 1 2 1 1 1 1 1
1 1 1 2 1 1 1 1
1 1 1 1 2 1 1 1
1 1 1 1 1 1 1 1
1 1 1 1 1 1 1 1
3 1 1 1 1 1 1 2
""")

    LETTER_MULTIPLIER = _multiplier_from_pattern("""
1 1 1 2 1 1 1 1
1 1 1 1 1 3 1 1
1 1 1 1 1 1 2 1
2 1 1 1 1 1 1 2
1 1 1 1 1 1 1 1
1 3 1 1 1 3 1 1
1 1 2 1 1 1 2 1
1 1 1 2 1 1 1 1
""")


class Appy:
    BINGO_SCORE = 35

    POINTS = {
        'A': 1, 'B': 4, 'C': 4, 'D': 2, 'E': 1, 'F': 4, 'G': 3, 'H': 3, 'I': 1, 'J': 10,
        'K': 5, 'L': 2, 'M': 4, 'N': 2, 'O': 1, 'P': 4, 'Q': 10, 'R': 1, 'S': 1, 'T': 1,
        'U': 2, 'V': 5, 'W': 4, 'X': 8, 'Y': 3, 'Z': 10, WILDCARD: 0
    }

    WORD_MULTIPLIER = _multiplier_from_pattern("""
1 1 1 3 1 1 1 1
1 1 1 1 1 2 1 1
1 1 1 1 1 1 1 1
3 1 1 1 1 1 1 2
1 1 1 1 1 1 1 1
1 2 1 1 1 1 1 1
1 1 1 1 1 1 1 1
1 1 1 2 1 1 1 2
""")

    LETTER_MULTIPLIER = _multiplier_from_pattern("""
1 1 1 1 1 1 3 1
1 1 2 1 1 1 1 1
1 2 1 1 2 1 1 1
1 1 1 3 1 1 1 1
1 1 2 1 1 1 2 1
1 1 1 1 1 3 1 1
3 1 1 1 2 1 1 1
1 1 1 1 1 1 1 1
""")


Candidate = collections.namedtuple('Candidate', ('word', 'row', 'col', 'is_horizontal'))


class BestCandidates:
    """Collects the top-scoring results from our search."""
    def __init__(self, nbest):
        self.nbest = nbest
        self._heap = []
        self._best = set([])

    def add(self, candidate, score):
        item = (score, candidate)
        if item in self._best:
            pass
        elif len(self._heap) < self.nbest:
            heapq.heappush(self._heap, item)
            self._best.add(item)
        elif self._heap[0] < item:
            self._best.remove(self._heap[0])
            heapq.heappushpop(self._heap, item)
            self._best.add(item)

    def add_horizontal(self, word, row, col, score):
        self.add(Candidate(word, row, col, is_horizontal=True), score)

    def add_vertical(self, word, row, col, score):
        self.add(Candidate(word, col, row, is_horizontal=False), score)

    def __iter__(self):
        return iter((candidate, score) for score, candidate in sorted(self._heap, reverse=True))


class State:
    """Represents the current state of the board."""
    def __init__(self, tiles, tiles_mask, board, board_mask, wildcard_mask):
        self.tiles = tiles
        self.tiles_mask = tiles_mask
        self.board = board
        self.board_mask = board_mask
        self.wildcard_mask = wildcard_mask

    def __repr__(self):
        def _cell(item_mask):
            item, mask = item_mask
            return f'\u001b[31;1m{item}\u001b[0m' if mask else str(item)

        tiles_repr = (
            '[ ' +
            ' '.join(map(_cell, zip(self.tiles, self.tiles_mask))) +
            ' ]')

        n = 2 * self.board.shape[1] + 1
        board_repr = f'+{"-"*n}+\n' + '\n'.join(
            f'| {" ".join(map(_cell, zip(row, row_mask)))} |'
            for row, row_mask in zip(self.board, self.board_mask)
        ) + f'\n+{"-"*n}+'

        return tiles_repr + '\n' + board_repr

    @classmethod
    def empty(cls, tiles):
        return cls(
            np.array(tiles),
            np.array([False for tile in tiles]),
            np.full((BOARD_SIZE, BOARD_SIZE), EMPTY),
            np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.bool),
            np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.bool))

    _CELL_PATTERN = re.compile(r'^(?P<char>[A-Z])(?P<wildcard>\*)?$')

    @classmethod
    def read_csv(cls, stream):
        rows = iter(line.rstrip('\n').upper().split('\t') for line in stream)
        tiles = np.array([tile for tile in next(rows) if tile])
        board = np.full((BOARD_SIZE, BOARD_SIZE), EMPTY)
        wildcard_mask = np.zeros(board.shape, dtype=np.bool)
        for row, line in enumerate(rows):
            for col, cell in enumerate(line):
                if cell:
                    match = cls._CELL_PATTERN.match(cell)
                    if not match:
                        raise ValueError(f'Could not read cell "{cell}"')
                    board[row, col] = match['char']
                    wildcard_mask[row, col] = (match['wildcard'] is not None)
        return cls(
            tiles, np.zeros(tiles.shape, dtype=np.bool),
            board, np.zeros(board.shape, dtype=np.bool), wildcard_mask)

    @classmethod
    def open_csv(cls, path):
        with open(path, 'r') as f:
            return cls.read_csv(f)

    def transpose(self):
        """Rotate the board 90 degrees left (so vertical is horizontal)."""
        return type(self)(
            self.tiles, self.tiles_mask,
            self.board.T, self.board_mask.T, self.wildcard_mask.T)

    def add_candidate(self, candidate):
        """Return a new board, with candidate marked."""
        tiles = self.tiles.copy()
        board = self.board.copy()
        tiles_mask = np.zeros(tiles.shape, dtype=np.bool)
        board_mask = np.zeros(board.shape, dtype=np.bool)
        wildcard_mask = self.wildcard_mask.copy()
        for ch, ch_row, ch_col in zip(
                candidate.word,
                it.count(candidate.row, not candidate.is_horizontal),
                it.count(candidate.col, candidate.is_horizontal)):

            if board[ch_row, ch_col] == EMPTY:
                board[ch_row, ch_col] = ch
                board_mask[ch_row, ch_col] = True

                # Mark the tile as used
                matching_tiles = ~tiles_mask & (tiles == ch)
                unused_wildcards = ~tiles_mask & (tiles == WILDCARD)
                if matching_tiles.any():
                    tiles_mask[np.where(matching_tiles)[0][0]] = True
                elif unused_wildcards.any():
                    tiles_mask[np.where(unused_wildcards)[0][0]] = True
                    wildcard_mask[ch_row, ch_col] = True
                else:
                    raise ValueError(f"Candidate invalid - cannot find tile for '{ch}'")

            elif ch != board[ch_row, ch_col]:
                raise ValueError(
                    f"Candidate mismatch at ({ch_row}, {ch_col}): expected '{ch}'")

        return type(self)(tiles, tiles_mask, board, board_mask, wildcard_mask)


class Vocab:
    """Vocabulary and indices for efficient searching."""
    def __init__(self, words):
        self.words = words
        self.prefixes = {
            word[:end]
            for word in words
            for end in range(1, len(word)+1)
        }
        self.substrings = {
            word[start:end]
            for word in words
            for start in range(len(word))
            for end in range(start+1, len(word)+1)
        }

    def __repr__(self):
        return (f'Vocab({len(self.words)} words'
                f', {len(self.prefixes)} prefixes'
                f', {len(self.substrings)} substrings)')

    @classmethod
    def read(cls, stream):
        return cls({line.rstrip('\n').upper() for line in stream})

    @classmethod
    def open(cls, path):
        with open(path, 'r') as f:
            return cls.read(f)


################################################################################
# Solver

def get_start_mask(board, row):
    """Returns mask of valid starting indices in the given row"""
    occupied = (board != EMPTY)
    adjacent = np.zeros(board.shape[1], np.bool)
    if not occupied.any():
        # Special case the starting board
        if 2 * row + 1 == board.shape[0]:
            adjacent[board.shape[1] // 2] = True
        return adjacent
    adjacent[1:] |= occupied[row, :-1]
    adjacent[:-1] |= occupied[row, 1:]
    if 1 < row:
        adjacent |= occupied[row-1, :]
    if row < board.shape[0] - 1:
        adjacent |= occupied[row+1, :]
    return adjacent & ~occupied[row, :]


def leading_string(a):
    """Get the string of consecutive tiles at the start of `a`."""
    return ''.join(a[np.cumprod(np.array(a != EMPTY), dtype=np.bool)])


# Note: score does not include the tile being added, may be None (no word formed)
Constraint = collections.namedtuple('Constraint', ('allowed_tiles', 'score'))


def get_vertical_constraint(board, scoring, words, row, col):
    """Return a function that evaluates and scores a tile against a vertical constraint.

    returns -- fn(str) -> (None | int) -- a function that takes a tile
               returns None if the tile cannot be placed here
               otherwise returns the score (not including `tile` for placement)
    """
    pre = leading_string(board[row-1::-1, col])[::-1]
    post = leading_string(board[row+1:, col])
    if (pre, post) == ('', ''):
        return Constraint(CHARACTERS, None)
    return Constraint(
        {tile for tile in CHARACTERS if (pre + tile + post) in words},
        sum(scoring.POINTS[tile] for tile in pre + post))


def tile_options(tile):
    """Return all the options for 'realising' a tile (i.e. handle wildcards)."""
    return CHARACTERS if tile == WILDCARD else (tile,)


def search_row(state, scoring, vocab, row, add_candidate):
    """Main search algorithm - find all given-direction, given-row solutions."""
    # precomputed constants
    start_mask = get_start_mask(state.board, row)
    width = state.board.shape[0]
    constraints = [get_vertical_constraint(state.board, scoring, vocab.words, row, col)
                   for col in range(width)]
    right_runs = [leading_string(state.board[row, col+1:]) for col in range(width)]
    left_runs = [leading_string(state.board[row, col-1::-1])[::-1] for col in range(width)]
    # mutable state
    tiles_used = [False for tile in state.tiles]  # tiles that have been used to get to this state
    word_multiplier = 1  # current accrued wordscore multiplier (could theoretically be >3)
    main_score = 0  # current score for the main (horizontal) word being constructed
    other_score = 0  # accumulated score for any other (vertical) words also constructed

    def _expand(pre, position, post, search_left):
        nonlocal tiles_used, word_multiplier, main_score, other_score

        left_position = position - 1 - len(pre)
        right_position = position + 1 + len(post)
        constraint = constraints[position]
        new_word_multiplier = scoring.WORD_MULTIPLIER[row, position]
        word_multiplier *= new_word_multiplier

        for idx, src_tile in enumerate(state.tiles):
            if not tiles_used[idx]:
                for tile in tile_options(src_tile):
                    candidate = pre + tile + post
                    if candidate in vocab.substrings and tile in constraint.allowed_tiles:
                        tiles_used[idx] = True
                        tile_score = (
                            scoring.LETTER_MULTIPLIER[row, position] * scoring.POINTS[src_tile])
                        main_score += tile_score
                        new_other_score = new_word_multiplier * (
                            0 if constraint.score is None else constraint.score + tile_score)
                        other_score += new_other_score

                        if candidate in vocab.words:
                            add_candidate(
                                candidate, row, position - len(pre),
                                word_multiplier * main_score + other_score +
                                scoring.BINGO_SCORE * (sum(tiles_used) == len(tiles_used)))
                        if candidate in vocab.prefixes and right_position < width:
                            _expand(candidate, right_position, right_runs[right_position],
                                    search_left=False)
                        if search_left and 0 <= left_position and not start_mask[left_position]:
                            _expand(left_runs[left_position], left_position, candidate,
                                    search_left=True)

                        other_score -= new_other_score
                        main_score -= tile_score
                        tiles_used[idx] = False
        word_multiplier //= new_word_multiplier

    for start in np.where(start_mask)[0]:
        _expand(left_runs[start], start, right_runs[start], search_left=True)


def best_words(state, scoring, vocab, nbest):
    """Search for the top scoring moves over the whole board."""
    candidates = BestCandidates(nbest)
    vertical_state = state.transpose()
    for row in range(BOARD_SIZE):
        search_row(state, scoring, vocab, row, candidates.add_horizontal)
        search_row(vertical_state, scoring, vocab, row, candidates.add_vertical)
    return list(candidates)


################################################################################
# Driver program

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Letters-In-A-Row saerch-based solver')
    parser.add_argument('board', help='csv file to read original board from')
    parser.add_argument('dictionary', help='word list file to read allowed dictionary')
    parser.add_argument('-n', '--n-results', type=int, default=3,
                        help='number of suggestions to show')
    parser.add_argument('-s', '--scoring', type=str, default='classic',
                        choices=[cls.__name__.lower() for cls in [Classic, Appy]],
                        help='scoring system to use')
    args = parser.parse_args()
    vocab = Vocab.open(args.dictionary)
    state = State.open_csv(args.board)
    scoring = globals()[args.scoring.capitalize()]
    for candidate, score in best_words(state, scoring, vocab, args.n_results):
        print(f'### {score}: {candidate.word}')
        print(state.add_candidate(candidate))
        print()


################################################################################
# Tests

@pytest.mark.parametrize('cls', [Classic, Appy])
def test_scoring(cls):
    assert not ((cls.LETTER_MULTIPLIER != 1) & (cls.WORD_MULTIPLIER != 1)).any()
    assert len(cls.POINTS) == 27


def test_classic():
    assert (Classic.WORD_MULTIPLIER == 3).sum() == 8
    assert (Classic.WORD_MULTIPLIER == 2).sum() == 17
    assert (Classic.LETTER_MULTIPLIER == 3).sum() == 12
    assert (Classic.LETTER_MULTIPLIER == 2).sum() == 24


def test_appy():
    assert (Appy.WORD_MULTIPLIER == 3).sum() == 8
    assert (Appy.WORD_MULTIPLIER == 2).sum() == 13
    assert (Appy.LETTER_MULTIPLIER == 3).sum() == 16
    assert (Appy.LETTER_MULTIPLIER == 2).sum() == 24


def test_best_candidates():
    best = BestCandidates(2)
    assert list(best) == []
    best.add('x', 10)
    assert list(best) == [('x', 10)]
    best.add('x', 10)
    assert list(best) == [('x', 10)]
    best.add('y', 5)
    assert list(best) == [('x', 10), ('y', 5)]
    best.add('z', 6)
    assert list(best) == [('x', 10), ('z', 6)]


def test_board_show():
    state = State.empty(['G', 'P'])
    head, *rows = repr(state).split('\n')
    assert head == '[ G P ]'
    assert len(rows) == 15 + 2
    assert re.match(r'\+-{31}\+', rows[0])
    assert rows[-1] == rows[0]
    assert all(re.match(r'| {31}|', row) for row in rows[1:-1])


def _nonzero_coordinates(a):
    return set(zip(*np.where(a)))


def test_state_read_csv():
    csv = """H\tA\tG

\t\tO\tH\t
\tI*\tF
"""
    state = State.read_csv(io.StringIO(csv))
    np.testing.assert_array_equal(state.tiles, ['H', 'A', 'G'])
    assert {(row, col, state.board[row, col])
            for row, col in _nonzero_coordinates(state.board != EMPTY)} == {
                    (1, 2, 'O'),
                    (1, 3, 'H'),
                    (2, 1, 'I'),
                    (2, 2, 'F')}
    assert _nonzero_coordinates(state.wildcard_mask) == {(2, 1)}


TEST_BOARD = State.read_csv(io.StringIO("""A\t*\tI\tG\tQ\tK\tR





\t\t\t\t\t\t\t\tL
\t\t\t\t\t\t\t\tO
\t\t\t\t\t\t\tZ\tO\tO
\t\t\t\t\t\t\t\t\tS
\t\t\t\t\t\t\t\t\tT
\t\t\t\t\t\t\t\t\tR\tE\tA\tL
\t\t\t\t\t\t\t\t\tI
\t\t\t\t\t\t\t\t\tC
\t\t\t\t\t\t\t\t\tH*
"""))


def test_board_add_candidate():
    kazoo = TEST_BOARD.add_candidate(Candidate('KAZOO', 7, 5, is_horizontal=True))
    # don't use wildcard unless you have to
    assert _nonzero_coordinates(kazoo.wildcard_mask) == {(13, 9)}
    assert set(kazoo.tiles[~kazoo.tiles_mask]) == {'*', 'I', 'G', 'Q', 'R'}

    # vertical
    TEST_BOARD.add_candidate(Candidate('LIAR', 10, 12, is_horizontal=False))

    with pytest.raises(ValueError):  # try to replace existing tile Z => R
        TEST_BOARD.add_candidate(Candidate('GROO', 7, 6, is_horizontal=True))


def test_board_add_candidate_wildcards():
    # use wildcard when required (missing 'B')
    bazoo = TEST_BOARD.add_candidate(Candidate('BAZOO', 7, 5, is_horizontal=True))
    assert _nonzero_coordinates(bazoo.wildcard_mask) == {(13, 9), (7, 5)}
    assert set(bazoo.tiles[~bazoo.tiles_mask]) == {'I', 'G', 'Q', 'K', 'R'}

    with pytest.raises(ValueError):  # try to use '*' twice
        TEST_BOARD.add_candidate(Candidate('BAAZOO', 7, 4, is_horizontal=True))


def test_vocab():
    dictionary = """one
two
three
thrace"""
    vocab = Vocab.read(io.StringIO(dictionary))
    assert '4 words' in repr(vocab)
    for w in ['ONE', 'TWO', 'THREE', 'THRACE']:
        assert w in vocab.words
        assert w in vocab.prefixes
        assert w in vocab.substrings

    assert 'ON' not in vocab.words
    assert 'ON' in vocab.prefixes
    assert 'ON' in vocab.substrings

    assert 'HRA' not in vocab.words
    assert 'HRA' not in vocab.prefixes
    assert 'HRA' in vocab.substrings

    assert 'T' in vocab.substrings
    assert 'T' in vocab.prefixes
    assert 'WO' in vocab.substrings


@pytest.mark.parametrize('sample,classic,appy', [
    ('blank_0', ('SEVEN', 18), ('SEVEN', 40)),
    ('constraint_0', ('ONE', 7), ('ONE', 8)),
    ('bingo_0', ('SEVENTEEN', 90), ('SEVENTEEN', 67)),
    ('general_0', ('SIX', 18), ('SIXTEEN', 30)),
])
def test_samples(sample, classic, appy):
    state = State.open_csv(f'sample/{sample}.csv')
    vocab = Vocab.open('sample/numbers.txt')
    for scoring, (top_word, top_score) in [(Classic, classic), (Appy, appy)]:
        results = best_words(state, scoring, vocab, 1)
        assert results[0][0].word == top_word
        assert results[0][1] == top_score


def test_command_line():
    sample = 'general_0'
    classic = ('SIX', 18)
    appy = ('SIXTEEN', 30)

    headings = re.compile(r'### (?P<score>\d+): (?P<word>[A-Z]+)')

    output = subprocess.check_output([
        'python', __file__, f'sample/{sample}.csv', 'sample/numbers.txt'
    ]).decode()
    match = headings.search(output)
    assert match is not None and (match['word'], int(match['score'])) == classic

    output = subprocess.check_output([
        'python', __file__, f'sample/{sample}.csv', 'sample/numbers.txt',
        '-n', '5', '-s', 'appy',
    ]).decode()
    match = headings.search(output)
    assert match is not None and (match['word'], int(match['score'])) == appy
    assert len(headings.findall(output)) == 5
