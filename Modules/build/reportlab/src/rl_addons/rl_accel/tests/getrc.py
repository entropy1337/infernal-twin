def getrc(defns,depth=1):
    from sys import getrefcount, _getframe
    f = _getframe(depth)
    G0 = f.f_globals
    L = f.f_locals
    if L is not G0:
        LL = [L]
        while 1:
            f = f.f_back
            G = f.f_globals
            L = f.f_locals
            if G is not G0 or G is L: break
            LL.append(L)
        L = {}
        for l in reversed(LL):
            L.update(l)
    else:
        L = L.copy()
    G0 = G0.copy()
    return [getrefcount(eval(x,L,G0))-1 for x in defns.split()]

def checkrc(defns,rcv0):
    rcv1 = getrc(defns,2)
    return ' '.join(["%s %d-->%d" % (x,v,w) for x,v,w in zip(defns.split(),rcv0,rcv1) if v!=w])
