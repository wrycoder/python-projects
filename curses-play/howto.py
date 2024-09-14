import curses
from curses import wrapper
import sys

def main(stdscr):
    if len(sys.argv) != 2:
        raise Exception("Dude you must tell me how many pages to create")
    window_height = curses.LINES - 5 
    window_width = curses.COLS - 10
    more_available = True
    total_pages = int(sys.argv[1])
    pad = curses.newpad((window_height * total_pages), window_width)
    prompt = curses.newwin(1, 75, window_height + 1, 0)
    # These loops fill the pad with letters
    for y in range(0, ((window_height * total_pages)-1)):
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
        if more_available == True:
            prompt.addstr(0, 0, "f: forward; q: quit")
        else:
            prompt.addstr(0, 0, "b: backward; q: quit")
        prompt.refresh()
        action = prompt.getch()
        match action:
            case 102: # 'f'
                if more_available == True:
                    pad.refresh(window_height,0, 5,5, window_height,window_width)
                    prompt.clear()
                    more_available = False
            case 98: # 'b'
                if more_available == False:
                    pad.refresh(0,0, 5,5, window_height,window_width)
                    prompt.clear()
                    more_available = True
            case 113: # 'q'
                break
            case _:
                continue

wrapper(main)
