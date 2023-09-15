import RPi.GPIO as GPIO
import time
import datetime
import random
import curses
import configparser
import logging
import sys
import csv
from picamera import PiCamera
import multiprocessing
from multiprocessing import Pool

class GPIOController:
    def __init__(self):
        self.PINS = {
            'cue_light': 11,
            'ir_beam': 13,
            'vacuum_solenoids': [8, 10, 12],
            'odor_solenoids': [31, 33, 35],
            'digital_inputs': [19, 21, 23, 16, 18, 22],
            'taste_solenoid': [26, 32, 36, 37, 38, 40],
            'water_solenoid': None,
            'retro_solenoid': None,
        }

    def setup(self):
        GPIO.setwarnings(False)
        GPIO.cleanup()
        GPIO.setmode(GPIO.BOARD)
        for pin in self.PINS.values():
            GPIO.setup(pin, GPIO.OUT)
        GPIO.setup(self.PINS['ir_beam'], GPIO.IN)

    def activate_solenoid(self, pin):
        GPIO.output(pin, 1)

    def deactivate_solenoid(self, pin):
        GPIO.output(pin, 0)

    def activate_digital_input(self, pin):
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 1)

    def deactivate_digital_input(self, pin):
        GPIO.setup(pin, GPIO.IN)

class Logger:
    def __init__(self, filename):
        logging.basicConfig(filename=filename, level=logging.INFO, format='[%(asctime)s] %(message)s')
        self.logger = logging.getLogger('Experiment')
        self.log_filename = filename

    def log_event(self, event_name):
        current_time = datetime.datetime.now()
        formatted_timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_line = f"[{formatted_timestamp}] {event_name}"
        print(log_line)
        with open(self.log_filename, mode='a', newline='') as log_file:
            log_writer = csv.writer(log_file)
            log_writer.writerow([formatted_timestamp, event_name])

class VideoRecorder:
    def __init__(self):
        self.camera = PiCamera()

    def record_video(self, filename, duration):
        try:
            self.camera.start_recording(filename)
            self.camera.wait_recording(duration)
        except Exception as e:
            self.logger.error(f"Error in record_video: {str(e)}")

    def stop_video_recording(self):
        try:
            self.camera.stop_recording()
        except Exception as e:
            self.logger.error(f"Error in stop_video_recording: {str(e)}")

