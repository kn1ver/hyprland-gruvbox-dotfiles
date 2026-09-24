for k in range(1000, 10000):
    k = str(k)
    s = sum(map(int, k))
    m = max(map(int, k))
    n = min(map(int, k))
    p1 = s - m
    p2 = s - n
    l = str(p1) + str(p2) if p1 <= p2 else str(p2) + str(p1)

    if int(l) == 1318: print(k)
