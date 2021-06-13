def parseInt(s):
    return int(s.replace(',',''))

def patch(seed, newArgs):
    return dict(seed, **newArgs)
