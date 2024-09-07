import fileinput
import curses

prompt = """
To select a president by ordinal number, enter 'o'
To select a president by year, enter 'y'
To select a president by state, enter 's'
To list all presidents in a given party, enter 'p'
To quit, enter 'q'
"""

presidents = {}

states = { 'AL': 'Alabama',
    'AK': 'Alaska',
    'AZ': 'Arizona',
    'AR': 'Arkansas',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DC': 'The District of Columbia',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'ME': 'Maine',
    'MD': 'Maryland',
    'MA': 'Massachusetts',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NE': 'Nebraska',
    'NV': 'Nevada',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NY': 'New York',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'OK': 'Oklahoma',
    'OH': 'Ohio',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VT': 'Vermont',
    'VA': 'Virginia',
    'WA': 'Washington',
    'WV': 'West Virginia',
    'WI': 'Wisconsin',
    'WY': 'Wyoming'
    }

presidential_states = {}

for state in states.keys():
    presidential_states[state] = []

def center(text, y_index, x_width, stdscr) -> None:
    """Center the text"""
    x_index = 0
    fmtstring = "{:^" + str(x_width) + "s}"
    stdscr.addstr(y_index, x_index, fmtstring.format(text))

def ordinal(n: int) -> str:
    """Convert a cardinal number to an ordinal."""
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix

def pronoun(p_string, p_case) -> str:
    """Find appropriate pronoun for a given case"""
    cases = ['subject', 'object', 'possessive']
    pronouns = p_string.split('/')
    p_table = dict(zip(cases, pronouns))
    return p_table[p_case]

class President:
    """A President of the United States.

    Properties of a president include the name, the year of inauguration,
    the state of residence at the time of inauguration, the preferred
    pronouns, party affiliation, and the key (which is simply the ordinal
    number of a given president in the historical record).
    """
    def __init__(self, key: str, name: str, year: str,
                 state: str, pronouns: str, party: str):
        self.key = int(key)
        self.name = name
        self.sworn_in = int(year)
        self.state = states[state]
        self.pronouns = pronouns
        self.party = party

    def display(self, y_index, x_width, stdscr) -> None:
        """Show the president's details."""
        message = f"{self.name}, {ordinal(self.key)} president of the United " + \
                  f"States, was inaugurated in {str(self.sworn_in)}."
        center(message, y_index, x_width, stdscr)
        y_index += 1
        message = f"{pronoun(self.pronouns, 'subject').capitalize()} was a resident of " + \
                  f"{self.state} on Inauguration Day."
        center(message, y_index, x_width, stdscr)
        y_index += 1
        if self.party != 'None':
            message = f"{pronoun(self.pronouns, 'subject').capitalize()} was a member of the " + \
                      f"{self.party} Party."
        else:
            message = f"{pronoun(self.pronouns, 'subject').capitalize()} was not affiliated with any " + \
                        "political party."
        center(message, y_index, x_width, stdscr)

def for_year(year: int) -> President:
    """Find out who was president in the given year."""
    y = int(year)
    if (y < 1789) | (y > 2024):
        raise ValueError('Invalid year')
    for i in presidents.keys():
        if presidents[i].sworn_in > y:
            target_key = int(i) - 1
            return presidents[str(target_key)]

