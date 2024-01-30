import RPi.GPIO as GPIO
import time
import random

class Experiment:
    def __init__(self, water_solenoid_pin, taste_solenoid_pin, reward_solenoid_pin, taste_intan_pin, water_intan_pin, reward_intan_pin, odor_intan_pin):
        self.PINS = {
            'cue_light': 15,
            'ir_beam': 16,
            'vacuum_solenoid': 23,  # Use 23 as the vacuum solenoid pin
            'odor_solenoids': [33, 35, 37, 31],
            'taste_solenoid': taste_solenoid_pin,
            'water_solenoid': water_solenoid_pin,
            'reward_solenoid': reward_solenoid_pin,
            'odor_intan_pin': odor_intan_pin,
            'taste_intan_pin': taste_intan_pin,
            'water_intan_pin': water_intan_pin,
            'reward_intan_pin': reward_intan_pin
        }
        self.setup_gpio_pins()

    def setup_gpio_pins(self):
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

    def activate_odor_intan_input(self, pin):
        GPIO.output(pin, 1)

    def deactivate_odor_intan_input(self, pin):
        GPIO.output(pin, 0)

    def activate_taste_intan_input(self, pin):
        GPIO.output(pin, 1)

    def deactivate_taste_intan_input(self, pin):
        GPIO.output(pin, 0)
        
    def activate_water_intan_input(self, pin):
        GPIO.output(pin, 1)

    def deactivate_water_intan_input(self, pin):
        GPIO.output(pin, 0)
        
    def activate_reward_intan_input(self, pin):
        GPIO.output(pin, 1)
        pass

    def deactivate_reward_intan_input(self, pin):
        GPIO.output(pin, 0)

    def activate_cue_light(self):
        GPIO.output(self.PINS['cue_light'], 0)  # Activate cue light

    def deactivate_cue_light(self):
        GPIO.output(self.PINS['cue_light'], 1)  # Deactivate cue light

    def log_event(self, event_name):
        timestamp = time.time()
        timestamp_tenths = int((timestamp % 1) * 10)
        formatted_timestamp = time.strftime("%Y-%m-%d %H:%M:%S.", time.localtime()) + str(timestamp_tenths)
        print(f"[{formatted_timestamp}] {event_name}")

    def run_experiment(self, num_trials, selected_odors, water_open_times, reward_open_times, taste_open_times, water_intan_pin, taste_intan_pin, reward_intan_pin, odor_intan_pin):
        try:
            for trial in range(num_trials):
                self.log_event("Cue light turned On")
                self.activate_cue_light()

                # Wait for IR beam to be crossed for at least 0.5 seconds
                self.log_event("Waiting for IR beam to be crossed for 0.5 seconds...")
                start_time = time.time()
                crossed_duration = 0
                while crossed_duration < 0.5:
                    if GPIO.input(self.PINS['ir_beam']) == 1:
                        crossed_duration = time.time() - start_time
                    else:
                        crossed_duration = 0  # Reset the timer if beam is broken
                    time.sleep(0.1)  # Adjust the sleep time as needed

                self.log_event("Cue light turned Off")
                self.log_event("Vacuum Off")
                self.activate_solenoid(23)
                self.deactivate_cue_light()
                odor_intan_pin = 8
                        
                self.log_event("Odor solenoid turned On")
                self.activate_solenoid(selected_odor_pin)
                    
                # Activate the corresponding Intan digital input pin
                self.log_event("Activating Odor Intan Pin")
                self.activate_odor_intan_input(odor_intan_pin)

                self.log_event("Water solenoid turned On")
                self.activate_solenoid(self.PINS['water_solenoid'])
                self.activate_water_intan_input(self.PINS['water_intan_pin'])

                # Sleep for the specified water solenoid open time
                time.sleep(water_open_times)

                # Close the water solenoid after the specified open time
                self.log_event("Water solenoid turned Off")
                self.deactivate_solenoid(self.PINS['water_solenoid'])
                self.deactivate_water_intan_input(self.PINS['water_intan_pin'])
                    
                self.log_event("Odor solenoid turned Off")
                self.deactivate_solenoid(selected_odor_pin)
                
                self.log_event("Deactivating Odor Intan Pin")
                self.deactivate_odor_intan_input(odor_intan_pin)
                time.sleep(2)
                self.log_event("Vacuum On")
                self.deactivate_solenoid(23)

                time.sleep(30)
                # Check if the IR beam is crossed for 2.1 seconds
                
                self.log_event("Checking IR beam for 2.1 seconds...")
                start_time = time.time()
                crossed_duration = 0
                while crossed_duration < 1:
                    if GPIO.input(self.PINS['ir_beam']) == 0:
                        crossed_duration = time.time() - start_time
                    else:
                        crossed_duration = 0  # Reset the timer if beam is broken

                    if crossed_duration >= 0.5:
                        self.log_event("IR beam crossed for 0.5 seconds. Reward solenoid turned On")
                        self.activate_solenoid(self.PINS['reward_solenoid'])
                        self.activate_reward_intan_input(self.PINS['reward_intan_pin'])
                        time.sleep(reward_open_times)

                        self.log_event("Reward solenoid turned Off")
                        self.deactivate_solenoid(self.PINS['reward_solenoid'])
                        self.deactivate_reward_intan_input(self.PINS['reward_intan_pin'])
                    else:
                        self.log_event("IR beam not crossed for 0.5 seconds. Skipping reward.")

                    iti = random.uniform(30, 45)
                    self.log_event("Waiting for ITI (Inter-Trial Interval)...")
                    time.sleep(iti)

                    if trial < num_trials - 1:
                        # Print a space between trials
                        print("\n")
                                
        except KeyboardInterrupt:
            print("Experiment interrupted by user.")

        finally:
            GPIO.cleanup()

