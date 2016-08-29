def retain_bitscore_cols(cols, points, header):
    retain_idxs = []
    for col in cols:
        retain_idxs.append(header.index(col))

    new_header = []
    for i in retain_idxs:
        new_header.append(header[i])

    new_points = []
    for point in points:
        row = []
        for i in retain_idxs:
            row.append(point[i])
        new_points.append(row)
    return new_points, new_header


def group_bitscore_by_family(names, points):
    from .short import general_fam_of
    from collections import defaultdict
    groups = defaultdict(list)
    for name, point in zip(names, points):
        fam = general_fam_of(name)
        groups[fam].append(point)
    return groups


def group_names_by_family(names):
    from .short import general_fam_of, is_bg
    names_by_family = {}
    for name in names:
        if is_bg(name):
            continue

        family = general_fam_of(name)
        if family not in names_by_family:
            names_by_family[family] = []
        names_by_family[family].append(name)
    return names_by_family
