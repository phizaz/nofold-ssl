import numpy as np
from itertools import product, chain
from os.path import join
import utils
import csv
import time
import pprint
import sys
from argparse import ArgumentParser
from collections import defaultdict
from gaw import GawClient

def get_result(tag, alg):
    path = join('../results', 'combined.' + tag + '.' + alg + '.refined.cluster.evaluation')
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
    (output, res, error) = utils.run_command(command)
    if error:
        raise Exception(output)

def run_normalize(tag, query, length_norm):
    # python pca_normalize_bitscore.py --tag=rfam75id_embed-rename.cripple0 --query=rfam75id_embed-rename
    command = 'python pca_normalize_bitscore.py --tag=%s --query=%s --lengthnorm=%s' % (
        tag, query, length_norm
    )
    (output, res, error) = utils.run_command(command)
    if error:
        raise Exception(output)

def run_ssl(tag, alg, kernel, gamma, alpha):
    # python cluster_semi_label_propagation.py --tag=rfam75id_embed-rename.cripple0 --alg=labelPropagation --kernel=rbf --gamma=0.5 --alpha=0.8
    command = 'python cluster_semi_label_propagation.py --tag=%s --alg=%s --kernel=%s --gamma=%f --alpha=%f' % (
        tag, alg, kernel, gamma, alpha
    )
    (output, res, error) = utils.run_command(command)
    if error:
        raise Exception(output)

def run_further(tag, alg, c):
    # python cluster_refinement_further_seprataion.py - -tag = rfam75id_embed - rename.cripple0 - -alg = labelPropagation - -C = 1.1
    command = 'python cluster_refinement_further_seprataion.py --tag=%s --alg=%s --C=%f' % (
        tag, alg, c
    )
    (output, res, error) = utils.run_command(command)
    if error:
        raise Exception(output)

def run_evaluate(tag, query, alg):
    # python evaluate.py --tag=rfam75id_embed-rename.cripple0 --query=rfam75id_embed-rename --nofold=false --alg=labelPropagation
    command = 'python evaluate.py --tag=%s --query=%s --nofold=false --alg=%s' % (
        tag, query, alg
    )
    (output, res, error) = utils.run_command(command)
    if error:
        raise Exception(output)


parser = ArgumentParser(usage='cluster using semi-supervised label propagation algorithm')
parser.add_argument('--query', required=True)
parser.add_argument('--cripple', default=0, type=int)
parser.add_argument('--use-cache', default=False, action='store_true')
parser.add_argument('--cache-ip', type=str)
parser.add_argument('--cache-port', type=int)
parser.add_argument('--cache-secret', type=str)
parser.add_argument('--flush-cache', default=False, action='store_true')
args = parser.parse_args()

if args.use_cache:
    if not args.cache_ip:
        print 'no cache ip (--cache-ip)'
        sys.exit()
    if not args.cache_port:
        print 'no cache port (--cache-port)'
        sys.exit()
    if not args.cache_secret:
        print 'no admin secret (--cache-secret)'
        sys.exit()

# query name
QUERY = args.query

# seeding
CRIPPLE = args.cripple

search_arguments = [
    ['query', 'cripple', 'nn_seed'],
    ['length_norm'],
    ['alg', 'kernel', 'gamma', 'alpha'],
    ['c']
]
search_space = {
    'query': [QUERY],
    'cripple': [CRIPPLE],
    'nn_seed': [7, 13, 25],
    # 'nn_seed': [7],
    'length_norm': ['false', 'true'],
    # 'length_norm': ['false'],
    'alg': ['labelSpreading', 'labelPropagation'],
    # 'alg': ['labelSpreading'],
    'kernel': ['rbf'],
    'gamma': [0.5],
    'alpha': np.linspace(0.4, 1.0, 7),
    # 'alpha': [1.0],
    'c': np.linspace(1.0, 1.5, 6),
}

def space_of(arg):
    return search_space[arg]

def level_of(arg):
    for i, items in enumerate(search_arguments):
        if arg in items:
            return i
    raise NameError('arg not found')

def stack_of(job):
    stack = defaultdict(list)
    for arg, each in zip(all_arguments, job):
        level = level_of(arg)
        stack[level].append(each)
    return stack

def uncommon_level(job_a, job_b):
    stack_a = stack_of(job_a)
    stack_b = stack_of(job_b)
    for (level, items_a), (level, items_b) in zip(stack_a.items(), stack_b.items()):
        if items_a != items_b:
            return level
    raise ValueError('job a and b are equal')

def jobkey_of(job):
    keys = []
    for each in job:
        if isinstance(each, float):
            keys.append(str(round(each, 6)))
        else:
            keys.append(str(each))
    return '[nofold-ssl]' + '|'.join(keys) # adding some namespace

def result_of(job, d):
    assert isinstance(d, dict)

    expect_keys = {'sensitivity', 'precision', 'max_in_cluster'}
    assert set(d.keys()) == expect_keys

    result_dict = dict(zip(all_arguments, job))

    # turn the value to float
    for key, val in d.items():
        d[str(key)] = float(val)

    result_dict.update(d)
    return result_dict

def compute_from(level, job):
    print 'compute from level:', level
    query, cripple, nn_seed, length_norm, alg, kernel, gamma, alpha, c = job

    tag = '{}.cripple{}'.format(query, cripple)

    # if level == 0:
    #     print 'run combine'
    #     run_combine(query, cripple, nn_seed)
    #     level += 1

    if level == 1:
        print 'run normalize'
        run_normalize(tag, query, length_norm)
        level += 1

    if level == 2:
        print 'run ssl'
        run_ssl(tag, alg, kernel, gamma, alpha)
        level += 1

    if level == 3:
        print 'run further'
        run_further(tag, alg, c)
        print 'run evaluate'
        run_evaluate(tag, query, alg)
        level += 1

    sensitivity, precision, max_in_cluster = get_result(tag, alg)
    return dict(sensitivity=sensitivity,
                precision=precision,
                max_in_cluster=max_in_cluster)

def run():
    global last_job
    for i, job in enumerate(all_jobs):
        jobkey = jobkey_of(job)

        print 'jobkey:', jobkey

        if args.use_cache:
            raise Exception('cache is not ready for now')

        if last_job:
            start_level = uncommon_level(last_job, job)
        else:
            start_level = 0

        # perform the real job
        print 'working on job:', i, 'detail:', job
        data = compute_from(start_level, job)
        results[i] = result_of(job, data)
        print 'job done:', i, 'result:', results[i]
        last_job = job

        if args.use_cache:
            raise Exception('cache is not ready for now')

all_arguments = list(chain(*search_arguments))
output_fields = ['sensitivity', 'precision', 'max_in_cluster']
all_jobs = list(product(*map(space_of, all_arguments)))

project_name = 'parameter_search.{}.cripple{}'.format(QUERY, CRIPPLE)
out_file = project_name + '.csv'

print 'project name:', project_name

if args.use_cache:
    raise Exception('cache is not ready for now')
else:
    print 'dont use cache'

results = [None] * len(all_jobs)
last_job = None

# perform the search until done
while True:
    # perform the search
    run()

    if all(results):
        break
    else:
        time.sleep(60)

# save results
print('saving ...')
outfile = 'parameter_search.{}.cripple{}.csv'.format(QUERY, CRIPPLE)
with open(outfile, 'w') as handle:
    writer = csv.DictWriter(handle, fieldnames=all_arguments + output_fields)
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
