#! /usr/bin/python

import curses
import time
import random

_HEIGHT = 30
_WIDTH = 30

_BASE_TETROMINOS = [
        [
            ' I  ',
            ' I  ',
            ' I  ',
            ' I  ',
        ],
        [
            ' OO ',
            ' OO ',
            '    ',
            '    ',
        ],
        [
            'TTT ',
            ' T  ',
            '    ',
            '    ',
        ],
        [
            ' J  ',
            ' J  ',
            'JJ  ',
            '    ',

        ],
        [
            'L   ',
            'L   ',
            'LL  ',
            '    ',
        ],
        [
            ' SS ',
            'SS  ',
            '    ',
            '    ',
        ],
        [
            'ZZ  ',
            ' ZZ ',
            '    ',
            '    ',
        ],
]


class GameBoard:

    def __init__(self, width, height):
        self._width = width
        self._height = height
        self.current_piece = None
        self.clearBoard()
        assert(type(self._board[0]) == list)

    def clearBoard(self):
        self._board = [list('#' + ' ' * self._width + '#') for i in range(self._height)]
        self._board.append('#' * (self._width + 2))

    def setPiece(self, piece):
        self.current_piece = piece

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
            self.current_piece = None

    def getRenderableBoard(self):
        ret = []
        for i, line in enumerate(self._board):
            if self.current_piece and self.current_piece.y <= i < self.current_piece.y + 4: #i >= self.current_piece.y and i < self.current_piece.y + 4:
                combined_line = list(line)
                for col in range(4):
                    if self.current_piece[i - self.current_piece.y][col] != ' ':
                        combined_line[self.current_piece.x + 1 + col] = self.current_piece[i - self.current_piece.y][col]
                ret.append(''.join(combined_line))
            else:
                ret.append(''.join(line))
        return ret


class GamePiece:

    def __init__(self, piece, start_x, start_y=1):
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
            rotated_piece[j][i] = char
    return rotated_piece


def render(stdscr, game_board):
    lines = game_board.getRenderableBoard()
    for y,line in enumerate(lines):
        stdscr.addstr(y, 0, line)
        #print(line)
    stdscr.refresh()

def gameLoop(stdscr, game_board):
    stdscr.nodelay(True)
    ticks = 0
    speed = 8
    while True:
        time.sleep(0.0625)

        # User input
        ch = stdscr.getch()
        if ch != curses.ERR:
            if ch == ord('q'):
                break
            elif ch == curses.KEY_LEFT:
                #game_board.current_piece.move(-1, 0)
                game_board.movePiece(-1, 0, False)
            elif ch == curses.KEY_RIGHT:
                #game_board.current_piece.move(1, 0)
                game_board.movePiece(1, 0, False)
            elif ch == curses.KEY_DOWN:
                #game_board.current_piece.move(0, 1)
                game_board.movePiece(0, 1, False)
            elif ch == curses.KEY_UP:
                #game_board.current_piece.move(0, 1)
                game_board.movePiece(0, 0, True)

        if ticks % speed == 0:
            # Game logic.
            if not game_board.descend():
                game_board.addPieceToBoard()
                game_board.setPiece(GamePiece(_BASE_TETROMINOS[random.randrange(7)], _WIDTH // 2 - 2))

        # Render
        render(stdscr, game_board)
        ticks += 1


def boundsCheck(value, maxBound, minBound=0):
    return minBound <= value < maxBound


def hasCompletedLines(game_board, start_x):
    pass

outer = None
def main(stdscr):
    stdscr.clear()
    board = GameBoard(30, 30)
    piece = GamePiece(_BASE_TETROMINOS[6], _WIDTH // 2 - 2)
    board.setPiece(piece)
    gameLoop(stdscr, board)
    time.sleep(1)
    global outer
    outer = board

if __name__ == '__main__':
    curses.wrapper(main)
    print(outer.getRenderableBoard())
