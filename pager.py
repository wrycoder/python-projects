import curses
import sys

def pager(stdscr, /, total_pages):
    """Display a multi-page document using a pad and a window"""
    window_height = curses.LINES - 5
    window_width = curses.COLS - 10
    total_chars = window_height * window_width * total_pages
    current_page = 0
    pad = curses.newpad((window_height * total_pages), window_width)
    prompt = curses.newwin(1, window_width, window_height, 0)
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
            if current_page > 0:
                menu_message += '; b: backward'
        else:
            if current_page > 0:
                menu_message += 'b: backward'
        menu_message += '; q: quit'
        half_length_of_message = int(len(menu_message) / 2)
        p_height, p_width = prompt.getmaxyx()
        p_midpoint = int(p_width / 2)
        x_position = p_midpoint - half_length_of_message
        prompt.addstr(0, x_position, menu_message)
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
                if current_page > 0:
                    current_page -= 1
                    pad.refresh((current_page * window_height),0, 5,5,
                                window_height - 1, window_width - 1)
                else:
                    continue
            case 113: # 'q'
                break
            case _:
                continue

if __name__ == "__main__":
    total_pages = 0
    try:
        total_pages = int(sys.argv[1])
    except(IndexError):
        print("Please tell me how many pages of data to generate")
        sys.exit()
    curses.wrapper(pager, total_pages)

