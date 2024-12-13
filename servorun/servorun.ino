#include <Servo.h>

Servo myServo;
int servoPin = 3;  // Pin connected to the servo control wire
int angle;

void setup() {
  myServo.attach(servoPin);  // Attach the servo to the pin
  Serial.begin(115200);  // Start serial communication at 9600 baud
  Serial.println("hi");
}

void loop() {
  if (Serial.available() > 0) {
    angle = Serial.parseInt();  // Read the integer from the serial input
    if (angle >= 0 && angle <= 180) {
      myServo.write(angle);  // Move the servo to the specified angle
    }
  }
}
