#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import math
from wigglecircle import wiggleCircle
from rect import rect
import helios

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

        frame.append(wiggleCircle(elapsed, timeFactor = 1.2,
         timeOffset = 2.0, numPoints = 500, baseRadius = 0.3,
         circleSpin = -0.1, blanks=2.0, waveSize = 0))

        rectX = math.sin(elapsed) * 0.3
        rectY = math.cos(elapsed) * 0.3
        frame.append(rect(rectX, rectY))

        boundingBox = rect(-1, -1, 2, 2)
        frame.append(boundingBox)

        statusAttempts = Helios.waitForDac()
        Helios.draw(frame)

        lastTime = curTime

except KeyboardInterrupt:
   exit(0)