def main():
    try:
        water_solenoid_pin = int(input("Enter water solenoid pin (e.g., 11): "))
        taste_solenoid_pin = int(input("Enter taste solenoid pin (e.g., 13): "))
        reward_solenoid_pin = int(input("Enter reward solenoid pin (e.g., 21): "))

        num_trials = int(input("Enter the number of trials: "))
        selected_odors = [int(odor) for odor in input("Enter selected odors separated by spaces (e.g., 0 1 2): ").split()]

        # Validate the number of selected odors and Intan pins
        if len(selected_odors) < 1:
            print("No odors selected. Exiting program.")
            return
            
        odor_intan_pin = int(input("Enter Intan digital input pin for odor: "))
        taste_intan_pin = int(input("Enter Intan digital input pin for taste solenoid: "))
        water_intan_pin = int(input("Enter Intan digital input pin for water solenoid: "))
        reward_intan_pin = int(input("Enter Intan digital input pin for reward solenoid: "))


        # Take input for solenoid open times in seconds (as decimals)
        water_open_time = float(input("Enter water solenoid open time (in seconds, e.g., 0.1): "))
        taste_open_time = float(input("Enter taste solenoid open time (in seconds, e.g., 0.1): "))
        reward_open_time = float(input("Enter reward solenoid open time (in seconds, e.g., 0.1): "))

        # Print assigned pins and open times for reference
        print("Water Solenoid Pins:", water_solenoid_pin)
        print("Taste Solenoid Pins:", taste_solenoid_pin)
        print("Odor Intan Pin:", odor_intan_pin)
        print("Taste Intan Pin:", taste_intan_pin)
        print("Water Intan Pin:", water_intan_pin)
        print("Reward Intan Pin:", reward_intan_pin)
        print("Water Solenoid Open Time:", water_open_time, "seconds")
        print("Taste Solenoid Open Time:", taste_open_time, "seconds")
        print("Reward Solenoid Open Time:", reward_open_time, "seconds")

        # Run the experiment
        odor_intan_pin = 8
        experiment = Experiment(water_solenoid_pin, taste_solenoid_pin, reward_solenoid_pin, taste_intan_pin, water_intan_pin, reward_intan_pin, odor_intan_pin)
        experiment.run_experiment(num_trials, selected_odors, odor_intan_pin, water_intan_pin, reward_intan_pin, taste_open_time, water_open_time, taste_intan_pin, reward_open_time)

    except Exception as e:
        print(f"Error: {e}")

    except KeyboardInterrupt:
        print("Experiment interrupted by user.")

    finally:
        print("done")
            

if __name__ == "__main__":
    main()

