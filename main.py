import threading
import time
import os
import cv2
from slug_mobile import SlugMobile
from controller import XboxController
import pygame

# Initialize directories for outputs
os.makedirs("data", exist_ok=True)
os.makedirs("data/rgb", exist_ok=True)
os.makedirs("data/imu", exist_ok=True)
os.makedirs("data/lidar", exist_ok=True)
os.makedirs("data/controller", exist_ok=True)
os.makedirs("data/events", exist_ok=True)

def num_to_range(num, inMin, inMax, outMin, outMax):
    """Scale a number from one range to another."""
    return round(outMin + (float(num - inMin) / float(inMax - inMin) * (outMax - outMin)), 3)

class SensorThread(threading.Thread):
    def __init__(self, name, car, stop_event):
        super().__init__()
        self.car = car
        self.name = name
        self.stop_event = stop_event
        self.is_logging = False
    
    def run(self):
        pass

class ControllerThread(threading.Thread):
    def __init__(self, controller, car, stop_event):
        super().__init__()
        self.name = "ControllerThread"
        self.controller = controller
        self.car = car
        self.stop_event = stop_event
        self.is_logging = False
        
    
    def run(self):
        try:
            print("Controller thread started.")
            print("- Press START to start data collection.")
            print("- Press BACK to stop data collection.")
            print("- Press XBOX button to exit the program.")

            while not self.stop_event.is_set():
                self.controller.update()

                if self.controller.buttons[XboxController.Axis.A]:
                    if not self.is_logging:
                        print("Starting data collection.")
                        self.is_logging = True
                        self.controller.logging_enabled = True
                        for thread in threading.enumerate():
                            if isinstance(thread, SensorThread):
                                thread.is_logging = True
                    else:
                        print("Data collection already in progress.")
                elif self.controller.buttons[XboxController.Axis.B]:
                    if self.is_logging:
                        print("Stopping data collection.")
                        self.is_logging = False
                        self.controller.logging_enabled = False
                        for thread in threading.enumerate():
                            if isinstance(thread, SensorThread):
                                thread.is_logging = False
                    else:
                        print("Data collection already not in progress.")
                elif self.controller.buttons[XboxController.Axis.X]:
                    print("Exiting program.")
                    self.stop_event.set()
                    break
                print(f"Mapped throttle: {num_to_range(self.controller.get_throttle(), -4.1, 4.1, -1, 1)}, Mapped steering: {num_to_range(self.controller.get_steering(), -81, 81, 0, 180)}")
                self.car.set_steering_angle(num_to_range(self.controller.get_steering(), -81, 81, 0, 180))
                self.car.set_throttle(num_to_range(self.controller.get_throttle(), -4.1, 4.1, -1, 1))
                print(f"Actual throttle: {self.car.DrivingServo.throttle}, Actual steering angle: {self.car.SteeringServo.angle}")
        except Exception as e:
            print(f"Controller thread error: {e}")
        finally:
            self.controller.close()

class RGBCameraThread(SensorThread):
    def __init__(self, car, stop_event):
        super().__init__("RGBCameraThread", car, stop_event)
    
    def run(self):
        frame_filename = f"data/rgb/frame_{int(time.time())}.jpg"
        try:
            while not self.stop_event.is_set():
                frame = self.car.get_RGB()
                if frame:
                    cv2.imwrite(frame_filename, frame)
                time.sleep(1/self.car.camera_frequency)
        except Exception as e:
            print(f"RGB Camera thread error: {e}")

class IMUThread(SensorThread):
    def __init__(self, car, stop_event):
        super().__init__("IMUThread", car, stop_event)
    
    def run(self):
        csv_filename = f"data/imu/imu_data_{int(time.time())}.csv"
        try:
            while not self.stop_event.is_set():
                magn, gyro, accel = self.car.get_imu_data()
                with open(csv_filename, "a") as f:
                    f.write(f"{magn[0]}, {magn[1]}, {magn[2]}, {gyro[0]}, {gyro[1]}, {gyro[2]}, {accel[0]}, {accel[1]}, {accel[2]}\n")
        except Exception as e:
            print(f"IMU thread error: {e}")

class EventCameraThread(SensorThread):
    def __init__(self, car, stop_event):
        super().__init__("EventCameraThread", car, stop_event)
    
    def run(self):
        csv_filename = f"data/events/event_data_{int(time.time())}.csv"
        try:
            while not self.stop_event.is_set():
                x, y, p, t = self.car.get_event()
                with open(csv_filename, "a") as f:
                    f.write(f"{x}, {y}, {p}, {t}\n")
        except Exception as e:
            print(f"Event Camera thread error: {e}")

class LIDARThread(SensorThread):
    def __init__(self, car, stop_event):
        super().__init__("LIDARThread", car, stop_event)
    
    def run(self):
        csv_filename = f"data/lidar/lidar_data_{int(time.time())}.csv"
        try:
            while not self.stop_event.is_set():
                timestamp, scan = self.car.get_distance()
                with open(csv_filename, "a") as f:
                    f.write(f"{timestamp}, {scan}\n")
        except Exception as e:
            print(f"LIDAR thread error: {e}")

def main():
    car = SlugMobile()
    controller = XboxController()
    stop_event = threading.Event()
    
    try:
        while True:
            controller.update()
            print(f"Mapped throttle: {num_to_range(controller.get_throttle(), -4.1, 4.1, -1, 1)}, Mapped steering: {num_to_range(controller.get_steering(), -81, 81, 0, 180)}")
            car.set_steering_angle(num_to_range(controller.get_steering(), -car.max_steering, car.max_steering, 0, 180))
            car.set_throttle(num_to_range(controller.get_throttle(), -4.1, 4.1, -1, 1))
            print(f"Actual throttle: {car.DrivingServo.throttle}, Actual steering angle: {car.SteeringServo.angle}")
    except KeyboardInterrupt:
        print("Exiting program.")
        return

    # # Create threads for each sensor
    # threads = [
    #     ControllerThread(controller, car, stop_event),
    #     RGBCameraThread(car, stop_event),
    #     # IMUThread(car, stop_event),
    #     # LIDARThread(car, stop_event),
    #     EventCameraThread(car, stop_event)
    # ]

    # # Start all threads
    # for thread in threads:
    #     thread.start()

    # # Wait for all threads to complete
    # for thread in threads:
    #     thread.join()

if __name__ == "__main__":
    print("Starting multi-sensor data collection...")
    main()
    print("All sensors have completed data collection.")
