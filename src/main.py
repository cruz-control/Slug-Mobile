from node import Node
from controller import Controller
from motors import Motors
from rgb import RGB
from imu import IMU
from lidar import Lidar
import time
from threading import Thread, Lock
from logger_node import CSVLoggerNode, ImageLoggerNode, VideoLoggerNode
import os
from pathlib import Path

# Change the working directory so that logs are in the right folders
parent_dir = Path(__file__).resolve().parent.parent
os.chdir(parent_dir)

# Create the list of nodes
# Some are stored as class references to allow errors in the constructor to be caught
nodes = [Controller, Motors, RGB, Lidar, IMU,
    VideoLoggerNode("rgb/frame", "log/video.avi"), ImageLoggerNode("rgb/frame", "log/images"),
    CSVLoggerNode("lidar/distances", "log/lidar_log.csv"),
    CSVLoggerNode(["imu/accel", "imu/gyro", "imu/mag", "imu/temp"], "log/imu_log.csv"),
    CSVLoggerNode(["controller/" + x for x in Controller.get_axes() + Controller.get_buttons()], "log/controller_log.csv")
]
update_rate = 50 # Hz

loop_time = 1.0/update_rate
stop = False
initializing = len(nodes)
initializing_lock = Lock()

def run_thread(node_class):
    global stop, loop_time, initializing
    initialized = False
    node = None
    name = "Unknown"

    try:
        # Detect if it is a class or object
        if isinstance(node_class, type):
            name = node_class.__name__
            node = node_class()
        else:
            name = node_class.__class__.__name__
            node = node_class
        
        # Start the node
        node.start()
        with initializing_lock:
            initializing -= 1
        initialized = True

        # Wait for all nodes to start
        while initializing > 0 and not stop:
            time.sleep(loop_time)
        
        # Update this node repeatedly
        start = time.monotonic()
        while not stop:
            node.update()
            end = time.monotonic()

            # Sleep to keep a constant update rate
            if end - start < loop_time:
                time.sleep(loop_time - (end-start))
                end = start + loop_time
            else:
                time.sleep(0)
            start = end
    except Exception as e:
        # Allow other nodes to update if this node failed to initialize
        if not initialized:
            with initializing_lock:
                initializing -= 1
            print(f'Error initializing {name}: {e}')
        else:
            print(f'Error in {name}: {e}')
    
    # Stop the node
    try:
        if node is not None:
            node.stop()
    except Exception as e:
        print(f'Error stopping {name}: {e}')

threads = []
for n in nodes:
    threads.append(Thread(target=run_thread, args=(n,)))

def main():
    global stop
    for t in threads:
        t.start()
    while not stop:
        try:
            time.sleep(0.5)
        except KeyboardInterrupt:
            print()
            stop = True
        except Exception as e:
            print(f'Error in main loop: {e}')
            stop = True
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
