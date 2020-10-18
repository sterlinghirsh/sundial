from helios import Point
from rect import slirp, dwell
from circle import circle
import math
from datetime import datetime 


class Clock:
   def __init__(self):
      self.x = 0
      self.y = 0
      self.r = 1.0

   def getHand(self, timeValue, maxTimeValue, rFactor):
      out = []
      dwellNum = 3
      angle = timeValue * 2.0 * math.pi / float(maxTimeValue)
      x1 = rFactor * self.r * math.sin(angle) + self.x;
      y1 = rFactor * self.r * math.cos(angle) + self.y;
      center = Point(self.x, self.y)
      hand = Point(x1, y1)
      out.extend(dwell(center, dwellNum))
      out.extend(slirp(center, hand, 10))
      out.extend(dwell(hand, dwellNum))
      out.extend(slirp(hand, center, 10))
      out.extend(dwell(center, dwellNum))

      return out
      

   def getPoints(self, curTime):
      t = datetime.now()
      out = []

      center = Point(self.x, self.y)
      circ = circle(self.x, self.y, self.r, 50)
      circleStart = circ[0]
      
      out.extend(circ)
      out.extend(dwell(circleStart, 4))
      out.extend(dwell(circleStart.withColor(0), 6))
      out.extend(slirp(circleStart, center, 10, 0))

      second = t.second + (t.microsecond / 1000000.0)
      minute = t.minute + (second / 60.0)
      hour = t.hour + (minute / 60.0)
      #print "hms", hour, minute, second 

      out.extend(dwell(center.withColor(0), 6))
      out.extend(self.getHand(second, 60, .9))
      out.extend(self.getHand(minute, 60, .75))
      out.extend(self.getHand(hour, 12, .5))

      out.extend(slirp(center, circleStart, 10, 0))
      out.extend(dwell(circleStart.withColor(0), 3))


      return out
