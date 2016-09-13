from __future__ import print_function


def is_valid_cmscore(output_lines, records):
    # go through each file, extract bitscores
    # check if any IDs got cut off
    from src import utils
    record_names = set(utils.modify.names_of_records(records))
    having_names = set()
    for line in output_lines:
        if line[0] == '#':
            continue
        tokens = line.split()
        if len(tokens) != 5:
            continue
        name = tokens[0]
        having_names.add(str(name))

    return record_names == having_names


def get_cmname(output_lines):
    tmpList = output_lines[12].split()
    cmName = tmpList[2]
    return cmName


def get_cmscore_score(output_lines):
    from collections import OrderedDict
    output = OrderedDict()
    # get scores
    for line in output_lines:
        if line[0] != "#":  # skip these lines
            columns = line.strip().split()
            if len(columns) == 5:
                id = columns[0]
                score = float(columns[
                                  2])  # we use the first score, unbanded d&c cyk, because "non-banded CYK variants are guaranteed to find the optimal alignment and score of each sequence" (Infernal 1.0 userguide pg. 93)
                output[id] = score

    return output


def get_cmscore_output(cm_file, records, prog_path='cmscore'):
    from src import utils
    from os.path import join

    tmp_file = join(utils.path.tmp_path(), utils.short.unique_name())
    utils.save.save_records(records, tmp_file)

    max_mem = 8000  # MB

    import time
    start = time.time()  # time the scoring for this CM
    from src import utils
    output = utils.run.run_command([
        prog_path, '--mxsize={}'.format(max_mem), '--search', '-a', '--infile', tmp_file, cm_file
    ])

    if 'Error' in output:
        print('output:', output)
        raise Exception('error found during get_cmscore')

    total_time = time.time() - start

    from os import remove
    remove(tmp_file)

    from io import StringIO
    string_io = StringIO(unicode(output))
    output_lines = list(map(str, string_io.readlines()))

    return (output_lines, total_time)


def get_cmscore(cm_file, records, prog_path='cmscore'):
    output_lines, total_time = get_cmscore_output(cm_file, records, prog_path)
    if not is_valid_cmscore(output_lines, records):
        raise ValueError('Error occurred during cmscore, may be names are too long')

    cm_name = get_cmname(output_lines)
    score = get_cmscore_score(output_lines)
    return (cm_name, score, total_time)


def get_cmscores(records, prog_path='cmscore'):
    from multiprocessing import Pool

    p = Pool()
    from src import utils
    cm_files = utils.path.get_cm_paths()
    from functools import partial
    fn = partial(get_cmscore, records=records, prog_path=prog_path)

    from collections import OrderedDict
    output = OrderedDict()
    for i, (cm_name, score, time) in enumerate(p.imap(fn, cm_files), 1):
        print('({}/{}) cm_name: {} time elapsed: {:.3f}'.format(i, len(cm_files), cm_name, time))
        for name, val in score.items():
            if name not in output:
                output[name] = OrderedDict()
            output[name][cm_name] = val
    return output

def serialize_cmscores(cmscores):
    output = ''
    first = True
    for name, cm in cmscores.items():
        if first:
            first = False
            keys = cm.keys()
            output += '\t'.join(keys) + '\n'

        vals = cm.values()
        output += name + '\t'
        output += '\t'.join(map(str, vals)) + '\n'
    return output

def save_cmscores(cmscores, target_file):
    with open(target_file, 'w') as handle:
        handle.write(serialize_cmscores(cmscores))
