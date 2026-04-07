from dataclasses import dataclass
from typing import List, Optional, Tuple

from hokuyolx import HokuyoLX


@dataclass
class LidarScan:

    #A simple container for one lidar reading.
    
    timestamp: int
    distances: List[int]
 

class HokuyoLidarSensor:

    #Modular wrapper for the Hokuyo lidar.
    
    def __init__(self):
        self._lidar: Optional[HokuyoLX] = None
        self._started = False

    def start(self):
        
        #Initialize the lidar hardware.
        #Call this once before reading data.
        
        if not self._started:
            self._lidar = HokuyoLX()
            self._started = True

    def read(self) -> LidarScan:

        #Read one scan from the lidar.
        #Returns a LidarScan object with timestamp + distance list.
        
        if not self._started or self._lidar is None:
            raise RuntimeError("Lidar not started. Call start() first.")

        timestamp, scan = self._lidar.get_dist()
        return LidarScan(timestamp=timestamp, distances=scan)

    def stop(self):

        #Clean up lidar if the library supports closing.
    
        if self._lidar is not None:
            close_method = getattr(self._lidar, "close", None)
            if callable(close_method):
                close_method()

        self._lidar = None
        self._started = False