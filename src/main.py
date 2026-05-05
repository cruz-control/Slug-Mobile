from node import Node
from controller import Controller
from motors import Motors
from rgb import RGB
from imu import IMU
from lidar import Lidar
import time
from threading import Thread

nodes = [Controller(), Motors(), RGB(), Lidar(), IMU()]
update_rate = 50 # Hz

loop_time = 1/update_rate
stop = False
initializing = len(nodes)

def run_thread(node):
    global stop, loop_time, initializing
    start = time.time()
    try:
        node.start()
        initializing -= 1
        while initializing > 0 and not stop:
            time.sleep(loop_time)
        while not stop:
            node.update()
            end = time.time()
            if end - start < loop_time:
                time.sleep(loop_time - (end-start))
            start = end
    except Exception as e:
      try:
        node.stop()
      except:
        pass
      raise e
    node.stop()

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
        except:
            print()
            stop = True
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
