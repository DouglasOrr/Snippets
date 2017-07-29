'''Basic strict go game logic.
'''
import enum
import re
import numpy as np
import itertools as it


@enum.unique
class State(enum.Enum):
    empty = 0
    black = 1
    white = 2

    @property
    def enemy(self):
        'Return the enemy of this player (for empty, return self).'
        if self is State.black:
            return State.white
        elif self is State.white:
            return State.black
        else:
            return State.empty


@enum.unique
class Blocked(enum.Enum):
    out_of_bounds = 0
    occupied = 1
    suicide = 2
    cycle = 3


@enum.unique
class Scoring(enum.Enum):
    territory = 0
    area = 1


class TerritoryMap:
    '''The result of finding out the territory (therefore point score) of a player.

    `prisoners[State.black]` -- the number of white prisoners held by black
    '''
    def __init__(self, scoring, points_map, prisoners={}):
        self.scoring = scoring
        self.points_map = points_map
        self.prisoners = prisoners

    def score(self, player):
        '''Return the score for the given player.
        '''
        return (self.points_map == player.value).sum() + \
            self.prisoners.get(player, 0)


class Text:
    '''A few basic display utilities for human-readable text-based
    board displays (reading and writing, primarily for testing.
    '''
    @staticmethod
    def value_to_ch(x):
        if x == State.black.value:
            return 'x'
        elif x == State.white.value:
            return 'o'
        else:
            return ' '

    @staticmethod
    def ch_to_value(ch):
        if ch == 'x':
            return State.black.value
        elif ch == 'o':
            return State.white.value
        else:
            return State.empty.value

    @staticmethod
    def dump(board):
        content = '\n'.join('| %s |' %
                            (' '.join(Text.value_to_ch(s) for s in row))
                            for row in board)
        separator = '+%s+' % ('-' * (2 * board.shape[1] + 1))
        return '\n'.join([separator, content, separator])

    @staticmethod
    def load(text):
        def parse_line(line):
            return [Text.ch_to_value(ch)
                    for ch in it.islice(line, None, None, 2)]
        return np.array([parse_line(m.group(1))
                         for m in re.finditer(r'\| (.+?) \|', text)])


