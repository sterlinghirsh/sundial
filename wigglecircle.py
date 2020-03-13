import math
from helios import Point

def wiggleCircle(elapsed, timeFactor = 1.0, timeOffset = 0.0, numPoints = 200, stretch = 0.2, wobble = 0.2,
     offsetxFactor = 0.2, offsetyFactor = 0.3, stretchxFactor = 0.5, stretchyFactor = 0.7,
     baseRadius = 0.5, blanks = 5.0, circleSpin = 0.3, waveSpin = -0.7,
     waveSize = 0.1, circleBumps = 16.0, blankChangeSpeed = 1.0, blankThreshold = 0.3):
    rads = math.pi * 2.0

    elapsed += timeOffset
    elapsed *= timeFactor

    offsetx = math.cos(rads * elapsed * offsetxFactor) * wobble
    offsety = math.sin(rads * elapsed * offsetyFactor) * wobble
    stretchx = (math.cos(rads * elapsed * stretchxFactor) * stretch) + 1.0
    stretchy = (math.sin(rads * elapsed * stretchyFactor) * stretch) + 1.0

    out = []

    for j in range(numPoints + 1):
        position = float(j)/float(numPoints)
        # print j, position

        angle = (position + (elapsed * circleSpin)) * rads

        radius = baseRadius + math.sin((waveSpin * elapsed * rads) + (position * rads * circleBumps)) * waveSize
        x = stretchx * radius * math.sin(angle) + offsetx
        y = stretchy * radius * math.cos(angle) + offsety

        on = 1 if math.cos(blanks * position * rads) > blankThreshold else 0
        out.append(Point(x, y, on))

    return out
