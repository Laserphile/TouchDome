import math
import argparse
import random
import time
from pythonosc import udp_client

coords=[[342, 548]]
#print(coords)
x=coords[0][0]
#print(x)
y=coords[0][1]
#print(y)

coords2=[800, 600]

coords.append(coords2)


ycenter = 1920/2
xcenter = 1080/2

y = y - ycenter
x = x - xcenter
#print("x, y:", x, y)
radians = math.atan2(y, x)
array = [math.hypot(y, x), math.degrees(radians)]
#print("radians", round(radians,2), "degrees", round(array[1],0), "distance:", round(array[0],0))

#we want to have an arbitrary number of radial slices. if it is in a certain section it should be sent to a different OSC server
control_count = 4 #how many different control segments
segment_size = 360/control_count


print(array)