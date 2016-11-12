from os.path import join, exists, isdir
from os import listdir
from Bio import SeqIO
from multiprocessing.pool import Pool
import sys

'''
add successfully computed family
'''

raise NotImplemented # need refactoring needed

path = '../Rfam-seed/db'

def get_family_record_cnt(family):
    db_file = join(path, family, family + '.db')
    with open(db_file, 'r') as handle:
        records = SeqIO.parse(handle, 'fasta')
        names = set(map(lambda x: x.name, records))
        record_cnt = len(names)
    return record_cnt

def check_family(family):
    record_cnt = get_family_record_cnt(family)
    bitscore_file = join(path, family, family + '.bitscore')
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

def run_command(command, verbose=False):
    """
    Run the given command using the system shell
    *fix this to print output as it goes
    """
    import subprocess
    error = False

    if verbose == True:
        print command
        print ""

    job = subprocess.Popen(command, bufsize=0, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    jobOutput = []
    if verbose == True:
        for line in job.stdout:
            print "   ", line,
            jobOutput.append(line)
    else:
        jobOutput = job.stdout.readlines()
    result = job.wait()
    if result != 0:
        error = True

    return (jobOutput, result, error)


all_families = [f for f in listdir(path) if isdir(join(path, f))]
pool = Pool()
check_results = pool.map(check_family, all_families)
pool.close()
calculated_families = list(map(lambda fr: fr[0], filter(lambda fr: fr[1], zip(all_families, check_results))))

for family in sorted(calculated_families):
    command = 'git add %s' % (
        join(path, family)
    )
    (output, res, error) = run_command(command)

    if error:
        print('error:', error)
        print(res)
        print(output)
        sys.exit()
    else:
        print('adding', family, 'to the git')