def namemap(names):
    all_names = set(names)
    all_int = [i for i in range(len(all_names))]
    return dict(zip(all_names, all_int)), dict(zip(all_int, all_names))