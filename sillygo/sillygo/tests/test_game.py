from sillygo.game import State, Board, Blocked, Scoring
from nose.tools import eq_
from nose_parameterized import parameterized


def test_state_enemy():
    eq_(State.empty.enemy, State.empty)
    eq_(State.black.enemy, State.white)
    eq_(State.white.enemy, State.black)


def test_text_serialization():
    board = Board.parse('''
    +---------+
    | o x x _ |
    | _ o _ _ |
    | _ _ _ _ |
    +---------+
    ''')
    eq_(board, Board.parse(str(board)))


def check_move(player, position, old_board, new_board):
    '''Check that a move on the given old board results in the new board
    (or an instance of Blocked).
    '''
    if isinstance(old_board, str):
        old_board = Board.parse(old_board)
    if isinstance(new_board, str):
        new_board = Board.parse(new_board)
    moved_board = old_board.move(player, position)
    eq_(moved_board, new_board)
    return moved_board


def test_move_capture():
    # Simple capture of something in the corner
    check_move(State.black, (1, 0), '''
    +---------+
    | o x x _ |
    | _ o _ _ |
    | _ _ _ _ |
    +---------+
    ''', '''
    +---------+
    | _ x x _ |
    | x o _ _ |
    | _ _ _ _ |
    +---------+
    ''')

    # This move is only valid because capture rules apply before
    # 'safety' rules
    check_move(State.white, (0, 2), '''
    +-----------+
    | _ x _ x x |
    | _ _ x o o |
    | _ _ _ _ _ |
    +-----------+
    ''', '''
    +-----------+
    | _ x o _ _ |
    | _ _ x o o |
    | _ _ _ _ _ |
    +-----------+
    ''')

    # Make sure we can capture big groups
    check_move(State.white, (3, 0), '''
    +---------+
    | x x x x |
    | o o x x |
    | _ o o x |
    | _ x x x |
    +---------+
    ''', '''
    +---------+
    | _ _ _ _ |
    | o o _ _ |
    | _ o o _ |
    | o _ _ _ |
    +---------+
    ''')


def test_move_extend():
    # The piece itself has no freedoms, but is part of a free group
    check_move(State.white, (1, 2), '''
    +---------+
    | _ x x x |
    | _ x _ x |
    | _ x o x |
    | _ _ _ _ |
    +---------+
    ''', '''
    +---------+
    | _ x x x |
    | _ x o x |
    | _ x o x |
    | _ _ _ _ |
    +---------+
    ''')


def test_move_suicide():
    # Moving into somewhere with no freedoms
    check_move(State.white, (1, 2), '''
    +---------+
    | _ x x x |
    | _ x _ x |
    | _ x o x |
    | _ _ x _ |
    +---------+
    ''', Blocked.suicide)


@parameterized([(3, 2), (2, 1)])
def test_move_occupied(row, col):
    # Moving into a self-occupied or enemy-occupied square
    check_move(State.white, (row, col), '''
    +---------+
    | _ o o x |
    | _ _ _ x |
    | _ x _ _ |
    | _ _ o _ |
    +---------+
    ''', Blocked.occupied)


@parameterized([(-1, 0), (0, -1), (0, 4), (3, 0)])
def test_move_out_of_bounds(row, col):
    check_move(State.black, (row, col), '''
    +---------+
    | _ _ _ _ |
    | _ _ _ _ |
    | _ _ _ _ |
    +---------+
    ''', Blocked.out_of_bounds)


def test_move_cycle():
    board = Board.empty(5)
    board = board.move(State.black, (0, 1))
    board = board.move(State.white, (0, 2))
    board = board.move(State.white, (0, 4))
    board = board.move(State.black, (1, 2))
    # Scenario - amenable to cycle/Ko
    board = check_move(State.white, (1, 3), board, '''
    +-----------+
    |   x o   o |
    |     x o   |
    |           |
    |           |
    |           |
    +-----------+
    ''')
    # Capture a piece - and introduce a potential cycle/Ko
    board = check_move(State.black, (0, 3), board, '''
    +-----------+
    |   x   x o |
    |     x o   |
    |           |
    |           |
    |           |
    +-----------+
    ''')
    # Cycle not allowed
    check_move(State.white, (0, 2), board, Blocked.cycle)

    board = board.move(State.white, (4, 4))
    board = board.move(State.black, (4, 3))
    # Now the move is allowed (as the board has moved on)
    check_move(State.white, (0, 2), board, '''
    +-----------+
    |   x o   o |
    |     x o   |
    |           |
    |           |
    |       x o |
    +-----------+
    ''')


def test_scoring():
    board = Board.parse(
        '''
        +---------+
        | _ x o _ |
        | x x o _ |
        | x x o o |
        | x _ _ _ |
        +---------+
        '''
    )
    board.prisoners = {State.black: 2}

    by_area = board.territory(Scoring.area)
    # 6 stones, 1 intersection
    eq_(by_area.score(State.black), 7)
    # 4 stones (2 non-scoring enclosed spaces)
    eq_(by_area.score(State.white), 4)

    by_territory = board.territory(Scoring.territory)
    # 1 enclosed space, 2 prisoners
    eq_(by_territory.score(State.black), 3)
    # 2 enclosed spaces
    eq_(by_territory.score(State.white), 2)
