"""Script to get the unique genera from a collection of all species

Author: Matthias van den Belt
"""
from sys import argv

def write_unique_genera():
    """Writes unique genera to the output file

    Output:
        - written file
    """
    with open(argv[1]) as inf:
        all_lines = inf.readlines()

    all_genera = []
    for line in all_lines:
        genus = line.strip().split()[0]

        if genus not in all_genera:
            all_genera.append(genus)

    with open(argv[2], 'w') as outf:
        for g in all_genera:
            outf.write(f'{g}\n')

    print(len(all_genera))
    # total number of genera is used in bash script from which this script
    # is called. Above line should be left in!

write_unique_genera()
