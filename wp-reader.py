import paginator
from curses import wrapper
import curses
import sys

def main_window(stdscr):
    text = None
    try:
        book = sys.argv[1]        
    except(IndexError):
        errmsg = "Please specify which book"
        msg_midpoint = len(errmsg) // 2
        height, width = stdscr.getmaxyx()
        stdscr.addstr(
            (height // 2),
            (width // 2) - msg_midpoint,
            errmsg
        )
        stdscr.refresh()
        curses.napms(3000)
        raise PaginatorException(msg=errmsg)
    filename = f'war-and-peace-book-{book}.txt'
    with open(filename) as f:
        text = f.readlines()
    p = paginator.Paginator()
    p.paginate(stdscr, text)

if __name__ == "__main__":
    wrapper(main_window)
