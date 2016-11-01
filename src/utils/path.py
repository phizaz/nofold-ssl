def utils_path():
    from os.path import dirname
    return dirname(__file__)


def root_path():
    from os.path import dirname
    return dirname(dirname(utils_path()))


def tmp_path():
    from os.path import join, exists

    path = join(root_path(), 'tmp')
    if not exists(path):
        from os import makedirs
        makedirs(path)

    return path


def src_path():
    from os.path import join
    return join(root_path(), 'src')


def queries_path():
    from os.path import join
    return join(root_path(), 'queries')


def db_path():
    from os.path import join
    return join(root_path(), 'Rfam-seed', 'db')


def norm_path():
    from os.path import join
    return join(root_path(), 'norm')


def cm_path():
    from os.path import join
    return join(root_path(), 'models', 'rfam_cms')


def tests_path():
    from os.path import join
    return join(src_path(), 'tests')


def tests_supplies_path():
    from os.path import join
    return join(tests_path(), 'supplies')


def make_path(path):
    from os.path import exists
    from os import makedirs
    if not exists(path):
        makedirs(path)


def get_cm_paths():
    from os.path import join
    from os import listdir
    path = cm_path()
    models = filter(lambda x: 'cm' in x, listdir(path))
    models.sort()
    full_path = map(lambda x: join(path, x), models)
    return list(full_path)


def results_path():
    from os.path import join
    return join(root_path(), 'results')


def family_db_path(family):
    from os.path import join
    return join(db_path(), family, family + '.db')


def family_bitscore_path(family):
    from os.path import join
    return join(db_path(), family, family + '.bitscore')


def query_db_path(query):
    from os.path import join
    return join(queries_path(), query, query + '.db')


def query_bitscore_path(query):
    from os.path import join
    return join(queries_path(), query, query + '.bitscore')
