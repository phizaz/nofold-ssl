if __name__ == '__main__':
    '''
    Automator for printing search space 'queries'
    '''

    d =  {
        "query": "rfam75id-rename",
        "unformatted": False,
        "cripple": 0
    }

    dd = []

    for i in range(41):
        _d = dict(d)
        _d['cripple'] = i
        dd.append(_d)

    import json
    print(json.dumps(dd))
