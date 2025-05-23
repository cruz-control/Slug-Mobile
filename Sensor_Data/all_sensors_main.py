import threading
import time
import os
from camera2JPEG import save_camera_frames
from controller_full import ControllerInputLogger
from imu2csv import log_imu_data
from events2dat import record_event_camera_data
from lidarfull import write_lidar_to_dat, lidar_generator
from hokuyolx import HokuyoLX

# Initialize directories for outputs
os.makedirs("data", exist_ok=True)
os.makedirs("data/color_frames", exist_ok=True)
os.makedirs("data/gray_frames", exist_ok=True)
os.makedirs("data/imu", exist_ok=True)
os.makedirs("data/lidar", exist_ok=True)
os.makedirs("data/controller", exist_ok=True)
os.makedirs("data/event_camera", exist_ok=True)

def run_camera():
    """Run the camera script to save color and grayscale frames."""
    try:
        save_camera_frames(output_dir="data/color_frames", gray_dir="data/gray_frames")
    except Exception as e:
        print(f"Camera thread error: {e}")

def run_controller():
    """Run the controller script to log inputs."""
    try:
        controller_logger = ControllerInputLogger(output_dir="data/controller")
        controller_logger.start_logging()
    except Exception as e:
        print(f"Controller thread error: {e}")

def run_imu():
    """Run the IMU script to log data to CSV."""
    try:
        log_imu_data(output_file="data/imu/imu_data.csv")
    except Exception as e:
        print(f"IMU thread error: {e}")

def run_event_camera():
    """Run the event camera script to log data to .dat."""
    try:
        record_event_camera_data(output_file="data/event_camera/event_camera_data.dat")
    except Exception as e:
        print(f"Event Camera thread error: {e}")

def run_lidar():
    """Run the LIDAR script to log data to .dat."""
    try:
        lidar = HokuyoLX()
        lidar_filename = f"data/lidar/lidar_output_{int(time.time())}.dat"
        write_lidar_to_dat(lidar.iterdist, lidar_filename)
    except Exception as e:
        print(f"LIDAR thread error: {e}")

def main():
    """Main function to run all scripts simultaneously."""
    # Create threads for each sensor
    threads = [
        threading.Thread(target=run_camera, name="CameraThread"),
        threading.Thread(target=run_controller, name="ControllerThread"),
        threading.Thread(target=run_imu, name="IMUThread"),
        threading.Thread(target=run_event_camera, name="EventCameraThread"),
        threading.Thread(target=run_lidar, name="LIDARThread"),
    ]

    # Start all threads
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    print("Starting multi-sensor data collection...")
    main()
    print("All sensors have completed data collection.")
