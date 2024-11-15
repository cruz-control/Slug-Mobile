import csv
import time
from BMX160 import BMX160

bmx = BMX160(1)

# Wait for sensor initialization
while not bmx.begin():
    time.sleep(2)

def main():
    # Open CSV file for writing
    with open("imu_data.csv", "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write header
        csv_writer.writerow(["timestamp", "magn_x", "magn_y", "magn_z",
                             "gyro_x", "gyro_y", "gyro_z",
                             "accel_x", "accel_y", "accel_z"])
        
        while True:
            try:
                # Get sensor data
                data = bmx.get_all_data()
                timestamp = time.time()
                
                # Write row to CSV
                csv_writer.writerow([timestamp, *data])
                csvfile.flush()  # Ensure data is written immediately
                
                # Print data to console for verification
                print("magn: x: {0:.2f} uT, y: {1:.2f} uT, z: {2:.2f} uT".format(data[0], data[1], data[2]))
                print("gyro  x: {0:.2f} g, y: {1:.2f} g, z: {2:.2f} g".format(data[3], data[4], data[5]))
                print("accel x: {0:.2f} m/s^2, y: {1:.2f} m/s^2, z: {2:.2f} m/s^2".format(data[6], data[7], data[8]))
                print(" ")

                # Delay for data collection rate
                time.sleep(1)

            except KeyboardInterrupt:
                print("Recording stopped by user.")
                break

if __name__ == "__main__":
    main()
