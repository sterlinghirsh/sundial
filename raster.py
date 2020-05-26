from helios import Point

import matplotlib.image as mpimg
import math

img = mpimg.imread('clementine.png')

class Raster:
   def __init__(self, filename):
      self.filename = filename
      self.pixels = mpimg.imread(filename)
      self.h = len(self.pixels)
      self.w = len(self.pixels[0])

   def getPoints(self, rowNum, scaleX = 1.0, scaleY = 1.0,
    colorMin = 0.2, colorMax = 1.0,
    xSkipRatio = 1.0, ySkipRatio = 1.0,
    brightnessDwell = 1):
      h = self.h
      w = self.w
      out = []

      rowNumPostSkip = int(rowNum * ySkipRatio)
      invertYOrder = int(rowNumPostSkip / h) % 2 == 0
      y = rowNumPostSkip % h

      if invertYOrder:
         y = -1 + h - y
         y = int(min(h-1, y + ySkipRatio / 2.0))

      row = img[-y]

      xOrder = range(int(w / xSkipRatio))
      #if rowNum % 2 == 1:
      #   xOrder = reversed(xOrder)

      aspectRatio = h / float(w)

      if h > w:
         scaleX *= (1 / aspectRatio)
      else :
         scaleY *= aspectRatio

      colorRange = colorMax - colorMin
      colorExpansion = 1/float(colorRange) if colorRange != 0 else 1


      #for x in range(w):
      for x in xOrder:
         x = int(x * xSkipRatio)
         xf = scaleX * ((x / float(w)) - 0.5)
         yf = scaleY * ((y / float(h)) - 0.5)

         pixel = row[x]
         color = (pixel[0] + pixel[1] + pixel[2]) / 3.0

         color -= colorMin
         color *= colorExpansion

         color = math.ceil(color * brightnessDwell)

         if color < 2:
            out.append(Point(xf, yf, 0))
         if color < 1:
            out.append(Point(xf, yf, 0))
            out.append(Point(xf, yf, 0))

         while color >= 1:
            out.append(Point(xf, yf, 1))
            color -= 1

      return out

