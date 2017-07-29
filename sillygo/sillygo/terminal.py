'''A terminal client for sillygo.
'''

from . import game
import sys
import re
import itertools as it


class Turn:
    '''Base class for a player's turn, which may be
    {Move, Pass, Resign}.
    '''
    def __init__(self, player):
        self.player = player


class Move(Turn):
    def __init__(self, player, position):
        super().__init__(player)
        self.position = position


class Pass(Turn):
    def __init__(self, player):
        super().__init__(player)


class Resign(Turn):
    def __init__(self, player):
        super().__init__(player)


class TerminalPlayer:
    MOVE_PATTERN = re.compile('([a-z]+)[^a-z0-9]*([0-9]+)')
    ALPHABET = 'abcdefghijklmnopqrstuvwxyz'

    def __init__(self, player):
        self.player = player

    def __call__(self, board):
        while True:
            sys.stderr.write('Your move (%s):%s\n' % (self.player.name, board))
            line = sys.stdin.readline().strip().lower()
            if line == 'pass':
                return Pass(self.player)
            elif line == 'resign':
                return Resign(self.player)
            else:
                m = self.MOVE_PATTERN.match(line)
                if m is not None:
                    x = self.ALPHABET.index(m.group(1))
                    y = int(m.group(2)) - 1
                    return Move(self.player, (x, y))
                else:
                    sys.stderr.write('Error! unrecognized move "%s", '
                                     'should be something like "C7", '
                                     '"pass" or "resign"\n' % line)


def play_move(board, player):
    while True:
        turn = player(board)
        if isinstance(turn, Resign):
            return board, turn
        if isinstance(turn, Pass):
            return board, turn
        if isinstance(turn, Move):
            result = board.move(player.player, turn.position)
            if isinstance(result, game.Board):
                return result, turn


class Result:
    pass


class PointsResult(Result):
    def __init__(self, black_points, white_points, handicap):
        self.black_points = black_points
        self.white_points = white_points
        self.handicap = handicap

    @property
    def winner(self):
        if self.black_points < self.white_points + self.handicap:
            return game.State.white
        else:
            return game.State.black


class Resignation(Result):
    def __init__(self, resigned_player):
        self.resigned_player = resigned_player

    @property
    def winner(self):
        return self.resigned_player.enemy()


def get_result(board, scoring, handicap):
    territory = board.territory(scoring)
    return PointsResult(territory.score(game.State.black),
                        territory.score(game.State.white),
                        handicap)


def play_game():
    scoring = game.Scoring.area
    handicap = 3.5
    board_size = 9

    board = game.Board.empty(board_size)
    player_black = TerminalPlayer(game.State.black)
    player_white = TerminalPlayer(game.State.white)
    last_pass = False
    for player in it.cycle([player_black, player_white]):
        board, turn = play_move(board, player)
        if isinstance(turn, Pass):
            if last_pass:
                return get_result(board, scoring, handicap)
            last_pass = True
        elif isinstance(turn, Resign):
            return Resignation(player.player)
        else:
            last_pass = False


if __name__ == '__main__':
    play_game()
