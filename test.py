#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Example for using Helios DAC libraries in python (using C library with ctypes)

NB: If you haven't set up udev rules you need to use sudo to run the program for it to detect the DAC.
"""

import ctypes
import math
import time

#Define point structure
class HeliosPoint(ctypes.Structure):
    #_pack_=1
    _fields_ = [('x', ctypes.c_uint16),
                ('y', ctypes.c_uint16),
                ('r', ctypes.c_uint8),
                ('g', ctypes.c_uint8),
                ('b', ctypes.c_uint8),
                ('i', ctypes.c_uint8)]

#Load and initialize library
HeliosLib = ctypes.cdll.LoadLibrary("./libHeliosDacAPI.so")

# These can be used in frameMode
HELIOS_FLAGS_START_IMMEDIATELY = 1
HELIOS_FLAGS_SINGLE_MODE = 2
HELIOS_FLAGS_DONT_BLOCK = 4

HELIOS_MAX_POINTS = 0x1000

deviceNum = 0
pps = 20000
pointCount = 500

xyMax = 0xFFF
xyHalf = xyMax / 2

msgOutputInterval = 100

class HeliosDAC:
    def __init__(self):
        numDevices = HeliosLib.OpenDevices()

        if numDevices == 0:
           print("No DAC found")
           exit(1)

        self.deviceNum = 0
        self.lastPoint = Point(0, 0, 0)

    def getFrame(self):
        return Frame(self.lastPoint)


    def draw(self, frame):
        points = frame.points
        numPoints = len(points)

        # TODO: Color delay
        # TODO: Take the second slice and use it?
        if numPoints > HELIOS_MAX_POINTS:
            #print("TOO MANY POINTS:", numPoints)
            numPoints = HELIOS_MAX_POINTS
            points = points[:HELIOS_MAX_POINTS]

        frameType = HeliosPoint * numPoints
        frame = frameType();

        frameMode = 0

        for i in range(numPoints):
            frame[i] = points[i].getHeliosPoint()

        HeliosLib.WriteFrame(self.deviceNum, pps, frameMode, ctypes.pointer(frame), numPoints) #Send the frame

    def waitForDac(self):
        statusAttempts = 0

        waitStart = time.time()
        # Make 512 attempts for DAC status to be ready. After that, just give up and try to write the frame anyway
        while (statusAttempts < 512 and HeliosLib.GetStatus(self.deviceNum) != 1):
            statusAttempts += 1
            # print("Frame", i, "StatusAttempts", statusAttempts)

        waitTime = time.time() - waitStart

        if (statusAttempts >= 512):
            print("ERROR: waiting a long time for DAC.", statusAttempts, "attempts in", waitTime, "seconds")
        
        attemptCounts.append(statusAttempts)
        waitTimes.append(waitTime)

        return statusAttempts


class Point:
    def __init__(self, x, y, r = 1):
        self.x = x
        self.y = y
        self.r = r
    
    def getHeliosPoint(self):
        intx = int(max(0, min(xyMax, round(self.x * xyHalf)+xyHalf)))
        inty = int(max(0, min(xyMax, round(self.y * xyHalf)+xyHalf)))

        brightness = int(max(0, min(0xFF, self.r * 0xFF)))
        return HeliosPoint(intx,inty,brightness,brightness,brightness, 0xFF)

class Frame:
    def __init__(self, firstPoint):
        self.points = [firstPoint]
    
    def append(self, newPoints, blankGap = 5, dwellStart = 1, dwellEnd = 1):
        if len(newPoints) == 0:
            return

        if len(self.points) > 0 and blankGap > 0:
            lastPoint = self.points[-1]
            nextPoint = newPoints[0]
            self.blankSlirp(lastPoint, nextPoint, blankGap)

        for i in range(dwellStart):
            self.points.append(newPoints[0])

        self.points.extend(newPoints)

        for i in range(dwellEnd):
            self.points.append(newPoints[-1])

    def blankSlirp(self, p1, p2, numBlanks):
        for i in range(numBlanks):
            f1 = (i + 0.5) / float(numBlanks)
            f2 = 1 - f1
            x = (p1.x * f1) + (p2.x * f2)
            y = (p1.y * f1) + (p2.y * f2)
            self.points.append(Point(x, y, 0))

    def appendBlanks(self, numBlanks = 100):
        for i in range(numBlanks):
            self.points.append(Point(0, 0, 0))

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

attemptCounts = []
waitTimes = []


timeSteps = []

Helios = HeliosDAC()

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
             "Attempts", sum(attemptCounts)/float(len(attemptCounts)), \
             "waitTimes", sum(waitTimes)/float(len(waitTimes))
            attemptCounts = []
            waitTimes = []
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
   HeliosLib.CloseDevices()

HeliosLib.CloseDevices()
