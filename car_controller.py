import gpiod
import time
import curses
import threading

# GPIO chip and pins (BCM numbering)
CHIP = 'gpiochip0'
SERVO1_PIN = 18  # Steering servo on GPIO 24
SERVO2_PIN = 23  # Speed servo on GPIO 23

# PWM period (50Hz = 20ms)
PERIOD = 0.02

# Pulse widths for Servo 1 (Steering) in seconds
SERVO1_LEFT = 0.0009   # Partly left (e.g., 60°)
SERVO1_CENTER = 0.00135 # Central (e.g., 90°)
SERVO1_RIGHT = 0.0018  # Partly right (e.g., 120°)

# Pulse widths for Servo 2 (Speed Controller) in seconds
SERVO2_CENTRAL = 0.0013 # Central/stop (e.g., 90°)
SERVO2_PARTIAL = 0.0017 # Forward partial speed (e.g., 110°)
SERVO2_MAX = 0.002     # Forward maximum speed (e.g., 180°)
SERVO2_REVERSE = 0.0009 # Reverse partial speed (e.g., 70°)

def send_pwm_burst(chip, pin, pulse_width, duration, return_to_central=False, central_pulse=SERVO2_CENTRAL):
    """Send a burst of PWM signals to move the servo to the desired position."""
    line = chip.get_line(pin)
    line.request(consumer='servo', type=gpiod.LINE_REQ_DIR_OUT)
    start_time = time.time()
    while time.time() - start_time < duration:
        line.set_value(1)
        time.sleep(pulse_width)
        line.set_value(0)
        time.sleep(PERIOD - pulse_width)
    if return_to_central and pin == SERVO2_PIN:
        # Return Servo 2 to central position after duration
        start_time = time.time()
        while time.time() - start_time < duration:
            line.set_value(1)
            time.sleep(central_pulse)
            line.set_value(0)
            time.sleep(PERIOD - central_pulse)
    line.release()

def main(stdscr):
    # Initialize curses
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.timeout(100)  # Non-blocking input with 100ms timeout
    stdscr.addstr(0, 0, "Servo Control Commands:")
    stdscr.addstr(1, 0, "- Servo 1 (Steering): '1 left', '1 center', '1 right'")
    stdscr.addstr(2, 0, "- Servo 2 (Speed): Up arrow (forward), Down arrow (reverse)")
    stdscr.addstr(3, 0, "- Quit: 'q'")
    stdscr.addstr(5, 0, "Enter command or use arrow keys: ")
    stdscr.refresh()

    chip = gpiod.Chip(CHIP)
    command = ""
    try:
        while True:
            try:
                # Check for key press (non-blocking)
                key = stdscr.getch()
                if key == curses.KEY_UP:
                    # Up arrow: Servo 2 forward (partial speed)
                    threading.Thread(target=send_pwm_burst, args=(chip, SERVO2_PIN, SERVO2_PARTIAL, 0.5, True)).start()
                    stdscr.addstr(6, 0, "Servo 2 set to partial speed (forward)  ")
                    stdscr.refresh()
                elif key == curses.KEY_DOWN:
                    # Down arrow: Servo 2 reverse
                    threading.Thread(target=send_pwm_burst, args=(chip, SERVO1_PIN, SERVO1_CENTER, 0.5, True)).start()
                    stdscr.addstr(6, 0, "Centering           ")
                    stdscr.refresh()
                elif key == curses.KEY_RIGHT:
                    threading.Thread(target=send_pwm_burst, args=(chip,SERVO1_PIN, SERVO1_RIGHT,0.5,False)).start()
                    stdscr.addstr(6 ,0, "Turning right           ")
                    stdscr.refresh()
                elif key == curses.KEY_LEFT:
                    threading.Thread(target=send_pwm_burst, args=(chip,SERVO1_PIN, SERVO1_LEFT,0.5,False)).start()
                    stdscr.addstr(6, 0, "Turning left             ")
                    stdscr.refresh()
                elif key != -1:  # Other key pressed
                    char = chr(key).lower()
                    if char == 'q':
                        stdscr.addstr(6, 0, "Exiting...                            ")
                        stdscr.refresh()
                        break
                    elif char == '\n':
                        if command:
                            try:
                                servo, position = command.strip().split()
                                if servo == '1':
                                    if position == 'left':
                                        send_pwm_burst(chip, SERVO1_PIN, SERVO1_LEFT)
                                        stdscr.addstr(6, 0, "Servo 1 set to partly left            ")
                                    elif position == 'center':
                                        send_pwm_burst(chip, SERVO1_PIN, SERVO1_CENTER)
                                        stdscr.addstr(6, 0, "Servo 1 set to central                ")
                                    elif position == 'right':
                                        send_pwm_burst(chip, SERVO1_PIN, SERVO1_RIGHT)
                                        stdscr.addstr(6, 0, "Servo 1 set to partly right           ")
                                    else:
                                        stdscr.addstr(6, 0, "Invalid position. Use 'left', 'center', or 'right' ")
                                elif servo == '2':
                                    if position == 'central':
                                        send_pwm_burst(chip, SERVO2_PIN, SERVO2_CENTRAL)
                                        stdscr.addstr(6, 0, "Servo 2 set to central (stop)         ")
                                    elif position == 'partial':
                                        threading.Thread(target=send_pwm_burst, args=(chip, SERVO2_PIN, SERVO2_PARTIAL, 0.5, True)).start()
                                        stdscr.addstr(6, 0, "Servo 2 set to partial speed (forward) ")
                                    elif position == 'max':
                                        threading.Thread(target=send_pwm_burst, args=(chip, SERVO2_PIN, SERVO2_MAX, 0.5, True)).start()
                                        stdscr.addstr(6, 0, "Servo 2 set to maximum speed (forward) ")
                                    else:
                                        stdscr.addstr(6, 0, "Invalid position. Use 'central', 'partial', or 'max' ")
                                else:
                                    stdscr.addstr(6, 0, "Invalid servo. Use '1' for steering or '2' for speed ")
                                stdscr.refresh()
                            except ValueError:
                                stdscr.addstr(6, 0, "Invalid format. Use '<servo> <position>', e.g., '1 left' ")
                                stdscr.refresh()
                            command = ""  # Reset command after processing
                    else:
                        command += char
                        stdscr.addstr(5, 30, command + " " * 20)
                        stdscr.refresh()
            except ValueError:
                stdscr.addstr(6, 0, "Invalid input detected                    ")
                stdscr.refresh()
    finally:
        chip.close()
        stdscr.addstr(6, 0, "GPIO resources released.                  ")
        stdscr.refresh()
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()

if __name__ == '__main__':
    curses.wrapper(main)
