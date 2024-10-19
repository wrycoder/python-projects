import sys, curses
from .flashcards import Deck, do_loop

try:
    with open(sys.argv[1]) as sourcefile:
        cards = Deck(sourcefile.read())
except(IndexError):
    print("ERROR: please specify a source file for the data")
    quit()
except(Exception) as cfg_ex:
    print(f"Error in source file: {str(cfg_ex)}")
    quit()

curses.wrapper(do_loop, cards)
