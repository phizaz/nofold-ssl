import utils
from os.path import join, exists
from operator import itemgetter
from functools import partial
import numpy as np
from normalizer_length import LengthNormalizer
from argparse import ArgumentParser
import sys

parser = ArgumentParser(description='rename rna bitscore')
parser.add_argument('--query', action='store', required=True)
parser.add_argument('--output', action='store', required=True)
args = parser.parse_args()

query = args.query
out_query = args.output

if not utils.check_query(query):
    print('query is not ready')
    sys.exit()

ori_names, ori_points, ori_header = utils.get_query_bitscores(query)

print('length normalizing...')
normalizer = LengthNormalizer()
points = normalizer.length_normalize_full(ori_names, ori_points, ori_header, query)

print('separate by family')
by_family = {}
for name, point in zip(ori_names, points):
    # skip backgrounds
    if name.find('bg') != -1:
        continue

    fam = name.split('_')[0]
    if fam not in by_family:
        by_family[fam] = ([], [])
    t_names, t_points = by_family[fam]
    t_names.append(name)
    t_points.append(point)
print('fam count:', len(by_family))

def is_cm_strong(col, points, header):
    idx = header.index(col)
    scores = np.array(list(map(itemgetter(idx), points)))
    mean = scores.mean()
    # if mean > 3.0:
    #     print('col:', col, 'mean:', mean)
    return mean > 3.0

strong_cms = set()
for fam, (names, points) in by_family.items():
    for col in ori_header:
        if is_cm_strong(col, points, ori_header):
            strong_cms.add(col)

print(len(strong_cms))
print(strong_cms)

print('writing..')
out_path = join('../queries', out_query)
utils.make_path(out_path)
out_file = join(out_path, out_query + '.bitscore')
with open(out_file, 'w') as handle:
    header = [col for col in ori_header if col not in strong_cms]
    print('header cnt:', len(header))

    handle.write('\t'.join(header) + '\n')
    for name, point in zip(ori_names, ori_points):
        weak_point = []
        for col, digit in zip(ori_header, point):
            if col not in strong_cms:
                weak_point.append(digit)
        handle.write('{}\t{}\n'.format(
            name, '\t'.join(map(str, weak_point))
        ))
print('done!')