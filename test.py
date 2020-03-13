#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import time
from wigglecircle import wiggleCircle
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
        frame.append(wiggleCircle(elapsed))
        frame.append(wiggleCircle(elapsed, timeFactor = 1.2, timeOffset = 2.0, numPoints = 50, baseRadius = 0.3, circleSpin = -0.1))
        frame.append(wiggleCircle(elapsed, offsetxFactor = 0.5, offsetyFactor = 0.8, circleSpin = -0.3), blankGap = 10)
        frame.append(wiggleCircle(elapsed, timeFactor = 2, timeOffset = 4.0, numPoints = 50, baseRadius = 0.3, waveSize = 0, blanks = 0))
        frame.append(wiggleCircle(elapsed, timeFactor = 1.2, timeOffset = 4.0, numPoints = 50, baseRadius = 0.3, waveSize = 0, blanks = 0), blankGap = 10)
        frame.append(wiggleCircle(elapsed, timeFactor = 1.3, timeOffset = 4.0, numPoints = 50, baseRadius = 0.3, waveSize = 0, blanks = 0), blankGap = 10)
        frame.append(wiggleCircle(elapsed, timeFactor = 1.4, timeOffset = 4.0, numPoints = 50, baseRadius = 0.3, waveSize = 0, blanks = 0), blankGap = 10)
        frame.append(wiggleCircle(elapsed, timeFactor = 1.5, timeOffset = 4.0, numPoints = 50, baseRadius = 0.3, waveSize = 0, blanks = 0), blankGap = 10)
        frame.append(wiggleCircle(elapsed, timeFactor = 1.6, timeOffset = 4.0, numPoints = 50, baseRadius = 0.3, waveSize = 0, blanks = 0), blankGap = 10)
        frame.append(wiggleCircle(elapsed, timeFactor = 1.7, timeOffset = 4.0, numPoints = 50, baseRadius = 0.3, waveSize = 0, blanks = 0), blankGap = 10)

        statusAttempts = Helios.waitForDac()
        Helios.draw(frame)

        lastTime = curTime

except KeyboardInterrupt:
   exit(0)
