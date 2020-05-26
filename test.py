#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import math
from wigglecircle import wiggleCircle
from rect import rect
import helios
from helios import Point

import matplotlib.image as mpimg

img = mpimg.imread('clementine.png')

def image(rowNum, scaleX = 1.0, scaleY = 1.0,
 colorMin = 0.2, colorMax = 1.0,
 xSkipRatio = 1.0, ySkipRatio = 1.0,
 brightnessDwell = 1):
   h = len(img)
   w = len(img[0])
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


msgOutputInterval = 100

timeSteps = []

Helios = helios.DAC()

try:
    """
    stats = {
        'frameNum': 0,
        'startTime': time.time(),
        'lastTime': time.time(),
        'curTime': time.time(),
        'timeStep': 0.01,
        '
        """
    frameNum = 0
    startTime = time.time()
    lastTime = startTime
    while True:
        curTime = time.time()
        timeStep = curTime - lastTime
        timeSteps.append(timeStep)
        elapsed = curTime - startTime
        frameNum += 1
        fps = 1/timeStep

        if frameNum % msgOutputInterval == 0:
            print "\rFrame", frameNum, "Elapsed", elapsed, \
             "Time Step", timeStep, "Fps", fps, \
             "Fps Avg", float(len(timeSteps))/float(sum(timeSteps)), \
             "Attempts", sum(Helios.attemptCounts)/float(len(Helios.attemptCounts)), \
             "waitTimes", sum(Helios.waitTimes)/float(len(Helios.waitTimes))
            Helios.attemptCounts = []
            Helios.waitTimes = []
            timeSteps = []

        frame = Helios.getFrame()

        #frame.append(wiggleCircle(elapsed))

        #frame.append(wiggleCircle(elapsed, timeFactor = 1.2,
        # timeOffset = 2.0, numPoints = 500, baseRadius = 0.3,
        # circleSpin = -0.1, blanks=2.0, waveSize = 0))

        #rectX = math.sin(elapsed) * 0.3
        #rectY = math.cos(elapsed) * 0.3
        #frame.append(rect(rectX, rectY))

        boundingBox = rect(-1, -1, 2, 2)

        frame.append(image(frameNum, scaleX = 1.0, scaleY = 1.0,
         ySkipRatio = 4.0, xSkipRatio = 2.0, brightnessDwell = 8),
         blankGap = 0, dwellStart = 0, dwellEnd = 0)

        frame.append(boundingBox)

        statusAttempts = Helios.waitForDac()
        Helios.draw(frame)

        lastTime = curTime

except KeyboardInterrupt:
   exit(0)
