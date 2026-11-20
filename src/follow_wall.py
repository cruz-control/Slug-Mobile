import math

from node import Node
from pid import PID

class FollowWall (Node):
    def __init__(self):
        super().__init__()
        self.distPID = PID(0.2, 0, 0)
        self.anglePID = PID(0.1, 0, 0)
    
    def start(self):
        self.distPID.reset()
        self.anglePID.reset()
        self.set_topic("motors/drive", 0)
        self.set_topic("motors/steer", 0)

    def update(self):
        self.set_topic("motors/drive", 0.1)

        angles = self.get_topic("lidar/angles")
        scan = self.get_topic("lidar/distances")
        points = [(scan[i] * math.cos(angles[i]) / 1000, scan[i] * math.sin(angles[i]) / 1000) for i in range(len(angles))]
        closestPoint = points[0]
        closestDist = math.hypot(closestPoint[0], closestPoint[1])
        for point in points[1:2*len(points)//3]:
            dist = math.hypot(point[0], point[1])
            if dist < closestDist:
                closestPoint = point
                closestDist = dist
            
        angle = math.atan2(closestPoint[1], closestPoint[0])
        distSetpoint = 0.3
        angleSetpoint = math.pi / 2
        steer = self.anglePID.calculate(angleSetpoint - angle) + self.distPID.calculate(distSetpoint - closestDist)
        self.set_topic("motors/steer", math.min(math.max(steer, -1), 1))

    def stop(self):
        pass