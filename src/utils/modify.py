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