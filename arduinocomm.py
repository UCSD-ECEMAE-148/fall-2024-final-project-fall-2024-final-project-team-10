import serial
import time

arduino = serial.Serial('/dev/ttyUSB0', 115200)

time.sleep(2)

def move_servo(angle):
	if 0 <= angle <= 180:
		arduino.write(f"{angle}\n".encode())
		print(f"moving servo to {angle} degrees")
	else:
		print("not between 0 and 180")

try:

	angle = 18
	move_servo(angle)
except KeyboardInterrupt:
	print("Program interrupted")
finally:
	arduino.close()