# Define a class for the experiment
class Experiment:
    def __init__(self):
        # Initialize GPIO controller
        self.gpio_controller = GPIOController()
        self.gpio_controller.setup()

        # Initialize logger (global instance)
        self.logger = None

        # Load experiment configuration from a file
        self.load_config()

        # Define the log filename based on the configuration
        self.log_filename = self.config.get('Experiment', 'log_filename')

        # Initialize the video recorder
        self.video_recorder = VideoRecorder()

    # Function to set up logging (use the global logger)
    def setup_logging(self):
        self.logger = Logger(self.log_filename)

    # Function to get the animal ID from user input
    def get_animal_id(self):
        animal_id = input("Enter Animal ID (anID): ")
        return animal_id

    # Function to set up GPIO pins
    def setup_gpio_pins(self):
        GPIO.setwarnings(False)
        GPIO.cleanup()
        GPIO.setmode(GPIO.BOARD)
        for pin in self.PINS.values():
            GPIO.setup(pin, GPIO.OUT)
        GPIO.setup(self.PINS['ir_beam'], GPIO.IN)

    # Function to activate a solenoid
    def activate_solenoid(self, pin):
        GPIO.output(pin, 1)

    # Function to deactivate a solenoid
    def deactivate_solenoid(self, pin):
        GPIO.output(pin, 0)

    # Function to activate a digital input
    def activate_digital_input(self, pin):
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 1)

    # Function to deactivate a digital input
    def deactivate_digital_input(self, pin):
        GPIO.setup(pin, GPIO.IN)

    # Function to log an event with a timestamp
    def log_event(self, event_name):
        current_time = datetime.datetime.now()
        formatted_timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_line = f"[{formatted_timestamp}] {event_name}"
        print(log_line)

        # Define quirky messages for specific events
        quirky_messages = {
            "Cue light turned On": "Let the show begin!",
            "Waiting for IR beam to be crossed...": "Counting down the seconds...",
            "Animal ID": "Who's the star of the show? Enter the Animal ID (anID)!",
        }

        quirky_message = quirky_messages.get(event_name, "")
        if quirky_message:
            print(f"{quirky_message}")

        # Log the event to a CSV file
        with open(self.log_filename, mode='a', newline='') as log_file:
            log_writer = csv.writer(log_file)
            log_writer.writerow([formatted_timestamp, event_name])

    # Function to load configuration settings from a file
    def load_config(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

    # Function to run the odor solenoid
    def run_odor_solenoid(self, pin, barrier):
        try:
            self.log_event("Odor_solenoid turned On")
            self.activate_solenoid(pin)
            barrier.wait()
            time.monotonic(2.1)

        except Exception as e:
            self.logger.error(f"Error in run_odor_solenoid: {str(e)}")

        finally:
            self.log_event("Odor_solenoid turned Off")
            self.deactivate_solenoid(pin)

    # Function to run the water solenoid
    def run_water_solenoid(self, open_time, barrier):
        try:
            barrier.wait()
            self.log_event("Water_solenoid turned On")
            self.activate_solenoid(self.PINS['water_solenoid'])
            time.monotonic(open_time)

        except Exception as e:
            self.logger.error(f"Error in run_water_solenoid: {str(e)}")

        finally:
            self.log_event("water_solenoid turned Off")

    # Function to run the retro solenoid
    def run_retro_solenoid(self, open_time, barrier):
        try:
            barrier.wait()
            self.log_event("Retro_solenoid turned On")
            self.activate_solenoid(self.PINS['retro_solenoid'])
            time.monotonic(open_time)

        except Exception as e:
            self.logger.error(f"Error in run_retro_solenoid: {str(e)}")

        finally:
            self.log_event("Retro_solenoid turned Off")

    # Function to record video using the camera
    def record_video(self, filename, duration):
        try:
            self.video_recorder.record_video(filename, duration)

        except Exception as e:
            self.logger.error(f"Error in record_video: {str(e)}")

    # Function to stop video recording
    def stop_video_recording(self):
        try:
            self.video_recorder.stop_video_recording()

        except Exception as e:
            self.logger.error(f"Error in stop_video_recording: {str(e)}")

    # Function to display a countdown on the terminal
    def countdown(self, seconds):
        try:
            for remaining in range(int(seconds), 0, -1):
                sys.stdout.write("\r")
                sys.stdout.write(f"Time remaining: {remaining} seconds")
                sys.stdout.flush()
                time.monotonic(1)
            sys.stdout.write("\r")
            sys.stdout.write("Time remaining: 0 seconds\n")
            sys.stdout.flush()

        except Exception as e:
            self.logger.error(f"Error in countdown: {str(e)}")

    # Function to run the entire experiment
    def run_experiment(self, num_trials, selected_odors, intan_pins, water_open_time, retro_open_time):
        try:
            animal_id = self.get_animal_id()
            self.log_event(f"Animal ID: {animal_id}")

            for trial in range(num_trials):
                self.log_event(f"=== Trial {trial + 1} ===")
                self.log_event("Cue light turned On")
                self.log_event("Waiting for IR beam to be crossed...")

                while GPIO.input(self.PINS['ir_beam']) == 0:
                    pass

                self.selected_odor_pin = None
                self.selected_odor_intan = None
                self.selected_vacuum_pins = []
                self.selected_odor = None

                if selected_odors:
                    self.selected_odor = random.choice(selected_odors)
                    self.selected_odor_pin = self.PINS['odor_solenoids'][self.selected_odor]
                    self.selected_odor_intan = self.PINS['digital_inputs'][self.selected_odor]
                    self.log_event(f"Odor {self.selected_odor} turned On")

                    # Create a synchronization barrier for solenoid processes
                    self.solenoid_sync_barrier = multiprocessing.Barrier(2)
                    odor_process = multiprocessing.Process(target=self.run_odor_solenoid, args=(self.selected_odor_pin, self.solenoid_sync_barrier))
                    water_process = multiprocessing.Process(target=self.run_water_solenoid, args=(water_open_time,))
                    retro_process = multiprocessing.Process(target=self.run_retro_solenoid, args=(retro_open_time, self.solenoid_sync_barrier))
                    odor_process.start()
                    water_process.start()
                    retro_process.start()
                    odor_process.join()
                    water_process.join()
                    retro_process.join()

                    # Deactivate digital input pins
                    for intan_pin in intan_pins:
                        self.log_event(f"Deactivating Intan Pin {intan_pin}")
                        self.deactivate_digital_input(intan_pin)

                    if self.selected_odor == 2:
                        self.log_event("Retro_solenoid turned Off")
                        self.deactivate_solenoid(self.PINS['retro_solenoid'])

                    for vacuum_pin in self.selected_vacuum_pins:
                        self.deactivate_solenoid(vacuum_pin)

                self.log_event("Water_solenoid turned On")
                self.activate_solenoid(self.PINS['water_solenoid'])
                time.monotonic(water_open_time)
                self.log_event("Water_solenoid turned Off")
                self.log_event("Cue light turned Off")
                self.stop_video_recording()
                iti = random.uniform(10, 15)
                self.log_event("Waiting for ITI (Inter-Trial Interval)...")
                self.countdown(iti)
                if trial < num_trials - 1:
                    print("\n")

        except KeyboardInterrupt:
            pass

        finally:
            self.camera.close()
            GPIO.cleanup()

def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()

    experiment = None  # Initialize experiment object outside the loop
    pool = Pool(processes=1)  # Create a multiprocessing pool

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Main Menu")
        stdscr.addstr(2, 2, "1. Set Number of Trials")
        stdscr.addstr(3, 2, "2. Select Odors")
        stdscr.addstr(4, 2, "3. Set Intan Pins")
        stdscr.addstr(5, 2, "4. Set Water Solenoid Pin")
        stdscr.addstr(6, 2, "5. Set Retro Solenoid Pin")
        stdscr.addstr(7, 2, "6. Set Water Open Time")
        stdscr.addstr(8, 2, "7. Set Retro Open Time")
        stdscr.addstr(9, 2, "8. Run Experiment")
        stdscr.addstr(10, 2, "9. Exit")
        stdscr.addstr(12, 2, "Enter your choice: ")
        stdscr.refresh()

        choice = stdscr.getch() - ord('0')

        if choice == 1:
            num_trials = int(input("Enter the number of trials: "))
        elif choice == 2:
            selected_odors = input("Enter selected odors separated by spaces (e.g., Odor1 Odor3): ").split()
        elif choice == 3:
            intan_pins = input("Enter Intan digital input pins separated by spaces (e.g., 19 21 23): ").split()
            intan_pins = [int(pin) for pin in intan_pins]
        elif choice == 4:
            Experiment.PINS['water_solenoid'] = int(input("Enter water solenoid pin (26, 32, 36, 37, 38, 40): "))
        elif choice == 5:
            Experiment.PINS['retro_solenoid'] = int(input("Enter retro solenoid pin (26, 32, 36, 37, 38, 40): "))
        elif choice == 6:
            water_open_time = float(input("Enter water solenoid open time (in seconds): "))
        elif choice == 7:
            retro_open_time = float(input("Enter retro solenoid open time (in seconds): "))
        elif choice == 8:
            experiment = Experiment()
            experiment.setup_logging()  # Initialize the logger
            pool.apply_async(experiment.run_experiment, (num_trials, selected_odors, intan_pins, water_open_time, retro_open_time))
        elif choice == 9:
            if experiment:
                experiment.camera.close()  # Close the camera if it's running
            GPIO.cleanup()
            break

if __name__ == "__main__":
    curses.wrapper(main)
