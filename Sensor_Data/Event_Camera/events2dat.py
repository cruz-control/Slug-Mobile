from metavision_hal import DeviceDiscovery
from metavision_core.event_io import DatWriter
import time

def main():
    device = DeviceDiscovery.open("")
    width = device.get_i_geometry().get_width()
    height = device.get_i_geometry().get_height()
    
    # Output filename with timestamp
    filename = f"recording_{time.strftime('%Y%m%d_%H%M%S')}.dat"
    
    # Initialize DAT writer
    writer = DatWriter(filename, height=height, width=width)
    
    # Get CD (Change Detection) events from the camera
    i_events = device.get_i_events_stream()
    
    print(f"Recording to {filename}...")
    print("Press Ctrl+C to stop recording")
    
    try:
        while True:
            # Get next event buffer
            events = i_events.get_latest_raw_data()
            if events is not None:
                writer.write(events)
            
    except KeyboardInterrupt:
        print("\nStopping recording...")
    finally:
        writer.close()
        print("Recording finished!")

if __name__ == "__main__":
    main()
