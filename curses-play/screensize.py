import curses

screen = curses.initscr()
num_rows, num_cols = screen.getmaxyx()
curses.endwin()

print(f"Rows:    {num_rows:>4}")
print(f"Columns: {num_cols:>4}")

