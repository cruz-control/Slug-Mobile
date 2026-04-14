from node import Node
import time
from threading import Thread

nodes = [Node()]
update_rate = 50 # Hz

loop_time = 1/update_rate
stop = False

def run_thread(node):
    global stop, loop_time
    start = time.time()
    try:
      node.start()
    except Exception as e:
        stop = True
        raise e
    while not stop:
        try:
            node.update()
        except Exception as e:
            stop = True
            raise e
        end = time.time()
        if end - start < loop_time:
            time.sleep(loop_time - (end-start))
        start = end
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
