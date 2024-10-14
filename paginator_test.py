import unittest
from paginator import Paginator, PaginatorException
import paginator, curses, re, os

class TestPaginator(unittest.TestCase):

    def test_arg_handling(self):
        p = Paginator()
        try:
            stdscr = curses.initscr()
            self.assertRaises(
                PaginatorException,
                p.load_data,
                stdscr,
                'ptest.txt'
            )
            err_re = re.compile(paginator.MISSING_SOURCE_MSG)
            self.assertRaisesRegex(
                PaginatorException,
                err_re,
                p.load_data,
                stdscr,
                'ptest.txt'
            )
        finally:
            curses.endwin()

    def test_input_format_errors(self):
        p = Paginator(True)
        try:
            stdscr = curses.initscr()
            err_re = re.compile(paginator.WRONG_FORMAT_MSG)
            self.assertRaisesRegex(
                PaginatorException,
                err_re,
                p.load_data,
                stdscr,
                'foo.bar'
            )
        finally:
            curses.endwin()

    def test_data_loading(self):
        p = Paginator(True)
        data = []
        line_length = 500
        total_lines = 500
        filename = 'paginator-test-output.txt'
        for y in range(0, total_lines):
            data.append('')
            for x in range(0, (line_length - 1)):
                data[y] += chr(ord('a') + (x*x+y*y) % 26)
            data[y] += '\n'
        with open(filename, 'w') as ofile:
            ofile.writelines(data)
        try:
            stdscr = curses.initscr()
            result = p.load_data(stdscr, filename)
            self.assertIsInstance(result, list)
            self.assertIn(data[3], result)
        finally:
            curses.endwin()
            os.remove(filename)

    def test_two_pages(self):
        p = Paginator()
        data = []
        try:
            stdscr = curses.initscr()
            screen_lines, screen_columns = stdscr.getmaxyx()
            # The pad height should be 1.5 times the current screen height
            pad_lines = screen_lines + (screen_lines // 2)
            for y in range(0, pad_lines):
                data.append('')
                for x in range(0, (screen_columns - 1)):
                    data[y] += chr(ord('a') + (x*x+y*y) % 26)
                data[y] += '\n'
            p.paginate(stdscr, data)
            self.assertTrue(len(data) == pad_lines)
        finally:
            curses.endwin()


if __name__ == '__main__':
    unittest.main()
