import cv2
import time
import os

# Create folders for color and grayscale frames
os.makedirs("color_frames", exist_ok=True)
os.makedirs("gray_frames", exist_ok=True)

# Initialize the camera
cap = cv2.VideoCapture(0)

# Check if the camera is opened successfully
if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

print("Press 'q' to stop recording...")

while True:
    ret, frame = cap.read()  # Capture a frame
    if not ret:
        print("Error: Could not read frame.")
        break

    # Get the current timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S_%f")  # Format: YYYYMMDD_HHMMSS_microseconds

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Save the color frame with a timestamp in the "color_frames" folder
    color_filename = os.path.join("color_frames", f"color_{timestamp}.jpg")
    cv2.imwrite(color_filename, frame)

    # Save the grayscale frame with a timestamp in the "gray_frames" folder
    gray_filename = os.path.join("gray_frames", f"gray_{timestamp}.jpg")
    cv2.imwrite(gray_filename, gray)

    # Display the frames
    cv2.imshow('Color Frame', frame)
    cv2.imshow('Grayscale Frame', gray)

    # Stop recording when 'q' is pressed
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

# Release the camera and close windows
cap.release()
cv2.destroyAllWindows()
