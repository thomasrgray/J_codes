'''
jet_rig contains basic functions for using the Jetson Nano behavior and electrophysiology rig in the Katz Lab

These functions can be used directly via IPython in a terminal window or called by other codes
'''

# Import necessary libraries
import time
import random
import csv
import numpy as np
import Jetson.GPIO as GPIO  

# Import other necessary libraries for video
from subprocess import Popen
import easygui
import os

# Setup GPIO for Jetson Nano
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
# Function to clear taste lines
def clearout(outports=[7, 11, 12, 13, 15, 16, 18, 22, 29, 31, 32, 33, 35, 36, 37, 38, 40], dur=5):
    # Setup GPIO ports
    GPIO.setmode(GPIO.BOARD)
    for i in outports:
        GPIO.setup(i, GPIO.OUT)

    # Activate taste lines
    for i in outports:
        GPIO.output(i, 1)
    time.sleep(dur)
    
    # Deactivate taste lines
    for i in outports:
        GPIO.output(i, 0)

    print('Tastant line clearing complete.')

# Function to calibrate taste lines
def calibrate(outports=[7, 11, 12, 13, 15, 16, 18, 22, 29, 31, 32, 33, 35, 36, 37, 38, 40], opentime=0.05, repeats=5):
    # Setup GPIO ports
    GPIO.setmode(GPIO.BOARD)
    for i in outports:
        GPIO.setup(i, GPIO.OUT)

    # Open ports for calibration
    for rep in range(repeats):
        for i in outports:
            GPIO.output(i, 1)
        time.sleep(opentime)
        for i in outports:
            GPIO.output(i, 0)
        time.sleep(1)

    print('Calibration procedure complete.')
