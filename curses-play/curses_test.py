import curses

def main(stdscr):
    stdscr.clear()

    # This raises ZeroDivisionError when i == 10.
    for i in range(0, 8):
        v = i-10
        stdscr.addstr(i, 0, '10 divided by {} is {}'.format(v, 10/v))

    stdscr.refresh()
    stdscr.getkey()

stdscr = curses.initscr()

curses.wrapper(main(stdscr))


