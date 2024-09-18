import unittest
from paginator import PaginatorException, load_data, paginate
import curses
import re

class TestPaginator(unittest.TestCase):

    def test_load_data(self):
        try:
            stdscr = curses.initscr()
            self.assertRaises(
                PaginatorException, 
                load_data,
                stdscr
            )
            error_message = "Dude you messed up"
            err_re = re.compile(error_message)
            stdscr.clear()
            stdscr.refresh()
            self.assertRaisesRegex(
                PaginatorException,
                err_re,
                load_data,
                stdscr,
                error_message
            )
        finally:
            curses.endwin()

if __name__ == '__main__':
    unittest.main()
