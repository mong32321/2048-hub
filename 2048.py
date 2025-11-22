import curses
import random
import sys

board_size = 4

keys = {
    curses.KEY_UP: "up",
    curses.KEY_DOWN: "down",
    curses.KEY_LEFT: "left",
    curses.KEY_RIGHT: "right",
    ord('w'): "up",
    ord('s'): "down",
    ord('a'): "left",
    ord('d'): "right",
    ord('q'): "quit",
    27: "quit"
}


class Game:
    def __init__(self, size=board_size):
        self.size = size
        self.score = 0
        self.best = 0
        self.board = []
        self.reset()

    def reset(self):
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.score = 0
        self._spawn()
        self._spawn()

    def _spawn(self):
        empty_cells = []
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == 0:
                    empty_cells.append((r, c))

        if not empty_cells:
            return

        r, c = random.choice(empty_cells)
        if random.random() < 0.1:
            self.board[r][c] = 4
        else:
            self.board[r][c] = 2

    def _slide_row(self, row):
        tiles = [x for x in row if x != 0]
        new_row = []
        gained = 0
        skip = False

        for i in range(len(tiles)):
            if skip:
                skip = False
                continue

            if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
                value = tiles[i] * 2
                new_row.append(value)
                gained += value
                skip = True
            else:
                new_row.append(tiles[i])

        while len(new_row) < self.size:
            new_row.append(0)

        return new_row, gained

    def move_left(self):
        changed = False
        total_gain = 0
        updated = []

        for row in self.board:
            new_row, gain = self._slide_row(row)
            if new_row != row:
                changed = True
            total_gain += gain
            updated.append(new_row)

        if changed:
            self.board = updated
            self.score += total_gain
            if self.score > self.best:
                self.best = self.score
            self._spawn()

    def move_right(self):
        for i in range(self.size):
            self.board[i].reverse()
        self.move_left()
        for i in range(self.size):
            self.board[i].reverse()

    def move_up(self):
        self._transpose()
        self.move_left()
        self._transpose()

    def move_down(self):
        self._transpose()
        self.move_right()
        self._transpose()

    def _transpose(self):
        t = []
        for c in range(self.size):
            row = []
            for r in range(self.size):
                row.append(self.board[r][c])
            t.append(row)
        self.board = t

    def can_move(self):
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == 0:
                    return True

        for r in range(self.size):
            for c in range(self.size):
                v = self.board[r][c]
                if r + 1 < self.size and self.board[r + 1][c] == v:
                    return True
                if c + 1 < self.size and self.board[r][c + 1] == v:
                    return True

        return False

    def max_tile(self):
        m = 0
        for row in self.board:
            for v in row:
                if v > m:
                    m = v
        return m


def setup_colors():
    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_WHITE, -1)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)
    curses.init_pair(3, curses.COLOR_CYAN, -1)
    curses.init_pair(4, curses.COLOR_GREEN, -1)
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)
    curses.init_pair(6, curses.COLOR_RED, -1)


def style_for_value(value):
    if value == 0:
        return curses.A_DIM

    if value == 2:
        pid = 1
    elif value == 4:
        pid = 2
    elif value == 8:
        pid = 3
    elif value == 16:
        pid = 4
    elif value == 32:
        pid = 5
    elif value == 64:
        pid = 6
    else:
        pid = 2

    return curses.color_pair(pid) | curses.A_BOLD


def draw(win, game):
    win.clear()
    h, w = win.getmaxyx()

    title = "2048 terminal"
    line = "-" * len(title)
    x_title = max(0, (w - len(title)) // 2)

    win.addstr(0, x_title, title)
    win.addstr(1, x_title, line)

    info = f"score {game.score} | best {game.best} | max {game.max_tile()}"
    win.addstr(3, max(0, (w - len(info)) // 2), info)

    controls = "arrows / wasd = move | q = quit | r = restart"
    win.addstr(h - 2, max(0, (w - len(controls)) // 2), controls, curses.A_DIM)

    cell_w = 6
    top_y = 5
    left_x = (w - (cell_w * game.size)) // 2

    for r in range(game.size):
        for c in range(game.size):
            v = game.board[r][c]
            text = "." if v == 0 else str(v)
            s = text.center(cell_w - 1)

            y = top_y + r * 2
            x = left_x + c * cell_w

            win.addstr(y, x, s, style_for_value(v))

    win.refresh()


def draw_game_over(win, game):
    h, w = win.getmaxyx()
    msg1 = "no more moves"
    msg2 = f"final score {game.score}, max tile {game.max_tile()}"
    msg3 = "press r to play again or q to quit"

    win.addstr(h // 2 - 1, max(0, (w - len(msg1)) // 2), msg1, curses.A_BOLD)
    win.addstr(h // 2, max(0, (w - len(msg2)) // 2), msg2)
    win.addstr(h // 2 + 1, max(0, (w - len(msg3)) // 2), msg3)
    win.refresh()


def main(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    stdscr.nodelay(False)
    setup_colors()

    game = Game()

    while True:
        draw(stdscr, game)

        if not game.can_move():
            draw_game_over(stdscr, game)
            k = stdscr.getch()
            if k in (ord('r'), ord('R')):
                game.reset()
                continue
            if keys.get(k) == "quit" or k in (ord('q'), ord('Q')):
                break
            else:
                continue

        k = stdscr.getch()
        action = keys.get(k)

        if action is None:
            continue

        if action == "quit":
            break
        elif action == "up":
            game.move_up()
        elif action == "down":
            game.move_down()
        elif action == "left":
            game.move_left()
        elif action == "right":
            game.move_right()


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        sys.exit(0)
