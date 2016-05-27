import os, sys
from os.path import join, exists, isdir, isfile, splitext
from os import listdir
from utils_analysis import *
import shutil
from optparse import OptionParser
from Bio import SeqIO
from multiprocessing.pool import Pool

parser = OptionParser(usage='score and normalize the Rfam seed')
parser.add_option("--begin", action="store", default='RF00000', dest="START_RF", help="Path to folder containing Infernal executables. Default is to assume they have been added to your PATH and can be called by name.")
parser.add_option("--cpus", action="store", type='int', default=1, dest="MAX_CPU", help="Maximum number of CPUs to use. Default is [%default].")
(opts, args) = parser.parse_args()

print('start RF:', opts.START_RF)
print('max CPU:', opts.MAX_CPU)

path = '../Rfam-seed/db'

def get_family_record_cnt(family):
    db_file = os.path.join(path, family, family + '.db')
    with open(db_file, 'r') as handle:
        records = SeqIO.parse(handle, 'fasta')
        names = set(map(lambda x: x.name, records))
        record_cnt = len(names)
    return record_cnt


def check_family(family):
    record_cnt = get_family_record_cnt(family)
    bitscore_file = os.path.join(path, family, family + '.bitscore')
    if not exists(bitscore_file):
        return False
    with open(bitscore_file, 'r') as handle:
        # ignore the header line
        handle.readline()
        line_cnt = 0
        for line in handle:
            line = line.strip()

            if len(line) == 0:
                continue

            line_cnt += 1
            tokens = line.split('\t')
            name, scores = tokens[0], tokens[1:]
            if len(scores) != 1973:
                return False

        if line_cnt != record_cnt:
            return False
    return True

def remove_cmscore_results(family):
    cmscore_path = os.path.join(path, family, 'cmscore_results_rfam')
    if exists(cmscore_path):
        shutil.rmtree(cmscore_path)
        return True
    return False

all_families = [f for f in listdir(path) if isdir(join(path, f))]
p = Pool()
check_results = p.map(check_family, all_families)
calculated_families = list(map(lambda fr: fr[0], filter(lambda fr: fr[1], zip(all_families, check_results))))

for family in calculated_families:
    if remove_cmscore_results(family):
        print('removing cmscores of', family)

# uncalculated families
families = list(set(all_families) - set(calculated_families))
families.sort()
families = list(filter(lambda x: x >= opts.START_RF, families))
print('calculating cmscore for', len(families), 'families...')

if len(families) == 0:
    print('done!')
    sys.exit(0)

print('starting from', opts.START_RF, 'actually', families[0])

sys.exit(0)

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
        if check_family(family):
            print('calculation successful, removing cmscore results')
            remove_cmscore_results(family)
        else:
            print('calculation unsuccessful..')
