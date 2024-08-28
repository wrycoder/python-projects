"""lmmm (Least, Most, Median, Mean)

This module processes data in a tab-separated input file.
It is assumed that the input file has two columns, that the 
first line of the input file contains the labels of the two
fields being examined, and that the second column in each 
line of the file contains a floating-point numerical value.

The following values will be returned:

    - LEAST. The smallest of the values in the second column
    - MOST. The largest of the values in the second column
    - MEDIAN. The 50th percentile for the set of numbers in the file
    - MEAN. The mathematical average of the data in the second column

"""
import sys, io

def sort(data, field='value', r=False, /):
    """Order the data by the specified field.
       The data is expected to be contained in a two-column table.
    """
    if isinstance(data, dict):
        if field == 'value':
            index = 1
        else:
            index = 0
        sorted_list = sorted(data.items(), key=lambda x:x[index],
            reverse=r)
        return dict(sorted_list)
    else:
        raise ArgumentError
    
def median(data):
    """Calculate the median value in the data"""
    values = list(data.values())
    if len(values) % 2 == 0:
        num1 = values[len(values) // 2]
        num2 = values[(len(values) + 1) // 2]
        return (num1 + num2) / 2
    else:
        return values[(len(values) + 1) // 2]

def mean(data):
    """Calculate the mean value in the data"""
    values = list(data.values())
    return sum(values) / len(values)


def lmmm(filename):
    inputfile = io.open(filename)
    current_table = {}
    labels = { 'column_1': None, 'column_2': None }
    for line in inputfile.readlines():
        if labels['column_1'] == None:
            data = line.rstrip().split('\t')
            labels['column_1'] = data[0]
            labels['column_2'] = data[1]
            continue
        if len(line.rstrip()) > 0:
            data = line.rstrip().split('\t')
            current_table[data[0]] = float(data[1])

    inputfile.close()

    ascending_values = sort(current_table, 'value')
    for item in ascending_values.items():
        print("LEAST: {0}".format(item))
        break
    descending_values = sort(current_table, 'value', True)
    for item in descending_values.items():
        print("MOST: {0}".format(item))
        break
    print("MEDIAN: {0}".format(median(ascending_values)))
    print("MEAN: {0}".format(mean(ascending_values)))
    sorted_keys = sort(current_table, 'key')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise FileNotFoundError("Please specify a valid input file")
    lmmm(sys.argv[1])