def choose_party(y_index, x_width, stdscr) -> str:
    """Enable user to choose a party from a menu."""
    parties = {}
    menu_option = 1
    for president in presidents.values():
        if president.party not in parties.values():
            parties[menu_option] = president.party
            menu_option += 1
    stdscr.clear()
    center("Please choose one of the following options...",
            y_index, x_width, stdscr)
    y_index += 1
    for option in parties.keys():
        center(f"{option}. {parties[option]}",
                y_index, x_width, stdscr)
        y_index += 1
    party = ""
    y_index += 2
    while len(party) == 0:
        try:
            party_prompt = "Your choice: "
            stdscr.addstr(y_index,
                (x_width // 2) - (len(party_prompt) // 2),
                party_prompt)
            curses.curs_set(1)
            curses.echo()
            key = stdscr.getstr(y_index,
                ((x_width // 2) + len(party_prompt))).decode("utf-8")
            party = parties[int(key)]
            break
        except KeyError:
            party = ""
            curses.curs_set(0)
            curses.curs_set(1)
            stdscr.refresh()
            pass
    curses.noecho()
    curses.curs_set(0)
    stdscr.clear()
    return party

def by_party(party: str) -> list:
    """Find out which presidents belonged to a given party"""
    for key in presidents.keys():
        if presidents[key].party == party:
            yield presidents[key]

#
# Initialize the system
#
def load_data() -> None:
    for line in fileinput.input('presidents.tsv'):
        stats = line.rstrip().split('\t')
        key = stats[0]
        p = President(key, stats[1], stats[2], stats[3], stats[4], stats[5])
        presidents[key] = p
        presidential_states[stats[3]].append(key)

def do_loop(stdscr):
    k = 0
    cursor_x = 0
    cursor_y = 0

    stdscr.clear()
    stdscr.refresh()

    curses.curs_set(0)
    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    result = 0
    while(result != ord('q')):
        # Clear and refresh the screen for a blank canvas
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        prompt_lines = prompt.split('\n')
        y_index = (height // 2) - (len(prompt_lines) // 2)
        # Draw the prompt
        for line in prompt_lines:
            center(line, y_index, width, stdscr)
            y_index += 1
        president_list = []
        onum = 0
        if result == ord('o'):
            stdscr.clear()
            ordinal_prompt = "Enter the number: "
            stdscr.addstr((height // 2),
                (width // 2) - (len(ordinal_prompt) // 2),
                ordinal_prompt)
            curses.curs_set(1)
            curses.echo()
            key = stdscr.getstr((height // 2),
                    ((width // 2) + len(ordinal_prompt))).decode("utf-8")
            if(int(key) <= presidents.__len__()):
                president_list.append(presidents[key])
            else:
                stdscr.clear()
                error_prompt = f"You only have {presidents.__len__()} "\
                                "presidents to choose from"
                stdscr.addstr((height // 2),
                    (width // 2) - (len(error_prompt) // 2),
                    error_prompt)
                center("Press any key to continue...",
                        (height - 2), width, stdscr)
                stdscr.getch()
                continue
            curses.curs_set(0)
            curses.noecho()
            stdscr.refresh()
        elif result == ord('y'):
            stdscr.clear()
            year_prompt = "Enter the year: "
            stdscr.addstr((height // 2),
                (width // 2) - (len(year_prompt) // 2),
                year_prompt)
            curses.curs_set(1)
            curses.echo()
            year = stdscr.getstr((height // 2),
                    ((width // 2) + len(year_prompt))).decode("utf-8")
            try:
                president_list.append(for_year(int(year)))
            except ValueError:
                if(int(year) < 1789):
                    message = "The office of President of the "\
                              "United States did not exist " + \
                              f"in the year {year}."
                elif(int(year) > 2024):
                    message = "We do not know who will be president " + \
                              f"in the year {year}."
                else:
                    message = "That is not a valid entry"
                stdscr.clear()
                stdscr.addstr((height // 2),
                    (width // 2) - (len(message) // 2),
                    message)
                center("Press any key to continue...",
                        (height - 2), width, stdscr)
                stdscr.getch()
                continue
        elif result == ord('s'):
            stdscr.clear()
            state_prompt = "Enter the two-letter abbreviation for the state: "
            stdscr.addstr((height // 2),
                (width // 2) - (len(state_prompt) // 2),
                state_prompt)
            curses.curs_set(1)
            curses.echo()
            results = []
            state = stdscr.getstr().decode("utf-8")
            try:
                stdscr.clear()
                results = presidential_states[state.upper()]
            except(KeyError):
                message = "That is not a valid state"
                stdscr.addstr((height // 2),
                    (width // 2) - (len(message) // 2),
                    message)
                center("Press any key to continue...",
                        (height - 2), width, stdscr)
                stdscr.getch()
                continue
            if(len(results) == 0):
                message = "No president resided in " + states[state.upper()] + \
                          " at the time of inauguration."
                stdscr.addstr((height // 2),
                    (width // 2) - (len(message) // 2),
                    message)
                center("Press any key to continue...",
                        (height - 2), width, stdscr)
                stdscr.getch()
                curses.curs_set(0)
                result = 0
                continue
            else:
                if(len(results) == 1):
                    verbiage = "president has come from"
                else:
                    verbiage = "presidents have come from"
                center("{0} {1} {2}"
                    .format(len(results), verbiage, states[state.upper()]),
                        y_index, width, stdscr)
                for key in results:
                    president_list.append(presidents[key])
        elif result == ord('p'):
            y_index = height // 3
            party = choose_party(y_index, width, stdscr)
            if party != 'None':
                message = "Presidents who belonged to the {0} "\
                          "Party".format(party)
            else:
                message = "Unaffiliated Presidents"
            center(message.upper(), y_index, width, stdscr)
            y_index += 2
            for president in by_party(party):
                center(president.name, y_index, width, stdscr)
                y_index += 1
            center("Press 'c' to continue...", (height - 2), width, stdscr)
            if stdscr.getch() == ord('c'):
                result = 0
                continue
        if(len(president_list) != 0):
            stdscr.clear()
            y_index = 5
            curses.curs_set(0)
            curses.noecho()
            for pres in president_list:
                pres.display(y_index, width, stdscr)
                y_index += 4
            center("Press 'c' to continue...", (height - 2), width, stdscr)
            stdscr.timeout(-20)
            if stdscr.getch() == ord('c'):
                result = 0
                continue
        stdscr.refresh()
        result = stdscr.getch()

def main():
    load_data()
    curses.wrapper(do_loop)

if __name__ == "__main__":
    main()
