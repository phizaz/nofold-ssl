def is_bg(name):
    bg_keywords = ['dinucShuff', 'bg']
    return any(keyword in name for keyword in bg_keywords)

def is_seed(name):
    try:
        fam = fam_of(name)
        return True
    except:
        return False

def fam_of(name):
    fam = name.split('_')[0]
    if fam[:2] != 'RF':
        raise ValueError('not a seed sequence, not RF')
    return fam

def qfam_of(name):
    fam = name.split('_')[0]
    if fam[:2] != 'QR':
        raise ValueError('not a query sequence, not QRF')
    # return the family part not including 'Q'
    return fam[1:]

def general_fam_of(name):
    return name.split('_')[0]

def normalize_array(array):
    import scipy.stats
    return scipy.stats.mstats.zscore(array)

def identical_clusters(A, B):
    if len(A) != len(B):
        return False

    def tuplize(clusters):
        l = []
        for each in clusters:
            l.append(tuple(set(each)))
        return tuple(sorted(l))

    return tuplize(A) == tuplize(B)

def list_equal(a, b):
    if len(a) != len(b): return False
    return all(aa == bb for aa, bb in zip(a, b))
