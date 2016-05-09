import os, sys
from utils_analysis import *

path = '../Rfam-seed/db'

families = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f)) and len(list(map(lambda x: x != '.DS_Store', os.listdir(os.path.join(path, f))))) == 1]
families.sort()

for family in families:
    print(family)

    command = 'python %s %s --cpus=%d' % (
        'score_and_normalize.py',
        os.path.join(path, family, family + '.db'),
        4
    )
    (output, res, error) = run_command(command)

    if error:
        print ">>Error detected. Exiting."
        print(output)
        sys.exit()