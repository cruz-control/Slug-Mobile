from dataclasses import dataclass
from typing import List, Optional, Tuple

from hokuyolx import HokuyoLX

from sensor import Sensor

import pubsub

@dataclass
class LidarFrame:
    timestamp: int
    distances: List[int]

class Lidar(Sensor):

    def __init__(self):
        super().__init__()
        self._lidar: HokuyoLX()
        self.start = False

    def start_lidar(self):
        self.start = True

    def get_frame(self) -> list:
        if not self.start:
            self.start_lidar()        
        
        timestamp, scan = self._lidar.get_dist()
        return [timestamp] + list(scan)
    
    def update(self):
        if not self.start:
            self.start_lidar()

        timestamp, scan = self._lidar.get_dist()
        pubsub.set_topic('lidar', LidarFrame(timestamp=timestamp, distances=list(scan)))
    
    def stop(self):
        self.start = False