
def ordinal(num):
    if(11 <= (num % 100) <= 13):
        suffix = 'th' 
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min((num % 10), 4)]
    return str(num) + suffix

start = 0
while True:
    try:
        start = int(input("Enter a number: "))
        end = start + 20
        for x in range(start, end):
            print("%s" % ordinal(x))
        break
    except ValueError:
        print("Oops! That was no valid number.")
        exit

