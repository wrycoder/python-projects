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
for line in fileinput.input('presidents.tsv'):
    stats = line.rstrip().split('\t')
    key = stats[0]
    p = President(key, stats[1], stats[2], stats[3], stats[4], stats[5])
    presidents[key] = p
    presidential_states[stats[3]].append(key)


def do_loop():
    #
    # Enter an endless loop with a prompt
    #
    while(True):
        result = input(prompt)
        president_list = []
        onum = 0
        match result:
            case 'q':
                break
            case 'o':
                onum = input("Enter the number: ")
                if(int(onum) <= presidents.__len__()):
                    president_list.append(presidents[onum])
                else:
                    print("You only have %d presidents to choose from" %
                        presidents.__len__());
            case 'y':
                year = input("Enter the year: ")
                try:
                    president_list.append(for_year(year))
                except ValueError:
                    if(int(year) < 1789):
                        print(  "The office of President of the United States "\
                                "did not exist in the year {0}".format(int(year)))
                    elif(int(year) > 2024):
                        print(  "We do not know who will be president in {0}".format(int(year)))
                    else:
                        print("That is not a valid entry")
            case 's':
                state = input("Enter the two-letter abbreviation for the state: ")
                results = []
                try:
                    results = presidential_states[state.upper()]
                except(KeyError):
                    print("\nThat is not a valid state")
                    continue

                if(len(results) == 0):
                    print("\nNo presidents have come from " + states[state.upper()])
                else:
                    print("{:*^95}".format(""))
                    if(len(results) == 1):
                        verbiage = "president has come from"
                    else:
                        verbiage = "presidents have come from"
                    center_and_star("{0} {1} {2}"
                        .format(len(results), verbiage, states[state.upper()]))
                    for key in results:
                        president_list.append(presidents[key])
            case 'p':
                party = choose_party()
                print("{:*^95}".format(""))
                if party != 'None':
                    message = "Presidents who belonged to the {0} "\
                              "Party".format(party)
                else:
                    message = "Unaffiliated Presidents"
                center_and_star(message.upper())
                for president in by_party(party):
                    center_and_star(president.name)
                print("{:*^95}".format(""))
            case _:
                print("\nYou can only enter 'o', 'y', 's', or 'q'")
        if(len(president_list) != 0):
            print("{:*^95}".format(""))
            for pres in president_list:
                pres.display()
            print("{:*^95}".format(""))

if __name__ == "__main__":
    do_loop()
