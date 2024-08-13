import fileinput

prompt = """
To select a president by ordinal number, enter 'o'
To select a president by year, enter 'y'
To quit, enter 'q'
"""

presidents = {}

states = { 'AR': 'Arkansas',
    'CA': 'California',
    'DC': 'The District of Columbia',
    'DE': 'Delaware',
    'GA': 'Georgia',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'LA': 'Louisiana',
    'MA': 'Massachusetts',
    'MI': 'Michigan',
    'MO': 'Missouri',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NY': 'New York',
    'OH': 'Ohio',
    'PA': 'Pennsylvania',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'VA': 'Virginia'
    }

def center_and_star(text):
    print("*", end='')
    print("{:^93s}".format(text), end='')
    print("*")

def ordinal(n: int):
    """Convert a cardinal number to an ordinal"""
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix

class President:
    def __init__(self, key, name, year, state):
        self.key = int(key)
        self.name = name
        self.sworn_in = int(year)
        self.state = states[state]

    def display(self):
        print("{:*^95}".format(""))
        message =   "{0}, {1} president of the United States, "\
                    "was inaugurated in {2}".format(self.name, ordinal(self.key), self.sworn_in)
        center_and_star(message)
        message = "{0} was a resident of {1} on Inauguration Day.".format(self.name, self.state)
        center_and_star(message)
        print("{:*^95}".format(""))

#
# 1. Initialize the system
#

for line in fileinput.input():
    stats = line.rstrip().split('\t')
    key = stats[0]
    p = President(key, stats[1], stats[2], stats[3])
    presidents[key] = p


def for_year(year):
    """Find out who was president in the given year"""
    y = int(year)
    if (y < 1789) | (y > 2024):
        raise ValueError('Invalid year')
    for i in presidents.keys():
        if presidents[i].sworn_in > y:
            target_key = int(i) - 1
            return presidents[str(target_key)]

#
# 2. Enter an endless loop with a prompt
#
while(True):
    result = input(prompt)
    president = 0
    onum = 0
    match result:
        case 'q':
            break
        case 'o':
            onum = input("Enter the number: ")
            if(int(onum) < presidents.__len__()):
                president = presidents[onum]
            else:
                print("You only have %d presidents to choose from" %
                    presidents.__len__());
        case 'y':
            year = input("Enter the year: ")
            try:
                president = for_year(year)
            except ValueError:
                if(int(year) < 1789):
                    print(  "The office of President of the United States "\
                            "did not exist in {0}".format(int(year)))
                elif(int(year) > 2024):
                    print(  "We do not know who will be president in {0}".format(int(year)))
                else:
                    print("That is not a valid entry")

    if(president != 0):
        president.display()

