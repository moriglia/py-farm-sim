import csv


def savecsv(data, filename):
    with open(filename, 'w') as fd:
        wr = csv.writer(fd)
        wr.writerows(data)
    return
