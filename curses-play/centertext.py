# Draw text at center of screen
import curses
import sys

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print("Please include the message to display")
        sys.exit()

screen = curses.initscr()
num_rows, num_cols = screen.getmaxyx()

# Make a function to print a line in the center of screen
def print_center(message):
    # Calculate center row
    middle_row = int(num_rows / 2)

    # Calculate center column, and then adust starting position based
    # on the length of the message
    half_length_of_message = len(message) // 2
    middle_column = num_cols // 2
    x_position = middle_column - half_length_of_message

    # Draw the text
    screen.addstr(middle_row, x_position, message)
    screen.refresh()

print_center(sys.argv[1])

# Wait and cleanup
curses.napms(3000)
curses.endwin()

