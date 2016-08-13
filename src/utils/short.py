def is_bg(name):
    bg_keywords = ['dinucShuff', 'bg']
    return any(keyword in name for keyword in bg_keywords)

def fam_of(name):
    fam = name.split('_')[0]
    if fam[:2] != 'RF':
        raise ValueError('not a seed sequenec, not RF')
    return fam

def qfam_of(name):
    fam = name.split('_')[0]
    if fam[:2] != 'QR':
        raise ValueError('not a query sequence, not QRF')
    # return the family part not including 'Q'
    return fam[1:]