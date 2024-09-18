import curses
import sys

HORIZONTAL_MARGIN = 3
VERTICAL_MARGIN = 3

def paginate(stdscr, /, data):
    """Display a multi-page document using a pad and a window"""
    window_height = curses.LINES - VERTICAL_MARGIN
    window_width = curses.COLS - HORIZONTAL_MARGIN
    curses.curs_set(0)
    current_page = 0
    total_pages = len(data) // window_height
    pad = curses.newpad(len(data) + 1, window_width)
    prompt = curses.newwin(1, window_width, window_height, 0)
    for line in data:
        pad.addstr(line[:window_width])
    pad.refresh(0,0, VERTICAL_MARGIN, HORIZONTAL_MARGIN,
                (window_height - 1), (window_width - 1))
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
                    pad.refresh((current_page * window_height),0,
                                 VERTICAL_MARGIN, HORIZONTAL_MARGIN,
                                  window_height - 1, window_width - 1)
                else:
                    continue
            case 98: # 'b'
                if current_page > 0:
                    current_page -= 1
                    pad.refresh((current_page * window_height),0,
                                VERTICAL_MARGIN, HORIZONTAL_MARGIN,
                                window_height - 1, window_width - 1)
                else:
                    continue
            case 113: # 'q'
                break
            case _:
                continue
    curses.curs_set(1)

if __name__ == "__main__":
    total_pages = 0
    try:
        total_lines = int(sys.argv[1])
    except(IndexError):
        print("Please tell me how many lines of data to generate")
        sys.exit()
    data = []
    line_length = 500
    # These loops fill the array with letters
    for y in range(0, total_lines):
        data.append('')
        for x in range(0, (line_length - 1)):
            data[y] += chr(ord('a') + (x*x+y*y) % 26)
    curses.wrapper(pager, data)

