'''
To see if the memory leakage happens in combine_rfam_bitscore or not ?
'''
if __name__ == '__main__':
    from src import combine_rfam_bitscore

    query = 'fam40_typedistributed_embed+bg_weak'

    from src.utils.helpers import sizeof
    for i in range(10):
        print('round {}'.format(i + 1))
        # leakage comes from here
        names, points, header = combine_rfam_bitscore.run(query, False, 6, 7, False, None)
        # print('size of names : {}'.format(sizeof.total_size(names)))
        # print('size of points : {}'.format(sizeof.total_size(points)))
        # print('size of header : {}'.format(sizeof.total_size(header)))

        # solves memory leak, but doing this way doesn't really solve the problem at the root
        names = None
        points = None
        header = None
        import gc
        gc.collect()

    print('done!')
