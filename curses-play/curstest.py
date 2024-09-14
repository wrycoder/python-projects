import curses 

screen = curses.initscr()

# update the buffer, adding text at different locations
screen.addstr(0, 0, "This string gets printed at position (0, 0)")
screen.addstr(3, 1, "Try Russian text: Привет")
screen.addstr(4, 4, "X")
screen.addch(5, 5, "Y")

# Changes go into the screen buffer and only get
# displayed after calling 'refresh()' to update
screen.refresh()

curses.napms(3000)
curses.endwin()

