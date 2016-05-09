import os, sys
sys.path.insert(0, 'src')
from utils_analysis import *

root = 'Rfam-seed'
if not os.path.exists(os.path.join(root, 'fasta')):
    os.makedirs(os.path.join(root, 'fasta'))

files = [f for f in os.listdir(root) if os.path.isfile(os.path.join(root, f))]

for each in files:
    print(each)

    command = '/usr/local/bin/esl-reformat fasta %s > %s' % (
        os.path.join(root, each),
        os.path.join(root, 'fasta', each + '.fasta')
    )
    (output, res, error) = run_command(command)

    if error:
        print ">>Error detected. Exiting."
        print(output)
        sys.exit()