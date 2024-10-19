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
PAGINATION_DONE_MSG     = "User finished paging"

TITLE_STYLE             = 1
MENU_STYLE              = 2
TEXT_STYLE              = 3

CENTERED                = 10
LEFT_ALIGNED            = 11
RIGHT_ALIGNED           = 12

def show_text(text, y_index, x_width, scr_object, *, alignment=CENTERED,
              left_padding=None, color=0, mode=curses.A_NORMAL) -> None:
    """
    Center the text horizontally, at the specified vertical position (y_index)

    Parameters:
        text:       the text to be displayed
        y_index:    vertical line in display
        x_width:    length of each line in display
        scr_object: display object
        alignment:  position of text within line
        color:      curses constant specifying a color
        mode:       curses constant specifying font style
    """
    x_index = 0
    padding_width = (x_width // 7)
    attrs = curses.color_pair(color) | mode
    try:
        if alignment == CENTERED:
            fmtstring = "{:^" + str(x_width) + "s}"
            scr_object.addstr(  y_index, x_index,
                                fmtstring.format(text)[:x_width],
                                attrs)
        elif alignment == LEFT_ALIGNED:
            if left_padding != None:
                padding_width = left_padding
            fmtstring = "{:" + str(padding_width) + "s}"
            scr_object.addstr(  y_index, x_index,
                                fmtstring.format(' ') + text[:x_width],
                                attrs)
        else:
            fmtstring = "{:>" + str(padding_width) + "s}"
            scr_object.addstr(  y_index, x_index,
                                fmtstring.format(text)[:x_width],
                                attrs)
    except curses.error:
        # The size of the display (scr_object) is unknown outside this module.
        # It's a potentially hazardous situation, because
        # curses needs to advance the cursor position as it prints.
        # We'll just assume that our data will fit.
        pass

class SeparatorMarker:
    def __init__(self, *, color=0, mode=curses.A_NORMAL):
        self.color = color
        self.mode = mode

def draw_separator(y_index, length, width, scr_object, *, color=MENU_STYLE, mode=curses.A_NORMAL) -> None:
    """
    Draw a centered, separating line, usually between elements of a list

    Parameters:
        y_index:    vertical line in display
        length:     number of characters to draw
        width:      horizontal length of line
        scr_object: display object
        color:      curses constant specifying a color
        mode:       curses constant specifying a style
    """
    starting_point = (width // 2) - (length // 2)
    for i in range(starting_point, starting_point + length):
        scr_object.addch(y_index, i, curses.ACS_HLINE,
                         curses.color_pair(color) | mode)

class PaginatorException(Exception):
    def __init__(self, msg=DEFAULT_MSG):
        super().__init__(msg)

class Paginator:
    """
    Creates a virtual display window for text that is longer than a single
    screen

    Parameters:
        fwd_prompt:         tells user how to advance to next page
        fwd_char:           character that says user wants next page
        bwd_prompt:         tells user how to go back to previous page
        bwd_char:           character that says user wants previous page
        quit_prompt:        tells user how to exit
        quit_char:          character that says user wants to exit
        prompt_color:       default prompt color
        prompt_mode:        default prompt style
    """
    def __init__(self, wait_on_error=False, centered=False,
                fwd_prompt=DEFAULT_FWD_PROMPT, fwd_char=DEFAULT_FWD_CHAR,
                bwd_prompt=DEFAULT_BWD_PROMPT, bwd_char=DEFAULT_BWD_CHAR,
                quit_prompt=DEFAULT_QUIT_PROMPT, quit_char=DEFAULT_QUIT_CHAR,
                prompt_color=0, prompt_mode=curses.A_NORMAL):
        self.wait_on_error = wait_on_error
        self.centered = centered
        self.fwd_prompt = fwd_prompt
        self.fwd_char = ord(fwd_char)
        self.bwd_prompt = bwd_prompt
        self.bwd_char = ord(bwd_char)
        self.quit_prompt = quit_prompt
        self.quit_char = ord(quit_char)
        self.prompt_color = prompt_color
        self.prompt_mode = prompt_mode
        self.left_padding = 0

    def handle_error(self, stdscr, error_message):
        """
        Display an error message, and (optionally) wait for a response
        from the user

        Parameters:
            stdscr:         display object
            error_message:  the message to display
        """
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
        """
        Import the text to be displayed

        Parameters:
            stdscr:         display object
            filename:       name of the file containing the text
        """
        text = None
        filename_re = re.compile(r'\S+\.txt$')
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

    def paginate(self, scr_obj, /, data):
        """
        Display a multi-page document using a pad and a window

        Parameters:
            scr_obj:        display object
            data:           iterable container of text to be displayed
        """
        scr_height, scr_width = scr_obj.getmaxyx()
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
            if line.__class__.__name__ == "SeparatorMarker":
                draw_separator(y_index, (window_width // 5) , window_width, pad,
                                color=line.color, mode=line.mode)
            else:
                if self.centered == True:
                    text_midpoint = len(line[:window_width]) // 2
                    line_midpoint = window_width // 2
                    pad.addstr(y_index,
                        line_midpoint - text_midpoint,
                        line[:window_width]
                    )
                else:
                    pad.addstr(y_index, self.left_padding, line[:window_width])
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
            prompt.addstr(0, x_position, menu_message,
                          curses.color_pair(self.prompt_color) | self.prompt_mode)
            prompt.refresh()
            action = prompt.getch()
            match action:
                case self.fwd_char:
                    if current_page < total_pages - 1:
                        current_page += 1
                        if current_page == total_pages - 1:
                            scr_obj.erase()
                            scr_obj.refresh()
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
                        scr_obj.erase()
                        scr_obj.refresh()
                        current_page -= 1
                        pad.refresh(
                            (current_page * window_height),
                            0,
                            VERTICAL_MARGIN,
                            HORIZONTAL_MARGIN,
                            window_height - 1, window_width - 1
                        )
                    else:
                        continue
                case self.quit_char:
                    raise PaginatorException(PAGINATION_DONE_MSG)
                case _:
                    continue
        curses.curs_set(1)

