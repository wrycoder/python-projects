import curses

screen = curses.initscr()
screen.addstr("Press any key...")
screen.refresh()

c = screen.getch()

curses.endwin()

# Convert the key to ASCII and print ordinal value
print(f"You pressed {chr(c)} which is keycode {c}")

