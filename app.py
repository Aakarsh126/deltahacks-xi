# Set up Raspberry Pi

# sudo apt-get update
# sudo apt-get install python3-rpi.gpio

from flask import Flask, render_template, request, jsonify
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

def set_motor(motor, direction, speed):
    """
    Control individual motors.
    direction: "forward" or "backward"
    speed: 0 to 100 (PWM duty cycle percentage)
    """
    if direction == "forward":
        GPIO.output(motor['dir1'], GPIO.HIGH)
        GPIO.output(motor['dir2'], GPIO.LOW)
    elif direction == "backward":
        GPIO.output(motor['dir1'], GPIO.LOW)
        GPIO.output(motor['dir2'], GPIO.HIGH)
    
    # Set speed using PWM
    motor['pwm_instance'].ChangeDutyCycle(speed)

def move(direction, speed=50):
    """
    Control all motors to move the robot in a specified direction.
    direction: "forward", "backward", "left", "right", "nothing"
    speed: 0 to 100 (default 50)
    """
    if direction == "forward":
        for motor_name in ['left1', 'left2', 'right1', 'right2']:
            set_motor(motor_pins[motor_name], "forward", speed)
    
    elif direction == "backward":
        for motor_name in ['left1', 'left2', 'right1', 'right2']:
            set_motor(motor_pins[motor_name], "backward", speed)
    
    elif direction == "left":
        for motor_name in ['left1', 'left2']:
            set_motor(motor_pins[motor_name], "backward", speed)
        for motor_name in ['right1', 'right2']:
            set_motor(motor_pins[motor_name], "forward", speed)
    
    elif direction == "right":
        for motor_name in ['left1', 'left2']:
            set_motor(motor_pins[motor_name], "forward", speed)
        for motor_name in ['right1', 'right2']:
            set_motor(motor_pins[motor_name], "backward", speed)
    
    elif direction == "nothing":
        for motor_name in motor_pins.keys():
            set_motor(motor_pins[motor_name], "forward", 0)  # Stop all motors

def set_servo_position(axis, angle):
    """
    Set the servo position.
    axis: "x_axis" or "y_axis"
    angle: 0 to 180 (convert to appropriate duty cycle)
    """
    duty_cycle = 2.5 + (angle / 180) * 10  # Convert angle to duty cycle (2.5 to 12.5)
    servo_pwm[axis].ChangeDutyCycle(duty_cycle)
    print(f"Setting {axis} servo to {angle} degrees")
    time.sleep(0.25)

def capture_image():
    """
    Capture an image using a USB webcam and save it locally.
    """
    # Initialize the webcam
    camera = cv2.VideoCapture(0)
    camera.set(3, 1280)  # Set width
    camera.set(4, 720)   # Set height

    ret, frame = camera.read()
    if ret:
        image_path = "weed_image.jpg"
        cv2.imwrite(image_path, frame)
        print(f"Image captured and saved as '{image_path}'")
    else:
        print("Failed to capture image")

    camera.release()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'direction' in request.form:
            direction = request.form['direction']
            speed = int(request.form.get('speed', 50))
            move(direction, speed)
        if 'servo_x' in request.form:
            x_angle = int(request.form['servo_x'])
            set_servo_position('x_axis', x_angle)
        if 'servo_y' in request.form:
            y_angle = int(request.form['servo_y'])
            set_servo_position('y_axis', y_angle)
    return render_template('index.html')

@app.route('/capture', methods=['POST'])
def capture():
    capture_image()
    return jsonify({"message": "Image captured successfully"})

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000)
    finally:
        print("WeedBot Shutting Down...\nRoBros, Inc.")