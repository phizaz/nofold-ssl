import numpy as np
from itertools import product
from os.path import join
import utils
import csv
import time
import pprint

QUERY = 'rfam75id_embed-rename'

# seeding
CRIPPLE = [0]
NN_SEED = [1, 3, 5, 7, 13, 19]

# ssl
ALG = ['labelPropagation', 'labelSpreading']
KERNEL = ['rbf']
GAMMA = [0.5]
ALPHA = np.linspace(0.1, 1.0, 10)

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

def run_normalize(tag, query):
    # python pca_normalize_bitscore.py --tag=rfam75id_embed-rename.cripple0 --query=rfam75id_embed-rename
    command = 'python pca_normalize_bitscore.py --tag=%s --query=%s' % (
        tag, query
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

jobs_cnt = len(CRIPPLE) * len(NN_SEED) * len(ALG) * len(KERNEL) * len(GAMMA) * len(ALPHA) * len(C)
print('total jobs:', jobs_cnt)

job_i = 1
results = []
time_start = time.time()
for cripple, nn_seed in product(CRIPPLE, NN_SEED):
    nn_seed = int(nn_seed)
    tag = QUERY + '.cripple' + str(cripple)

    print('combining...')
    run_combine(QUERY, cripple, nn_seed)
    print('normalizing...')
    run_normalize(tag, QUERY)

    for alg, kernel, gamma, alpha in product(ALG, KERNEL, GAMMA, ALPHA):

        for c in C:
            print('job:', job_i, 'of', jobs_cnt)
            job_i += 1

            print('cripple:', cripple, 'nn_seed:', nn_seed)
            print('alg:', alg, 'kernel:', kernel, 'gamma:', gamma, 'alpha:', alpha)
            print('c:', c)

            # run
            print('running...')
            run_ssl(tag, alg, kernel, gamma, alpha)
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
outfile = 'parameter_search.' + QUERY + '.csv'
with open(outfile, 'w') as handle:
    fieldnames = ['sensitivity', 'precision', 'max_in_cluster', 'alg', 'alpha', 'nn_seed', 'kernel', 'gamma', 'c', 'cripple', 'query']
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
