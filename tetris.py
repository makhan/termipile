#! /usr/bin/python

import curses
import time
import random
import collections

_HEIGHT = 20
_WIDTH = 10

_BASE_TETROMINOS = [
        [
            ' I  ',
            ' I  ',
            ' I  ',
            ' I  ',
        ],
        [
            '    ',
            ' OO ',
            ' OO ',
            '    ',
        ],
        [
            '    ',
            ' TTT',
            '  T ',
            '    ',
        ],
        [
            '  J ',
            '  J ',
            ' JJ ',
            '    ',

        ],
        [
            ' L  ',
            ' L  ',
            ' LL ',
            '    ',
        ],
        [
            '    ',
            ' SS ',
            'SS  ',
            '    ',
        ],
        [
            '    ',
            'ZZ  ',
            ' ZZ ',
            '    ',
        ],
]

class RandomGenerator:

    def __init__(self):
        self._bag = collections.deque()
        self._topUpIfNecessary()

    def _topUpIfNecessary(self):
        if len(self._bag) < 2:
            new_values = list(range(7))
            random.shuffle(new_values)
            self._bag.extend(new_values)

    def next(self):
        value = self._bag.popleft()
        self._topUpIfNecessary()
        return value

    def preview(self):
        return self._bag[0]


class GameBoard:

    def __init__(self, width, height):
        self._width = width
        self._height = height
        self.current_piece = None
        self.score = 0
        self.level = 0
        self.lines = 0
        self.clearBoard()
        self.piece_queue = RandomGenerator()
        start_y = 0
        start_piece = _BASE_TETROMINOS[self.piece_queue.next()]
        if start_piece[0] == '    ':
            start_y = -1
        piece = GamePiece(start_piece, _WIDTH // 2 - 2, start_y)
        self.setPiece(piece)

    def clearBoard(self):
        self._board = [list('┃' + ' ' * self._width + '┃') for i in range(self._height)]
        self._board.append('┗' + '━' * self._width + '┛')

    def setPiece(self, piece):
        self.current_piece = piece
        return self._canFit(piece)


    def movePiece(self, dx, dy, rotate):
        # This is not very efficient, but fast enough for tetris.
        new_piece = self.current_piece.copy()
        if rotate:
            new_piece.rotate()
        if dx or dy:
            new_piece.move(dx, dy)
        if self._canFit(new_piece):
            self.current_piece = new_piece

    def descend(self):
        old_piece = self.current_piece
        self.movePiece(0, 1, False)
        return old_piece != self.current_piece


    def _canFit(self, piece):
        ret = True
        for y in range(4):
            for x in range (4):
                if piece[y][x] != ' ':
                    ret = ret and boundsCheck(piece.y + y, _HEIGHT) and boundsCheck(piece.x + x, _WIDTH) and self._board[piece.y + y][piece.x + x + 1] == ' '
        return ret


    def addPieceToBoard(self):
        if self.current_piece:
            for y in range(4):
                for x in range(4):
                    if self.current_piece[y][x] != ' ':
                        self._board[y + self.current_piece.y][x + self.current_piece.x + 1] = self.current_piece[y][x]

    def getRenderableBoard(self):
        ret = []
        for i, line in enumerate(self._board):
            if self.current_piece and self.current_piece.y <= i < self.current_piece.y + 4:
                combined_line = list(line)
                for col in range(4):
                    if self.current_piece[i - self.current_piece.y][col] != ' ':
                        combined_line[self.current_piece.x + 1 + col] = self.current_piece[i - self.current_piece.y][col]
                ret.append(''.join(combined_line))
            else:
                ret.append(''.join(line))
        return ret

    def _isLine(self, row):
        row_data = self._board[row]
        return all(char != ' ' for char in row_data)

    def completeLines(self, start_y):
        return [index for index in range(start_y, min(start_y + 6, _HEIGHT)) if self._isLine(index)]

    def moveRowDown(self, row_index):
        if row_index >= 0:
            self._board[row_index + 1] = self._board[row_index].copy()

    def _deleteRow(self, row_index):
        for i in range(row_index - 1, -1, -1):
            self.moveRowDown(i)

    def deleteRows(self, rows):
        for row_index in sorted(rows):
            self._deleteRow(row_index)
        factors = [0, 40, 100, 300, 1200]
        self.score += factors[len(rows)] * (self.level + 1)
        self.lines += len(rows)


class GamePiece:

    def __init__(self, piece, start_x, start_y=0):
        self._piece = list(piece)
        self.x = start_x
        self.y = start_y

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def __getitem__(self, idx):
        return self._piece[idx]

    def rotate(self):
        # TODO(muntasir): Check if rotation is valid
        self._piece = rotate(self._piece)

    def copy(self):
        return GamePiece(self._piece, self.x, self.y)


# TODO(muntasir): Precompute rotations
def rotate(piece):
    rotated_piece = [[' ' for i in range(4)] for j in range(4)]
    for i, row in enumerate(piece):
        for j, char in enumerate(row):
            rotated_piece[j][3 - i] = char
    return rotated_piece


def renderShape(stdscr, lines, y_offset, x_offset, blank='.'):
    for y,line in enumerate(lines):
        for x, char in enumerate(line):
            index = '0IOTJLSZ'.find(char)
            y_pos, x_pos = y + y_offset, x + x_offset
            if index != -1:
                stdscr.addch(y_pos, x_pos, chr(9606), curses.color_pair(index))
                stdscr.refresh()
            elif char == ' ':
                stdscr.addch(y_pos, x_pos, blank)
            else:
                stdscr.addch(y_pos, x_pos, char)

def render(stdscr, game_board):
    lines = game_board.getRenderableBoard()
    next_piece = GamePiece(_BASE_TETROMINOS[game_board.piece_queue.preview()], 0, 0)
    stdscr.addstr(0, 0, '┏' + '━' *_WIDTH + '┓')
    renderShape(stdscr, lines, 1, 0)
    renderShape(stdscr, next_piece, 4, _WIDTH + 5, blank=' ')
    stdscr.addstr(3, _WIDTH + 5, 'Next:')
    stdscr.addstr(10, _WIDTH + 5, 'score: %d' % game_board.score)
    stdscr.addstr(11, _WIDTH + 5, 'lines: %d' % game_board.lines)
    stdscr.addstr(12, _WIDTH + 5, 'level: %d' % game_board.level)
    stdscr.refresh()


def flushInput(stdscr):
    while True:
        ch = stdscr.getch()
        if ch == curses.ERR:
            break


def gameLoop(stdscr, game_board):
    stdscr.nodelay(True)
    ticks = 0
    speed = 8
    running = True
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLACK)
    while True:
        flushInput(stdscr)
        time.sleep(0.0625)

        # User input
        ch = stdscr.getch()
        if ch != curses.ERR:
            if ch == ord('q'):
                break
            elif ch == curses.KEY_LEFT:
                game_board.movePiece(-1, 0, False)
            elif ch == curses.KEY_RIGHT:
                game_board.movePiece(1, 0, False)
            elif ch == curses.KEY_DOWN:
                game_board.movePiece(0, 1, False)
            elif ch == curses.KEY_UP:
                game_board.movePiece(0, 0, True)

        if ticks % speed == 0 and running:
            # Game logic.
            if not game_board.descend():
                game_board.addPieceToBoard()
                start_y = game_board.current_piece.y - 1
                handleCompletedLines(game_board, start_y)
                if not game_board.setPiece(GamePiece(_BASE_TETROMINOS[game_board.piece_queue.next()], _WIDTH // 2 - 2)):
                   running = False
        # Render
        if running:
            render(stdscr, game_board)
        else:
           stdscr.addstr(_HEIGHT // 2, _WIDTH // 2, "Game Over")
        ticks += 1


def boundsCheck(value, maxBound, minBound=0):
    return minBound <= value < maxBound


def handleCompletedLines(game_board, start_y):
    lines = game_board.completeLines(start_y)
    game_board.deleteRows(lines)

def main(stdscr):
    stdscr.clear()
    board = GameBoard(_WIDTH, _HEIGHT)
    gameLoop(stdscr, board)
    time.sleep(1)

if __name__ == '__main__':
    curses.wrapper(main)
