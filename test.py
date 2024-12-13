import cv2
import depthai as dai
from openalpr import Alpr
import sys
import sqlite3
import serial
import time

arduino = serial.Serial('/dev/ttyUSB0', 115200)

def setup_database():
    """Sets up and populates the SQLite database."""
    conn = sqlite3.connect('plates.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plates (
            id INTEGER PRIMARY KEY,
            plate VARCHAR(10),
            description TEXT
        )
    ''')
    initial_plates = [
        ("AB12345", "Valid plate"),
        ("9JRI205", "Valid plate"),
	("ECE148", "Violated plate")
    ]
    cursor.execute('SELECT COUNT(*) FROM plates')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO plates (plate, description) VALUES (?, ?)', initial_plates)
    conn.commit()
    conn.close()

def check_plate(plate):
    """Checks if a recognized plate is in the database."""
    conn = sqlite3.connect('plates.db')
    cursor = conn.cursor()
    cursor.execute('SELECT plate, description FROM plates WHERE plate = ?', (plate,))
    result = cursor.fetchone()
    conn.close()
    return result

def main():
    setup_database()
    pipeline = dai.Pipeline()
    camRgb = pipeline.create(dai.node.ColorCamera)
    xoutRgb = pipeline.create(dai.node.XLinkOut)
    xoutRgb.setStreamName("rgb")
    camRgb.setPreviewSize(300, 300)
    camRgb.setInterleaved(False)
    camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
    camRgb.preview.link(xoutRgb.input)

    alpr = Alpr("us", "/home/jetson/openalpr/config/openalpr.defaults.conf", "/home/jetson/openalpr/runtime_data")
    if not alpr.is_loaded():
        print("Error loading OpenALPR")
        sys.exit(1)
    alpr.set_top_n(7)
    alpr.set_default_region("wa")
    alpr.set_detect_region(False)

    with dai.Device(pipeline) as device:
        print('Connected cameras:', device.getConnectedCameraFeatures())
        print('USB speed:', device.getUsbSpeed().name)
        qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        last_issued_plate = None

        while True:
            inRgb = qRgb.get()
            frame = inRgb.getCvFrame()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = alpr.recognize_ndarray(frame_rgb)

            highest_confidence = 0
            best_candidate = None

            for plate in results['results']:
                for candidate in plate['candidates']:
                    if candidate['confidence'] > highest_confidence:
                        highest_confidence = candidate['confidence']
                        best_candidate = candidate['plate']

            if best_candidate and best_candidate != last_issued_plate:
                plate_details = check_plate(best_candidate)
                
                if plate_details:
                    plate_number, description = plate_details
                    
                    if description == "Violated plate":
                        print(f"Ticket required: {plate_number}")
                        last_processed_plate = best_candidate
#                        inp = input("Sticker? Y/N:")
 #                       if (inp == 'Y'): 
                        arduino.write(f"18\n".encode())
		        #print(f"No ticket needed for: {plate_number}")
                    else:
			#print(f"Ticket required: {plate_number}")
                        #print(description)
                        print(f"No Ticket required: {plate_number}")
            
            cv2.imshow("Frame", frame)
            if cv2.waitKey(1) == ord('q'):
                break

if __name__ == "__main__":
    main()
 
