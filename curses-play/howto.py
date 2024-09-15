import curses
from curses import wrapper
import sys

def more(current_page: int, lines_per_page: int,
    data_length: int, forward: bool=True):
    total_pages = data_length // lines_per_page
    if forward == True:
        return current_page <= lines_per_page
    else:
        return current_page >= 1

def main(stdscr):
    if len(sys.argv) != 2:
        raise Exception("Dude you must tell me how many pages to create")
    window_height = curses.LINES - 5 
    window_width = curses.COLS - 10
    total_pages = int(sys.argv[1])
    current_page = 1
    pad = curses.newpad((window_height * total_pages), window_width)
    prompt = curses.newwin(1, 75, window_height + 1, 0)
    total_chars = 0
    # These loops fill the pad with letters
    for y in range(0, ((window_height * total_pages)-1)):
        total_chars += 1
        for x in range(0, (window_width - 1)):
            pad.addch(y, x, ord('a') + (x*x+y*y) % 26)
            total_chars += 1
    # Displays a section of the pad in the middle of the screen.
    # (0,0) : coordinate of upper-left corner of pad area to display.
    # (5,5) : coordinate of upper-left corner of window area to be filled
    #         with pad content.
    # (20, 75) : coordinate of lower-right corner of window area to be
    #            filled with pad content
    pad.refresh(0,0, 5,5, window_height,window_width)
    while True:
        prompt.clear()
        menu_message = ''
        if more(current_page, window_height, total_chars):
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
                if more(current_page, window_height, total_chars):
                    current_page += 1
                    pad.refresh(((current_page * window_height)-1),0, 5,5, window_height,window_width)
                    prompt.clear()
                else:
                    continue
            case 98: # 'b'
                if more(current_page, window_height,
                        total_chars, forward=False):
                    if current_page > 1:
                        current_page -= 1
                    pad.refresh(((current_page * window_height)-1),0, 5,5, window_height,window_width)
                    prompt.clear()
                else:
                    continue
            case 113: # 'q'
                break
            case _:
                continue

wrapper(main)
