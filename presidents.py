import fileinput

prompt = """
To select a president by ordinal number, enter 'o'
To select a president by year, enter 'y'
To select a president by state, enter 's'
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

def center_and_star(text):
    """Center the text, with asterisks at left and right."""
    print("*", end='')
    print("{:^93s}".format(text), end='')
    print("*")

def ordinal(n: int) -> str:
    """Convert a cardinal number to an ordinal."""
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix

def pronoun(p_string, p_case):
    """Find appropriate pronoun for a given case"""
    cases = ['subject', 'object', 'possessive']
    pronouns = p_string.split('/')
    p_table = dict(zip(cases, pronouns))
    return p_table[p_case]

class President:
    def __init__(self, key, name, year, state, pronouns):
        self.key = int(key)
        self.name = name
        self.sworn_in = int(year)
        self.state = states[state]
        self.pronouns = pronouns

    def display(self) -> None:
        message =   "{0}, {1} president of the United States, "\
                    "was inaugurated in {2}.".format(self.name, ordinal(self.key), self.sworn_in)
        center_and_star(message)
        message = "{0} was a resident of {1} on Inauguration Day.".format(
            pronoun(self.pronouns, 'subject').capitalize(), self.state)
        center_and_star(message)

def for_year(year) -> President:
    """Find out who was president in the given year."""
    y = int(year)
    if (y < 1789) | (y > 2024):
        raise ValueError('Invalid year')
    for i in presidents.keys():
        if presidents[i].sworn_in > y:
            target_key = int(i) - 1
            return presidents[str(target_key)]

#
# 1. Initialize the system
#
for line in fileinput.input('presidents.tsv'):
    stats = line.rstrip().split('\t')
    key = stats[0]
    p = President(key, stats[1], stats[2], stats[3], stats[4])
    presidents[key] = p
    presidential_states[stats[3]].append(key)

#
# 2. Enter an endless loop with a prompt
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

        case _:
            print("\nYou can only enter 'o', 'y', 's', or 'q'")
    if(len(president_list) != 0):
        print("{:*^95}".format(""))
        for pres in president_list:
            pres.display()
        print("{:*^95}".format(""))