class Board:
    '''The main game logic - boards can accept moves to create new boards,
    and report any problems with the move.
    '''
    def __init__(self, board, prisoners):
        self.board = board
        self.prisoners = prisoners
        # cycle_pair may become (last_stone, last_capture) if a cycle (or Ko)
        # is possible
        self._cycle_pair = None

    @staticmethod
    def empty(board_size=19):
        return Board(np.full((board_size, board_size),
                             State.empty.value,
                             np.int8), {})

    def copy(self):
        return Board(self.board.copy(), self.prisoners.copy())

    @staticmethod
    def parse(text):
        '''Parse a board from its' string representation (mainly intended for
        tests). Note that this cannot recover state for the cycle/Ko rule, or
        keep a faithful territory/Japanese score.
        '''
        return Board(Text.load(text), {})

    def __repr__(self):
        '''Dump a human-friendly representation of the board to a string.
        Such a representation is also machine-parsable by 'parse'.
        '''
        return '\n' + Text.dump(self.board)

    def __eq__(self, other):
        '''Are two boards in the same state (ignoring the 'cycling' state.)
        '''
        return isinstance(other, Board) and (self.board == other.board).all()

    def neighbours(self, position):
        '''Iterate over neighbouring positions to 'position'.
        '''
        x, y = position
        if 0 < x:
            yield (x-1, y)
        if 0 < y:
            yield (x, y-1)
        if x < self.board.shape[0] - 1:
            yield (x+1, y)
        if y < self.board.shape[1] - 1:
            yield (x, y+1)

    def group(self, position):
        '''Iterate over the set of members of a group, starting at 'position'.
        (Note that this also works for empty space).
        '''
        player = self.board[position]
        queue = [position]
        group = set([position])
        while 0 < len(queue):
            parent = queue.pop()
            yield parent
            for child in self.neighbours(parent):
                if self.board[child] == player and child not in group:
                    queue.append(child)
                    group.add(child)

    def liberties(self, position, count_up_to=np.inf):
        '''Count the liberties (empty neighbours) of a group that covers 'position'.
        If the state at 'position' is empty, returns 0.
        '''
        if self.board[position] == State.empty.value:
            return 0
        liberties = 0
        for member in self.group(position):
            for child in self.neighbours(member):
                if self.board[child] == State.empty.value:
                    liberties += 1
                    if count_up_to <= liberties:
                        return liberties
        return liberties

    def move(self, player, position):
        '''Return a new board with the move completed, or else a Blocked
        instance describing why the move is invalid.
        '''
        # Basic checks - in range, non-empty
        if not (0 <= position[0] and position[0] < self.board.shape[0] and
                0 <= position[1] and position[1] < self.board.shape[1]):
            return Blocked.out_of_bounds
        if self.board[position] != State.empty.value:
            return Blocked.occupied

        # Try out the move
        candidate = self.copy()
        candidate.board[position] = player.value

        # Process captures
        enemy = player.enemy
        capture_count = 0
        first_capture = None
        for neighbour in self.neighbours(position):
            if self.board[neighbour] == enemy.value and \
               not candidate.liberties(neighbour, 1):
                for child in candidate.group(neighbour):
                    candidate.board[child] = State.empty.value
                    capture_count += 1
                    if first_capture is None:
                        first_capture = child

        # Track prisoners (for territory scoring)
        candidate.prisoners[player] = \
            candidate.prisoners.get(player, 0) + capture_count

        # Check for a cycle
        if capture_count == 1:
            if (first_capture, position) == self._cycle_pair:
                return Blocked.cycle
            candidate._cycle_pair = (position, first_capture)

        # Check for my own liberty
        if candidate.liberties(position, 1) == 0:
            return Blocked.suicide

        # Success - return the new board state
        return candidate

    @property
    def positions(self):
        return ((row, col)
                for row in range(0, self.board.shape[0])
                for col in range(0, self.board.shape[1]))

    def remove_dead(self):
        # TODO: remove 'dead' stones / stones that cannot live
        return self.copy()

    def get_area_map(self):
        '''Returns a map of stones already on the board, and intersections
        surrounded by one player.
        '''
        points = self.board.copy()
        for position in self.positions:
            if self.board[position] == State.empty.value:
                if all(self.board[n] == State.black.value
                       for n in self.neighbours(position)):
                    points[position] = State.black.value
                elif all(self.board[n] == State.white.value
                         for n in self.neighbours(position)):
                    points[position] = State.white.value
        return points

    def get_territory_map(self):
        '''Returns a map of empty intersections that are surrounded by just
        one player.
        '''
        points = np.full(self.board.shape, State.empty.value, np.int8)
        visited = set([])
        for position in self.positions:
            if self.board[position] == State.empty.value and \
               position not in visited:
                # Add enclosed empty 'groups'
                group = set(self.group(position))
                visited |= group
                borders_black = False
                borders_white = False
                for child in group:
                    for n in self.neighbours(child):
                        if self.board[n] == State.black.value:
                            borders_black = True
                        elif self.board[n] == State.white.value:
                            borders_white = True
                if borders_black != borders_white:
                    for child in group:
                        points[child] = (State.black
                                         if borders_black
                                         else State.white).value
        return points

    def territory(self, scoring):
        '''Determine the territory for each player, given the current board.
        Returns a TerritoryMap containing the result.
        '''
        final = self.remove_dead()

        if scoring is Scoring.area:
            return TerritoryMap(scoring, final.get_area_map(), {})
        else:
            return TerritoryMap(scoring, final.get_territory_map(),
                                final.prisoners.copy())
