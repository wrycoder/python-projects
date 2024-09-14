import curses

def scroll_it(msg, pad, offset):
    pad.clear()
    pad.addstr(msg)
    pad.refresh(0, offset, 5, 5, 15, 20)
    curses.napms(3000)

screen = curses.initscr()
test_message = "This text is thirty characters"

# Make a pad 100 lines tall and 20 chars wide
# Make the pad large enough to fit the contents you want
# You cannot add text larger than the pad
# We are only going to add one line and barely use any of the space
pad = curses.newpad(100, 100)
pad.addstr(test_message)

# Start printing text from (0,2), of the pad (first line, 3rd char)
# on the screen at position (5,5)
# with the maximum portion of the pad displayed being 20 chars x 15 lines
# Since we only have one line, the 15 lines is overkill, but the 20 chars
# will only show 20 characters before cutting off
pad.refresh(0, 2, 5, 5, 15, 20)
curses.napms(3000)

for offset in range(3, 15):
    scroll_it(test_message, pad, offset)

curses.endwin()
