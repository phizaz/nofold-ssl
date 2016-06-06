import numpy as np
from itertools import product
from os.path import join
import utils
import csv
import time
import pprint
from optparse import OptionParser

parser = OptionParser(usage='cluster using semi-supervised label propagation algorithm')
parser.add_option('--query', action='store', dest='QUERY', help='query')
parser.add_option('--cripple', action='store', default=0, type='int', dest='CRIPPLE', help='cripple')
(opts, args) = parser.parse_args()

QUERY = opts.QUERY

# seeding
CRIPPLE = opts.CRIPPLE
NN_SEED = [7, 13, 19, 25]
LENGTH_NORM = ['false', 'true']

# ssl
ALG = ['labelSpreading']
KERNEL = ['rbf']
GAMMA = [0.5]
ALPHA = np.linspace(0.4, 1.0, 7)

# further
# C = [1.1]
C = np.linspace(1.0, 1.3, 4)

def get_result(tag, alg):
    path = join('Rfam-seed', 'combined.' + tag + '.' + alg + '.refined.cluster.evaluation')
    with open(path, 'r') as handle:
        lines = handle.readlines()
        scores = map(float, lines[-1].strip().split())
        sensitivity, precision, max_in_cluster = scores
    return sensitivity, precision, max_in_cluster

def run_combine(query, cripple, nn_seed):
    # python combine_rfam_bitscore.py --query=rfam75id_embed-rename --cripple=0 --type=closest --nn=3
    command = 'python combine_rfam_bitscore.py --query=%s --cripple=%d --type=closest --nn=%d' % (
        query, cripple, nn_seed
    )
    print('')
    (output, res, error) = utils.run_command(command)

def run_normalize(tag, query, length_norm):
    # python pca_normalize_bitscore.py --tag=rfam75id_embed-rename.cripple0 --query=rfam75id_embed-rename
    command = 'python pca_normalize_bitscore.py --tag=%s --query=%s --lengthnorm=%s' % (
        tag, query, length_norm
    )
    (output, res, error) = utils.run_command(command)

def run_ssl(tag, alg, kernel, gamma, alpha):
    # python cluster_semi_label_propagation.py --tag=rfam75id_embed-rename.cripple0 --alg=labelPropagation --kernel=rbf --gamma=0.5 --alpha=0.8
    command = 'python cluster_semi_label_propagation.py --tag=%s --alg=%s --kernel=%s --gamma=%f --alpha=%f' % (
        tag, alg, kernel, gamma, alpha
    )
    (output, res, error) = utils.run_command(command)

def run_further(tag, alg, c):
    # python cluster_refinement_further_seprataion.py - -tag = rfam75id_embed - rename.cripple0 - -alg = labelPropagation - -C = 1.1
    command = 'python cluster_refinement_further_seprataion.py --tag=%s --alg=%s --C=%f' % (
        tag, alg, c
    )
    (output, res, error) = utils.run_command(command)

def run_evaluate(tag, query, alg):
    # python evaluate.py --tag=rfam75id_embed-rename.cripple0 --query=rfam75id_embed-rename --nofold=false --alg=labelPropagation
    command = 'python evaluate.py --tag=%s --query=%s --nofold=false --alg=%s' % (
        tag, query, alg
    )
    (output, res, error) = utils.run_command(command)

jobs_cnt = len(NN_SEED) * len(LENGTH_NORM) * len(ALG) * len(KERNEL) * len(GAMMA) * len(ALPHA) * len(C)
print('total jobs:', jobs_cnt)

job_i = 1
results = []
time_start = time.time()
for nn_seed in NN_SEED:
    cripple = CRIPPLE
    nn_seed = int(nn_seed)
    tag = QUERY + '.cripple' + str(cripple)
    print('tag:', tag)

    print('combining...')
    run_combine(QUERY, cripple, nn_seed)

    for length_norm in LENGTH_NORM:
        print('length_norm:', length_norm)
        print('normalizing...')
        run_normalize(tag, QUERY, length_norm)

        for alg, kernel, gamma, alpha in product(ALG, KERNEL, GAMMA, ALPHA):
            print('cripple:', cripple, 'nn_seed:', nn_seed)
            print('alg:', alg, 'kernel:', kernel, 'gamma:', gamma, 'alpha:', alpha)

            print('running ssl...')
            run_ssl(tag, alg, kernel, gamma, alpha)

            for c in C:
                print('job:', job_i, 'of', jobs_cnt)
                job_i += 1

                print('c:', c)

                # run
                print('run further cluster...')
                run_further(tag, alg, c)
                run_evaluate(tag, QUERY, alg)

                # get result
                sensitivity, precision, max_in_cluster = get_result(tag, alg)
                print('sense:', sensitivity)
                print('preci:', precision)
                print('max_in:', max_in_cluster)

                results.append({
                    'query': QUERY,
                    'cripple': cripple,
                    'nn_seed': nn_seed,
                    'length_norm': length_norm,
                    'alg': alg,
                    'kernel': kernel,
                    'gamma': gamma,
                    'alpha': alpha,
                    'c': c,
                    'sensitivity': sensitivity,
                    'precision': precision,
                    'max_in_cluster': max_in_cluster
                })

time_end = time.time()
print('time elapsed:', time_end - time_start)

# save results
print('saving ...')
outfile = 'parameter_search.' + QUERY + '.cripple' + str(CRIPPLE) + '.csv'
with open(outfile, 'w') as handle:
    fieldnames = ['sensitivity', 'precision', 'max_in_cluster', 'alg', 'alpha', 'nn_seed', 'length_norm','kernel', 'gamma', 'c', 'cripple', 'query']
    writer = csv.DictWriter(handle, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)
print('done...')

# best sensitivity
print('best sensitivity:')
pp = pprint.PrettyPrinter(indent=2)
best_sensitivity = max(results, key=lambda x: x['sensitivity'])
pp.pprint(best_sensitivity)

# best precision
print('best precision:')
best_precision = max(results, key=lambda x: x['precision'])
pp.pprint(best_precision)

# best max in cluster
print('best max_in_cluster:')
best_max_in_cluster = max(results, key=lambda x: x['max_in_cluster'])
pp.pprint(best_max_in_cluster)
