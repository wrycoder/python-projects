import curses, sys, re

HORIZONTAL_MARGIN       = 3
VERTICAL_MARGIN         = 3
ERROR_DELAY_TIME        = 2000
DEFAULT_FWD_PROMPT      = "f: forward"
DEFAULT_FWD_CHAR        = 'f'
DEFAULT_BWD_PROMPT      = "b: backward"
DEFAULT_BWD_CHAR        = 'b'
DEFAULT_QUIT_PROMPT     = "q: quit"
DEFAULT_QUIT_CHAR       = 'q'
DEFAULT_MSG             = "Unspecified paginator error"
MISSING_SOURCE_MSG      = "Source document not found"
WRONG_FORMAT_MSG        = "Source document needs to be plain text, "\
                          "with .txt extension"

class PaginatorException(Exception):
    def __init__(self, msg=DEFAULT_MSG):
        super().__init__(msg)

class Paginator:
    def __init__(self, wait_on_error=False, centered=False,
                fwd_prompt=DEFAULT_FWD_PROMPT, fwd_char=DEFAULT_FWD_CHAR,
                bwd_prompt=DEFAULT_BWD_PROMPT, bwd_char=DEFAULT_BWD_CHAR,
                quit_prompt=DEFAULT_QUIT_PROMPT, quit_char=DEFAULT_QUIT_CHAR):
        self.wait_on_error = wait_on_error
        self.centered = centered
        self.fwd_prompt = fwd_prompt
        self.fwd_char = ord(fwd_char)
        self.bwd_prompt = bwd_prompt
        self.bwd_char = ord(bwd_char)
        self.quit_prompt = quit_prompt
        self.quit_char = ord(quit_char)

    def handle_error(self, stdscr, error_message):
        curses.savetty()
        msg_midpoint = len(error_message) // 2
        height, width = stdscr.getmaxyx()
        curses.curs_set(0)
        stdscr.addstr(
            (height // 2),
            (width // 2) - msg_midpoint,
            error_message
        )
        if self.wait_on_error == True:
            wait_msg = '(Press any key to exit)'
            msg_midpoint = len(wait_msg) // 2
            stdscr.addstr(
                (height // 2) + 1,
                (width // 2) - msg_midpoint,
                wait_msg
            )
            stdscr.refresh()
            stdscr.getch()
        else:
            stdscr.refresh()
            curses.napms(ERROR_DELAY_TIME)
        curses.resetty()

    def load_data(self, stdscr, filename):
        text = None
        filename_re = re.compile('\S+\.txt$')
        if filename_re.match(filename) == None:
            self.handle_error(stdscr, WRONG_FORMAT_MSG)
            raise PaginatorException(WRONG_FORMAT_MSG)
        try:
            with open(filename) as f:
                text = f.readlines()
        except FileNotFoundError as fnfx:
            self.handle_error(stdscr, MISSING_SOURCE_MSG)
            raise PaginatorException(MISSING_SOURCE_MSG)
        return text

    def paginate(self, stdscr, /, data):
        """Display a multi-page document using a pad and a window"""
        scr_height, scr_width = stdscr.getmaxyx()
        window_height = scr_height - VERTICAL_MARGIN
        window_width = scr_width - HORIZONTAL_MARGIN
        curses.curs_set(0)
        current_page = 0
        total_pages = len(data) // window_height
        if len(data) % window_height:
            total_pages += 1
        pad = curses.newpad(len(data) + 1, window_width)
        prompt = curses.newwin(1, window_width, window_height, 0)
        y_index = 0
        for line in data:
            if self.centered == True:
                text_midpoint = len(line[:window_width]) // 2
                line_midpoint = window_width // 2
                pad.addstr(y_index,
                    line_midpoint - text_midpoint,
                    line[:window_width]
                )
            else:
                pad.addstr(y_index, 0, line[:window_width])
            y_index += 1
        pad.refresh(0,0, VERTICAL_MARGIN, HORIZONTAL_MARGIN,
                    (window_height - 1), (window_width - 1))
        while True:
            prompt.clear()
            menu_message = ''
            if current_page < total_pages - 1:
                menu_message += self.fwd_prompt
                if current_page > 0:
                    menu_message += '; ' + self.bwd_prompt
            else:
                if current_page > 0:
                    menu_message += self.bwd_prompt
            if total_pages > 1:
                menu_message += '; '
            menu_message += self.quit_prompt
            half_length_of_message = int(len(menu_message) / 2)
            p_height, p_width = prompt.getmaxyx()
            p_midpoint = int(p_width / 2)
            x_position = p_midpoint - half_length_of_message
            prompt.addstr(0, x_position, menu_message)
            prompt.refresh()
            action = prompt.getch()
            match action:
                case self.fwd_char:
                    if current_page < total_pages - 1:
                        current_page += 1
                        if current_page == total_pages - 1:
                            stdscr.erase()
                            stdscr.refresh()
                        pad.refresh(
                            ((current_page * window_height) - VERTICAL_MARGIN),
                            0,
                            0,
                            HORIZONTAL_MARGIN,
                            window_height - 1, window_width - 1
                        )
                    else:
                        continue
                case self.bwd_char:
                    if current_page > 0:
                        current_page -= 1
                        stdscr.erase()
                        stdscr.refresh()
                        pad.refresh(
                            ((current_page * window_height) - VERTICAL_MARGIN),
                            0,
                            VERTICAL_MARGIN,
                            HORIZONTAL_MARGIN,
                            window_height - 1, window_width - 1
                        )
                    else:
                        continue
                case self.quit_char:
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
    p = Paginator(wait_on_error = True)
    curses.wrapper(p.paginate, data)

