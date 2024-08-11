import fileinput

def ordinal(n: int):
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix


class President:
    def __init__(self, name, year):
        self.name = name
        self.sworn_in = int(year)
    def display(self, number):
        print("%s, %s president of the United States, was inaugurated in %d" %
            (self.name, ordinal(int(number)), self.sworn_in))

presidents = {}

for line in fileinput.input():
    stats = line.rstrip().split('\t')
    key = stats[0]
    p = President(stats[1], stats[2])
    presidents[key] = p

while(True):
    result = input( "Which president do you want to see? "\
                    "(Enter a number, or 'q' to quit) ")
    if result == 'q':
        break
    elif(int(result) < presidents.__len__()):
        presidents[result].display(int(result))
    else:
        print("You only have %d presidents to choose from" %
            presidents.__len__());
                
