import os, sys
from os.path import join, exists, isdir, isfile, splitext
from os import listdir
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

def check_family(family):
    expected_file = join(path, family, family + '.bitscore')
    return exists(expected_file)

families = [f for f in listdir(path) if isdir(join(path, f)) and not check_family(f)]
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

    if error:
        print ">>Error detected. Exiting."
        print(output)
        sys.exit()
    else:
        # check the cmscore results integrity
        cmscore_results = os.path.join(path, family, 'cmscore_results_rfam')
        files = [f for f in listdir(cmscore_results) if isfile(join(cmscore_results, f)) and splitext(join(cmscore_results, f))[1] == '.txt']
        if len(files) == 1973:
            shutil.rmtree(os.path.join(path, family, 'cmscore_results_rfam'))
