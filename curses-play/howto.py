import curses
from curses import wrapper
import sys

def main(stdscr):
    window_height = curses.LINES - 5 
    window_width = curses.COLS - 10
    is_first_page = True
    pad = curses.newpad((window_height * 2), window_width)
    prompt = curses.newwin(1, 75, window_height + 1, 0)
    # These loops fill the pad with letters
    for y in range(0, ((window_height * 2)-1)):
        for x in range(0, (window_width - 1)):
            pad.addch(y, x, ord('a') + (x*x+y*y) % 26)
    # Displays a section of the pad in the middle of the screen.
    # (0,0) : coordinate of upper-left corner of pad area to display.
    # (5,5) : coordinate of upper-left corner of window area to be filled
    #         with pad content.
    # (20, 75) : coordinate of lower-right corner of window area to be
    #            filled with pad content
    pad.refresh(0,0, 5,5, window_height,window_width)
    while True:
        if is_first_page == True:
            prompt.addstr(0, 0, "f: forward; q: quit")
        else:
            prompt.addstr(0, 0, "b: backward; q: quit")
        prompt.refresh()
        action = prompt.getch()
        match action:
            case 102: # 'f'
                if is_first_page == True:
                    pad.refresh(window_height,0, 5,5, window_height,window_width)
                    prompt.clear()
                    is_first_page = False
            case 98: # 'b'
                if is_first_page == False:
                    pad.refresh(0,0, 5,5, window_height,window_width)
                    prompt.clear()
                    is_first_page = True
            case 113: # 'q'
                break
            case _:
                continue

wrapper(main)
