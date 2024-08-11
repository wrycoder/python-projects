import fileinput

prompt = """
To select a president by ordinal number, enter 'o'
To select a president by year, enter 'y'
To quit, enter 'q'
"""

def ordinal(n: int):
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix

class President:
    def __init__(self, key, name, year):
        self.key = int(key)
        self.name = name
        self.sworn_in = int(year)
    def display(self):
        print("%s, %s president of the United States, was inaugurated in %d" %
            (self.name, ordinal(self.key), self.sworn_in))

    
presidents = {}

for line in fileinput.input():
    stats = line.rstrip().split('\t')
    key = stats[0]
    p = President(key, stats[1], stats[2])
    presidents[key] = p

def for_year(year):
    y = int(year)
    if (y < 1789) | (y > 2024):
        raise ValueError('Invalid year')
    for i in presidents.keys():
        if presidents[i].sworn_in > y:
            target_key = int(i) - 1
            return presidents[str(target_key)]

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

