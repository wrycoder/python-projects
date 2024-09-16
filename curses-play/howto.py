import curses
from curses import wrapper
import sys

DEBUG_LIMIT = 5

def more(current_page: int, lines_per_page: int,
    total_pages: int, forward: bool=True):
    """Tell us if there is more data"""
    if forward == True:
        return current_page < total_pages
    else:
        return current_page > 0

def main(stdscr):
    """Display a multi-page document using a pad and a window"""
    window_height = curses.LINES - 5 
    window_width = curses.COLS - 10
    total_pages = DEBUG_LIMIT
    total_chars = window_height * window_width * total_pages
    current_page = 0
    pad = curses.newpad((window_height * total_pages), window_width)
    prompt = curses.newwin(1, 75, window_height, 0)
    # These loops fill the pad with letters
    for y in range(0, ((window_height * total_pages)- 1)):
        for x in range(0, (window_width - 1)):
            pad.addch(y, x, ord('a') + (x*x+y*y) % 26)
    pad.refresh(0,0, 5,5, (window_height - 1), (window_width - 1))
    while True:
        prompt.clear()
        menu_message = ''
        if current_page < total_pages - 1:
            menu_message += 'f: forward'
            if more(current_page, window_height, total_chars, forward=False):
                menu_message += '; b: backward'
        else:
            if more(current_page, window_height, total_chars, forward=False):
                menu_message += 'b: backward'
        menu_message += '; q: quit'
        prompt.addstr(0, 0, menu_message)
        prompt.refresh()
        action = prompt.getch()
        match action:
            case 102: # 'f'
                if current_page < total_pages - 1:
                    current_page += 1
                    pad.refresh((current_page * window_height),0, 5,5,
                                  window_height - 1, window_width - 1)
                else:
                    continue
            case 98: # 'b'
                if more(current_page, window_height, -1, forward=False):
                    current_page -= 1
                    pad.refresh((current_page * window_height),0, 5,5,
                                window_height - 1, window_width - 1)
                else:
                    continue
            case 113: # 'q'
                break
            case _:
                continue

wrapper(main)
