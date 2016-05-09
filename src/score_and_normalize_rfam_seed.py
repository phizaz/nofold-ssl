import os, sys
from utils_analysis import *
import shutil
from optparse import OptionParser

parser = OptionParser(usage='score and normalize the Rfam seed')
parser.add_option("--begin", action="store", default='RF00000', dest="START_RF", help="Path to folder containing Infernal executables. Default is to assume they have been added to your PATH and can be called by name.")
parser.add_option("--cpus", action="store", type='int', default=1, dest="MAX_CPU", help="Maximum number of CPUs to use. Default is [%default].")
(opts, args) = parser.parse_args()

print('start RF:', opts.START_RF)
print('max CPU:', opts.MAX_CPU)

path = '../Rfam-seed/db'

def things_count(path):
    l = list(filter(lambda x: x != '.DS_Store', os.listdir(path)))
    return len(l)

families = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f)) and things_count(os.path.join(path, f)) == 1]
families.sort()
families = list(filter(lambda x: x >= opts.START_RF, families))

for family in families:
    print(family)

    command = 'python %s %s --cpus=%d --infernal-path=%s' % (
        'score_and_normalize.py',
        os.path.join(path, family, family + '.db'),
        opts.MAX_CPU,
        '/usr/local/bin/'
    )
    (output, res, error) = run_command(command)

    shutil.rmtree(os.path.join(path, family, 'cmscore_results_rfam'))

    if error:
        print ">>Error detected. Exiting."
        print(output)
        sys.exit()