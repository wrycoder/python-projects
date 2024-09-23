import paginator
from curses import wrapper
import curses, sys, re

'''Notes about the War and Peace Reader

This work in progress is a customized reader for Leo Tolstoy's novel War and
Peace.

The application includes a workaround for what appears to be a bug in
curses.newpad(). That function is supposed to return a pad object, which
can then be used for scrolling up and down in the text. 

Unfortunately, when I call newpad() with an array containing the entire
text (over 66000 lines), it returns NULL. After some testing, the maximum
size of the input array appears to be somewhere under 35000 or 40000 lines.

To address that shortcoming, I create a hash containing the fifteen separate 
books, and two epilogues, in Tolstoy's text.
'''

SOURCE_FILENAME = 'war-and-peace.txt'
toc = [] 
book_re = re.compile('^\s{4}BOOK.+')
epilogue_re = re.compile('^\s{4}(FIRST|SECOND) EPILOGUE')
books = {}

with open(SOURCE_FILENAME) as txt:
    for line in txt.readlines():
        if(book_re.match(line)):
            toc.append(line)
        elif(epilogue_rematch(line)):
            toc.append(line)
    

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
