# Set up Raspberry Pi

# sudo apt-get update
# sudo apt-get install python3-rpi.gpio

from flask import Flask, render_template, request
import time
import RPi.GPIO as GPIO
import cv2

# Initialize Flask app
app = Flask(__name__)

# Set up the GPIO pins for the motor driver
GPIO.setmode(GPIO.BCM)

# Pin configuration
motor_pins = {
    'left1': {'dir1': 5, 'dir2': 6, 'pwm': 13},  # Left motor 1
    'left2': {'dir1': 17, 'dir2': 27, 'pwm': 22},  # Left motor 2
    'right1': {'dir1': 11, 'dir2': 9, 'pwm': 10},  # Right motor 1
    'right2': {'dir1': 4, 'dir2': 3, 'pwm': 2},  # Right motor 2
}
servo_pins = {'x_axis': 19, 'y_axis': 26}  # GPIO pins for servo control

# Initialize all motor pins
for motor in motor_pins.values():
    GPIO.setup(motor['dir1'], GPIO.OUT)
    GPIO.setup(motor['dir2'], GPIO.OUT)
    GPIO.setup(motor['pwm'], GPIO.OUT)
    motor['pwm_instance'] = GPIO.PWM(motor['pwm'], 1000)  # Set PWM frequency to 1kHz
    motor['pwm_instance'].start(0)  # Start with motor

# Set up servo pins
for servo in servo_pins.values():
    GPIO.setup(servo, GPIO.OUT)

# Create PWM instances for servos
servo_pwm = {
    axis: GPIO.PWM(pin, 50)  # 50Hz for servo control
    for axis, pin in servo_pins.items()
}

# Start servos at 0 degrees (mid-range for most servos)
for pwm in servo_pwm.values():
    pwm.start(7.5)  # 7.5% duty cycle represents the center position



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/move", methods=["POST"])
def move_route():
    direction = request.form.get("direction")
    if direction:
        move(direction, 100)
    return "OK"

@app.route("/capture", methods=["POST"])
def capture_route():
    capture_image()
    return "Image Captured"

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000)
    finally:
        print("WeedBot Shutting Down...\nRoBros, Inc.")