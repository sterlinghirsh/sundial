from helios import Point

def slirp(p1, p2, num = 1, r = None):
    if r is None:
        r = p1.r

    out = []
    for i in range(num):
        f2 = i / float(num)
        f1 = 1 - f2
        x = (p1.x * f1) + (p2.x * f2)
        y = (p1.y * f1) + (p2.y * f2)
        out.append(Point(x, y, r))

    return out

def dwell(p, num):
    return [p for i in range(num)]

def rect(x1 = 0, y1 = 0, width = 0.2, height = 0.2, sidePoints = 20):
    out = []

    p1 = Point(x1, y1)
    p2 = Point(x1 + width, y1)
    p3 = Point(x1 + width, y1 + height)
    p4 = Point(x1, y1 + height)

    dwellNum = 3
    out.extend(dwell(p1, dwellNum))
    out.extend(slirp(p1, p2, sidePoints))
    out.extend(dwell(p2, dwellNum))
    out.extend(slirp(p2, p3, sidePoints))
    out.extend(dwell(p3, dwellNum))
    out.extend(slirp(p3, p4, sidePoints))
    out.extend(dwell(p4, dwellNum))
    out.extend(slirp(p4, p1, sidePoints))
    out.extend(dwell(p1, dwellNum))

    return out

