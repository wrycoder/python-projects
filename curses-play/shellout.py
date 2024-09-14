import curses
import subprocess
import os

# Create a screen and print hello
screen = curses.initscr()
screen.addstr("Hello! Dropping you into a command prompt...\n")
print("Program initialized...")
screen.refresh()
curses.napms(2000)

# Hide the screen, show original terminal, restore cursor position
curses.endwin()

screen.clear()
# Update screen in background
screen.addstr("Welcome back")

print("About to open command prompt...")
curses.napms(2000)

if os.name == 'nt':
    shell = 'cmd.exe'
else:
    shell = 'sh'
subprocess.run(shell)

# when the subprocess ends, return to our screen,
# also restoring cursor position
screen.refresh()
curses.napms(2000)

# Finally go back to the terminal for real
curses.endwin()
