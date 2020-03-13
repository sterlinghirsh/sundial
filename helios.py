# -*- coding: utf-8 -*-
"""
NB: If you haven't set up udev rules you need to use sudo to run the program for it to detect the DAC.
"""

import ctypes
import time

import Queue

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

xyMax = 0xFFF
xyHalf = xyMax / 2

class DAC:
    def __init__(self):
        numDevices = HeliosLib.OpenDevices()

        if numDevices == 0:
           print("No DAC found")
           exit(1)

        self.deviceNum = 0
        self.lastPoint = Point(0, 0, 0)

        self.attemptCounts = []
        self.waitTimes = []

        self.colorDelay = 0
        self.xDelay = self.yDelay = 0

        self.delayedColors = Queue.Queue()
        while self.delayedColors.qsize() < self.colorDelay:
            self.delayedColors.put(0)

        self.delayedX = Queue.Queue()
        while self.delayedX.qsize() < self.xDelay:
            self.delayedX.put(0)

        self.delayedY = Queue.Queue()
        while self.delayedY.qsize() < self.yDelay:
            self.delayedY.put(0)
    
    def __del__(self):
        HeliosLib.CloseDevices()

    def getFrame(self):
        return Frame(self.lastPoint)

    def delayColors(self, points):
        numPoints = len(points)
        for i in range(numPoints):
            self.delayedX.put(points[i].x)
            self.delayedY.put(points[i].y)
            self.delayedColors.put(points[i].r)
            points[i].x = self.delayedX.get()
            points[i].y = self.delayedY.get()
            points[i].r = self.delayedColors.get()

    def draw(self, frame):
        points = frame.points
        numPoints = len(points)

        # TODO: Color delay
        # TODO: Take the second slice and use it?
        if numPoints > HELIOS_MAX_POINTS:
            #print("TOO MANY POINTS:", numPoints)
            numPoints = HELIOS_MAX_POINTS
            points = points[:HELIOS_MAX_POINTS]

        #self.delayColors(points)

        self.lastPoint = points[-1]

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
        
        self.attemptCounts.append(statusAttempts)
        self.waitTimes.append(waitTime)

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

    def withColor(self, r):
        return Point(self.x, self.y, r)

class Frame:
    def __init__(self, firstPoint):
        self.points = [firstPoint]
    
    def append(self, newPoints, blankGap = 5, dwellStart = 3, dwellEnd = 3):
        if len(newPoints) == 0:
            return

        if len(self.points) > 0 and blankGap > 0:
            lastPoint = self.points[-1]
            nextPoint = newPoints[0]
            self.blankSlirp(lastPoint, nextPoint, blankGap)

        for i in range(dwellStart):
            self.points.append(newPoints[0].withColor(0))
        for i in range(dwellStart):
            self.points.append(newPoints[0].withColor(1))

        self.points.extend(newPoints)

        for i in range(dwellEnd):
            self.points.append(newPoints[-1].withColor(1))
        for i in range(dwellEnd):
            self.points.append(newPoints[-1].withColor(0))

    def blankSlirp(self, p1, p2, numBlanks):
        for i in range(numBlanks):
            f2 = (i + 0.5) / float(numBlanks)
            f1 = 1 - f2
            x = (p1.x * f1) + (p2.x * f2)
            y = (p1.y * f1) + (p2.y * f2)
            self.points.append(Point(x, y, 0))

    def appendBlanks(self, numBlanks = 100):
        for i in range(numBlanks):
            self.points.append(Point(0, 0, 0))
