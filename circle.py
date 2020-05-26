import math
from helios import Point

def circle(x = 0.0, y = 0.0, r = 1.0, numPoints = 200):
   if numPoints < 2:
      return []

   out = []

   for j in range(numPoints):
      angle = math.pi * 2.0 * float(j)/float(numPoints - 1)
      x1 = r * math.sin(angle) + x
      y1 = r * math.cos(angle) + y
      out.append(Point(x1, y1, 1))
   return out
