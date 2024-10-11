#
# Notes about the War and Peace Reader
#
# This work in progress is a customized reader for Leo Tolstoy's novel War and
# Peace.
#
# The application includes a workaround for what appears to be a bug in
# curses.newpad(). That function is supposed to return a pad object, which
# can then be used for scrolling up and down in the text.
#
# Unfortunately, when I call newpad() with an array containing the entire
# text (over 66000 lines), it returns NULL. After some testing, the maximum
# size of the input array appears to be somewhere under 35000 or 40000 lines.
#
# To address that shortcoming, I create a hash containing the fifteen separate
# books, and two epilogues, in Tolstoy's text.

import paginator
from curses import wrapper
import curses, sys, re


SOURCE_FILENAME = 'war-and-peace.txt'
MIN_DISPLAY_HEIGHT = 20
MIN_DISPLAY_WIDTH = 80
TEXT_STYLE = 1
TITLE_STYLE = 2
MENU_STYLE = 3
TITLE_STRING = "Leo Tolstoy's WAR AND PEACE"

toc = []
books = {}

class ScreenSetupError(Exception):
    pass

def do_setup():
    '''Initialize the system.'''
    result = 0
    book_re = re.compile(r'^\s{4}BOOK.+')
    epilogue_re = re.compile(r'^\s{4}(FIRST|SECOND) EPILOGUE')
    with open(SOURCE_FILENAME) as txt:
        for line in txt.readlines():
            if(book_re.match(line)):
                toc.append(line)
            elif(epilogue_re.match(line)):
                toc.append(line)
    if(len(toc) != 17):
        raise Exception(
            'Table of contents did not load correctly. ' +\
            f'The novel has 17 books, but your app has {len(toc)}.'
        )
    for b in range(1, 18):
        books[b] = []
    book_re = re.compile(r'^BOOK\s.+')
    epilogue_re = re.compile('^FIRST EPILOGUE')
    book_begin, book_end = 0, 0
    current_line = 0
    with open(SOURCE_FILENAME) as txt:
        bookmarks = []
        lines = txt.readlines()
        # Bookmark the beginning of each chapter
        for i in range(0, len(lines)):
            if(book_re.match(lines[i])):
                bookmarks.append(i)
        for i in range(0, len(lines)):
            if(epilogue_re.match(lines[i])):
                bookmarks.append(i)
                epilogue_re = re.compile('^SECOND EPILOGUE')
                for j in range(0, len(lines)):
                    if(epilogue_re.match(lines[j])):
                        result = j
                        bookmarks.append(j)
        for b in range(1, 18):
            current_line = bookmarks[b-1]
            for i in range(current_line, (bookmarks[b] - 1)):
                books[b].append(lines[i])
        for i in range(bookmarks[16], len(lines)):
            books[b].append(lines[i])
    return result

def main_window(stdscr):
    text = None
    screen_height, screen_width = stdscr.getmaxyx()
    curses.start_color()
    curses.init_pair(TITLE_STYLE, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(MENU_STYLE, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(TEXT_STYLE, curses.COLOR_WHITE, curses.COLOR_BLACK)
    if (screen_height < MIN_DISPLAY_HEIGHT):
        stdscr.addstr(
            "ERROR: Your terminal needs to have at least " + \
            f"{MIN_DISPLAY_HEIGHT} lines."
        )
        stdscr.refresh()
        curses.napms(3000)
        raise ScreenSetupError()
    if (screen_width < MIN_DISPLAY_WIDTH):
        stdscr.addstr(
            "ERROR: Your terminal needs to have at least " + \
            f"{MIN_DISPLAY_WIDTH} columns."
        )
        stdscr.refresh()
        curses.napms(3000)
        raise ScreenSetupError()
    default_prompt = "Choose a chapter by number " \
                     "(include leading zeroes). Press 'ESC' to quit..."
    curses.set_escdelay(2)
    p = paginator.Paginator()
    paging_window = curses.newwin(screen_height - 2, screen_width - 1)
    prompt_bar = curses.newwin(1, screen_width - 1, screen_height - 2, 0)
    result = 0
    while(True):
        stdscr.addstr(0,
            (screen_width // 2) - (len(TITLE_STRING) // 2),
            TITLE_STRING,
            curses.A_BOLD | curses.color_pair(TITLE_STYLE)
        )
        y_index = 1
        for key in books.keys():
            title = f"{key:02}.{toc[key-1]}"
            stdscr.addstr(
                y_index,
                (screen_width // 2) - (len(title) // 2),
                title,
                curses.color_pair(TITLE_STYLE)
            )
            y_index +=1

        prompt_bar.addstr(
            0,
            (screen_width // 2) - (len(default_prompt) // 2),
            default_prompt,
            curses.color_pair(TITLE_STYLE)
        )
        stdscr.refresh()
        prompt_bar.refresh()
        curses.curs_set(1)
        curses.echo()
        prompt_bar.keypad(True)
        char1 = prompt_bar.getch()
        if(char1 == 27): # ESC key...
            break
        else:
            char1 -= 48
        char2 = prompt_bar.getch() - 48
        try:
            stdscr.clear()
            result = int(f"{char1}{char2}")
            stdscr.refresh()
            p.paginate(paging_window, books[result])
            paging_window.erase()
        except(KeyError, ValueError):
            continue
        stdscr.clear()
        stdscr.refresh()

if __name__ == "__main__":
    do_setup()
    wrapper(main_window)
