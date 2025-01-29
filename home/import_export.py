import csv


def exportcsv(filename, data):
    """ export data to csv file

    Args:
        filename (string): path and name of the csv file
        data (dictionary): data to export
    """
    
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, data.keys())
    
        for item in data:
            writer.writerow(item)
    

    return "Export to csv done"
