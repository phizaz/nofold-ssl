from __future__ import print_function


def int_fam(fam):
    return int(fam[2:])


def run(start, end, cpu):
    from src import utils
    all_fam = set(map(int_fam, utils.get.get_all_families()))
    calculated_fam = set(map(int_fam, utils.get.get_calculated_families()))

    left_fam = all_fam - calculated_fam
    left_fam = list(left_fam)

    if not start:
        start = left_fam[0]
    if not end:
        end = left_fam[-1]

    print(start, end)

    job_fam = filter(lambda x: start <= x <= end, left_fam)
    from src.utils.helpers import cmscore
    from os.path import join
    for i, i_fam in enumerate(job_fam, 1):
        fam = 'RF{:05}'.format(i_fam)
        print('({}/{}) fam: {}'.format(i, len(job_fam), fam))

        records = utils.get.get_family_records(fam)
        scores = cmscore.get_cmscores(records, cpu=cpu)
        cmscore.save_cmscores(scores, join(
            utils.path.db_path(), fam, '{}.bitscore'.format(fam)
        ))


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('--start', type=int)
    parser.add_argument('--end', type=int)
    parser.add_argument('--cpu', type=int)
    args = parser.parse_args()

    run(args.start, args.end, args.cpu)