# Function for passive deliveries
def passive(outports=[18, 22, 29, 31, 32, 33], intaninputs=[7, 11, 12, 13, 15, 16], 
            opentimes=[0.01, 0.01, 0.01, 0.01, 0.01, 0.01], itimin=22, itimax=22, trials=30):
    # Ask for directory to save data
    directory = easygui.diropenbox(msg='Select the directory to save the delivery times from this experiment.', title='Select directory')
    os.chdir(directory)
    
    # Setup GPIO ports
    GPIO.setmode(GPIO.BOARD)
    for i in outports:
        GPIO.setup(i, GPIO.OUT)
    for i in intaninputs:
        GPIO.setup(i, GPIO.OUT)

    # Set and shuffle trial order
    tot_trials = len(outports) * trials
    count = 0
    trial_array = trials * list(np.arange(len(outports)))
    time_array = []
    random.shuffle(trial_array)

    time.sleep(15)

    # Loop through trials
    for i in trial_array:
        time_array.append(time.ctime())
        GPIO.output(outports[i], 1)
        GPIO.output(intaninputs[i], 1)
        time.sleep(opentimes[i])
        GPIO.output(outports[i], 0)
        GPIO.output(intaninputs[i], 0)
        count += 1
        iti = random.randint(itimin, itimax)
        print('Trial '+str(count)+' of '+str(tot_trials) +
              ' completed. ITI = '+str(iti)+' sec.')
        time.sleep(iti)

    print('Passive deliveries completed')

    # Save delivery times as CSV
    csv_name = 'output_times.csv'
    with open(csv_name, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for r_i in range(len(time_array)):
            spamwriter.writerow(time_array[r_i])

    print('Delivery times .csv saved.')
# Function for passive cue deliveries
def passive_cue(outports=[18, 22, 29, 31, 32, 33], 
                intaninputs=[7, 11, 12, 13, 15, 16], opentimes=[0.01], itimin=10, itimax=30, trials=150,
                cue_input=40):

    # Setup GPIO ports
    GPIO.setmode(GPIO.BOARD)
    for i in outports:
        GPIO.setup(i, GPIO.OUT)
    for i in intaninputs:
        GPIO.setup(i, GPIO.OUT)
    GPIO.setup(cue_input, GPIO.OUT)

    # Set and shuffle trial order
    tot_trials = len(outports) * trials
    count = 0
    trial_array = trials * list(np.arange(len(outports)))
    time_array = []
    random.shuffle(trial_array)

    time.sleep(3)

    # Loop through trials
    for i in trial_array:
        time_array.append(time.ctime())
        GPIO.output(cue_input, 1)
        GPIO.output(outports[i], 1)
        GPIO.output(intaninputs[i], 1)
        time.sleep(opentimes[i])
        GPIO.output(outports[i], 0)
        GPIO.output(intaninputs[i], 0)
        time.sleep(1)
        GPIO.output(cue_input, 0)
        count += 1
        iti = random.randint(itimin, itimax)
        print('Trial '+str(count)+' of '+str(tot_trials) +
              ' completed. ITI = '+str(iti)+' sec.')
        time.sleep(iti)

    print('Passive cue deliveries completed')

    # Save delivery times as CSV
    csv_name = 'output_times.csv'
    with open(csv_name, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for r_i in range(len(time_array)):
            spamwriter.writerow(time_array[r_i])

    print('Delivery times .csv saved.')
# Function for basic nose poking procedure
def basic_np(outport=31, opentime=0.012, iti=[.4, 1, 2], trials=200, outtime=0):
    intaninput = 35
    trial = 1
    inport = 36
    pokelight = 37
    houselight = 38
    lights = 0
    maxtime = 60
#35, 36, 37, 38, 40
    # Setup GPIO ports
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pokelight, GPIO.OUT)
    GPIO.setup(houselight, GPIO.OUT)
    GPIO.setup(inport, GPIO.IN)
    GPIO.setup(outport, GPIO.OUT)
    GPIO.setup(intaninput, GPIO.OUT)

    time.sleep(15)
    starttime = time.time()

    while trial <= trials:
        # Timer to stop experiment if over 60 mins
        curtime = time.time()
        elapsedtime = round((curtime - starttime)/60, 2)
        if elapsedtime > maxtime:
            GPIO.output(pokelight, 0)
            GPIO.output(houselight, 0)
            break

        if lights == 0:
            GPIO.output(pokelight, 1)
            GPIO.output(houselight, 1)
            lights = 1

        # Check for pokes
        if GPIO.input(inport) == 0:
            poketime = time.time()
            curtime = poketime

            # Make rat remove nose from nose poke to receive reward
            while (curtime - poketime) <= outtime:
                if GPIO.input(inport) == 0:
                    poketime = time.time()
                curtime = time.time()

            # Taste delivery and switch off lights
            GPIO.output(outport, 1)
            GPIO.output(intaninput, 1)
            time.sleep(opentime)
            GPIO.output(outport, 0)
            GPIO.output(intaninput, 0)
            GPIO.output(pokelight, 0)
            GPIO.output(houselight, 0)
            print('Trial '+str(trial)+' of '+str(trials)+' completed.')
            trial += 1
            lights = 0

            # Calculate and execute ITI delay. Pokes during ITI reset ITI timer.
            if trial <= trials/2:
                delay = floor((random.random()*(iti[1]-iti[0]))*100)/100 + iti[0]
            else:
                delay = floor((random.random()*(iti[2]-iti[0]))*100)/100 + iti[0]

            poketime = time.time()
            curtime = poketime

            while (curtime - poketime) <= delay:
                if GPIO.input(inport) == 0:
                    poketime = time.time()
                curtime = time.time()

    print('Basic nose poking has been completed.')
# Function for odor nose poking procedure
def odor_np(outport=31, odorport=40, vacport=38, t_opentime=0.012, o_opentime=0.5, v_opentime=1, iti=[.4, 1, 2], trials=200, outtime=0):
    intaninput_t = 7
    intaninput_o = 11
    intaninput_v = 12
    trial = 1
    inport = 36
    pokelight = 37
    houselight = 38
    maxtime = 60

    # Setup GPIO ports
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pokelight, GPIO.OUT)
    GPIO.setup(houselight, GPIO.OUT)
    GPIO.setup(inport, GPIO.IN)
    GPIO.setup(outport, GPIO.OUT)
    GPIO.setup(intaninput_t, GPIO.OUT)
    GPIO.setup(odorport, GPIO.OUT)
    GPIO.setup(intaninput_o, GPIO.OUT)
    GPIO.setup(vacport, GPIO.OUT)
    GPIO.setup(intaninput_v, GPIO.OUT)

    time.sleep(15)
    starttime = time.time()

    while trial <= trials:
        # Timer to stop experiment if over 60 mins
        curtime = time.time()
        elapsedtime = round((curtime - starttime)/60, 2)
        if elapsedtime > maxtime:
            GPIO.output(pokelight, 0)
            GPIO.output(houselight, 0)
            break

        GPIO.output(houselight, 1)

        # Check for pokes
        if GPIO.input(inport) == 0:
            poketime = time.time()
            curtime = poketime
            
            # Vacuum
            GPIO.output(vacport, 1)
            GPIO.output(intaninput_v, 1)
            time.sleep(0.2)  # Overlap vacport with odorport
            GPIO.output(odorport, 1)
            GPIO.output(intaninput_o, 1)
            time.sleep(0.5)  # Remaining 0.2 seconds of odorport opentime
            GPIO.output(vacport, 0)
            GPIO.output(odorport, 0)
            GPIO.output(intaninput_v, 0)
            GPIO.output(intaninput_o, 0)

            # Make rat remove nose from nose poke to receive reward
            while (curtime - poketime) <= outtime:
                if GPIO.input(inport) == 0:
                    poketime = time.time()
                curtime = time.time()

            # Taste delivery and switch off lights
            GPIO.output(outport, 1)
            GPIO.output(intaninput_t, 1)
            time.sleep(t_opentime)
            GPIO.output(outport, 0)
            GPIO.output(intaninput_t, 0)
            GPIO.output(houselight, 0)
            print('Trial '+str(trial)+' of '+str(trials)+' completed.')
            trial += 1

            # Calculate and execute ITI delay
            delay = np.random.choice(np.arange(30, 40, 1), size=1)
            time.sleep(delay)

    print('Odor nose poking has been completed.')
# Function to clear all GPIO settings
def clearall():
    # Define GPIO ports to be cleared
    outports = [7, 11, 12, 13, 15, 16, 18, 22, 29, 31, 32, 33, 35, 36, 37, 38, 40]
    inports = [36]
    pokelights = [37]
    houselight = 38
    intan = [7, 11, 12, 13, 15, 16]

    # Set all ports to default/low state
    for i in intan:
        GPIO.setup(i, GPIO.OUT)
        GPIO.output(i, 0)

    for i in outports:
        GPIO.setup(i, GPIO.OUT)
        GPIO.output(i, 0)

    for i in inports:
        GPIO.setup(i, GPIO.IN, GPIO.PUD_UP)

    for i in pokelights:
        GPIO.setup(i, GPIO.OUT)
        GPIO.output(i, 0)

    for i in lasers:
        GPIO.setup(i, GPIO.OUT)
        GPIO.output(i, 0)

    GPIO.setup(houselight, GPIO.OUT)
    GPIO.output(houselight, 0)

    print('All GPIO ports cleared.')
