def utils_path():
    from os.path import dirname
    return dirname(__file__)

def root_path():
    from os.path import dirname
    return dirname(dirname(utils_path()))

def src_path():
    from os.path import join
    return join(root_path(), 'src')

def queries_path():
    from os.path import join
    return join(root_path(), 'queries')

def db_path():
    from os.path import join
    return join(root_path(), 'Rfam-seed', 'db')


def make_path(path):
    from os.path import exists
    from os import makedirs
    if not exists(path):
        makedirs(path)

def get_cm_paths():
    from os.path import join
    from os import listdir
    path = join(root_path(), 'models', 'rfam_cms')
    models = filter(lambda x: 'cm' in x, listdir(path))
    full_path = map(lambda x: join(path, x), models)
    return list(full_path)

def results_path():
    from os.path import join
    return join(root_path(), 'results')
