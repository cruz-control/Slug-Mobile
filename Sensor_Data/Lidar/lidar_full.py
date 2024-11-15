import signal
import sys
import struct
from hokuyolx import HokuyoLX

# Initialize the LIDAR
laser = HokuyoLX()

"""
Function to write LIDAR data to a .dat file.
- generator_func: A generator function like laser.iterdist()
- filename: Name of the .dat file to store data
"""
def write_lidar_to_dat(generator_func, filename):
    def signal_handler(sig, frame):
        print("\nInterrupted. Closing file and exiting.")
        sys.exit(0)
    
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal_handler)

    with open(filename, 'wb') as datfile:
        try:
            for timestamp, lidar_scan in generator_func():
                if len(lidar_scan) != 1081:
                    print(f"Warning: Expected 1081 elements, got {len(lidar_scan)}. Skipping this row.")
                    continue

                # Pack and write the timestamp and scan data into binary format
                datfile.write(struct.pack('d', timestamp))  # Write timestamp as double
                datfile.write(struct.pack(f'{len(lidar_scan)}f', *lidar_scan))  # Write scan distances as floats
        except KeyboardInterrupt:
            print("\nInterrupted. Closing file and exiting.")
        finally:
            datfile.close()
            print("File closed.")

"""
Substitute for laser.iterdist() for testing (generates fake data)
"""
def lidar_generator():
    import time
    import random
    while True:
        timestamp = time.time()  # Precise timestamp (seconds with microsecond precision)
        lidar_scan = [random.uniform(0, 100) for _ in range(1081)]  # Fake 1081 distance values
        yield timestamp, lidar_scan

if __name__ == "__main__":
    # Define filename with timestamp for the .dat file
    filename = f"lidar_output_{int(time.time())}.dat"

    # Start writing LIDAR data to the .dat file
    print(f"Recording LIDAR data to {filename}...")
    write_lidar_to_dat(laser.iterdist, filename)
