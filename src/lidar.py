from typing import List, Optional, Tuple

from hokuyolx import HokuyoLX

from node import Node

from pubsub import set_topic

class Lidar(Node):
    def __init__(self):
        super().__init__()
        self.lidar = HokuyoLX()

    def start(self):
        angles = self.lidar.get_angles()
        set_topic("lidar/timestamp", -1)
        set_topic("lidar/distances", [])
        set_topic("lidar/angles", list(angles))
        
    def update(self):
        timestamp, scan = self.lidar.get_dist()
        set_topic('lidar/timestamp', timestamp)
        set_topic('lidar/distances', list(scan))
    
    def stop(self):
        pass