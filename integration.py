import RPi.GPIO as GPIO
import time
import smbus
import datetime
from threading import Thread

GPIO.setmode(GPIO.BCM)

#-------------stepper motor setup-----------------
stepperPins = [18,23,24,25]
GPIO.setup(stepperPins,GPIO.OUT)

#-------------PWM LED setup-----------------------
GPIO.setup(26, GPIO.OUT)
pinLED = GPIO.PWM(26, 60)  # pin=26 frequency=60Hz

#-------Ultrasonic Distance Sensor setup----------
TRIGGER_PIN=12
ECHO_PIN=17
HIGH_TIME=0.00001 # 10 microseconds
LOW_TIME=1-HIGH_TIME
GPIO.setup(TRIGGER_PIN,GPIO.OUT)
GPIO.setup(ECHO_PIN,GPIO.IN)
SPEED_OF_SOUND=330/float(1000000)


def stepperMotor():
    stepperSequence=[]
    stepperSequence.append([GPIO.HIGH, GPIO.LOW, GPIO.LOW,GPIO.LOW]) #A
    stepperSequence.append([GPIO.LOW, GPIO.HIGH, GPIO.LOW,GPIO.LOW]) #B
    stepperSequence.append([GPIO.LOW, GPIO.LOW, GPIO.HIGH,GPIO.LOW]) #C
    stepperSequence.append([GPIO.LOW, GPIO.LOW, GPIO.LOW,GPIO.HIGH]) #D

    degree = int(input("Enter a degree (-1 to exit): "))
    try:
        while degree != -1:
            step = 0
            steps = degree/360*4096/2 # divide by 2 for full steps
            print("Stepper motor starting...")
            while step < steps:
                for row in stepperSequence: 
                    GPIO.output(stepperPins,row)
                    time.sleep(0.01)
                    step += 1
            degree = int(input("Enter a degree (-1 to exit): "))
        print("Stepper motor finished...\n")
        time.sleep(2)
    except KeyboardInterrupt:		
        pass

def ADDAModule():
    address = 0x48
    A0 = 0x40  # potentiometer
    A1 = 0x41  # photoresistor
    A2 = 0x42  # thermistor
    sensor = 0

    bus = smbus.SMBus(1)

    userInput = input("Enter A0/A1/A2 for a potentiometer/photoresistor/thermistor, respectively: ")
    while sensor == 0:
        if userInput == 'A0':
            sensor = A0
            break
        elif userInput == 'A1':
            sensor = A1
            break
        elif userInput == 'A2':
            sensor = A2
            break
        else: 
            print("\nSensor does not exist, please enter A0, A1 or A2\n")
        userInput = input("Enter A0/A1/A2 for a potentiometer/photoresistor/thermistor, respectively: ")

    try:
        print("\nAD/DA module starting...") 
        for i in range(100):               
            bus.write_byte(address, sensor) # change input value
            value = bus.read_byte(address)
            print("AOUT:%1.3f  " %(value*3.3/255))
            time.sleep(0.1)
        print("AD/DA module finished...\n")
        time.sleep(2)
    except KeyboardInterrupt:		
            pass

def PWMLED():
    pinLED.start(0)
    try:
        test = input("Would you like to choose the brightness (Y or N):")
        if test == 'Y' or test == 'y':
            temp = int(input("Enter a brightness between 0-100 (-1 to exit): "))
            while temp != -1:
                if temp >= 0 and temp <= 100:
                    pinLED.ChangeDutyCycle(temp)
                else:
                    print("Invalid")
                temp = int(input("Enter a brightness between 0-100 (-1 to exit): "))
        else:
            print("\nLED starting at 0 duty cycle...")
            for i in range(0, 101, 10):
                pinLED.ChangeDutyCycle(i)
                time.sleep(1)
                print("Duty cycle: ", i)
        print("PWM LED finished...\n")
        time.sleep(2)
    except KeyboardInterrupt:
        pass
    pinLED.stop()

def getDistance(td):
	distance=SPEED_OF_SOUND*td/float(2)
	return distance

def ultrasonicDistanceSensor():
    try:
        print("\nUltrasonic Distance Sensor starting...")
        for i in range(20):
            GPIO.output(TRIGGER_PIN,GPIO.HIGH)
            time.sleep(HIGH_TIME)
            GPIO.output(TRIGGER_PIN,GPIO.LOW)

            while GPIO.input(ECHO_PIN)==False:
                pass

            starttime = datetime.datetime.now().microsecond
            while GPIO.input(ECHO_PIN)==True:
                pass

            endtime = datetime.datetime.now().microsecond
            travelTime = endtime - starttime
            distance = getDistance(travelTime)
            if (distance > 0):
                print(distance)
            else: 
                pass
            time.sleep(LOW_TIME)
        print("Ultrasonic Distance Sensor finished...\n")
        time.sleep(2)
    except: 
        KeyboardInterrupt 

def main():
    selectDevice = input("Select 1, 2, 3 or 4 for the stepper motor, AD/DA module, PWM LED or Ultrasonic Distance sensor, respectively (-1 to exit): ")
    try:
        while selectDevice != '-1':
            if selectDevice == '1':
                stepperMotor()
                selectDevice = 0
            elif selectDevice == '2':
                ADDAModule()
                selectDevice = 0
            elif selectDevice == '3':
                PWMLED()
                selectDevice = 0              
            elif selectDevice == '4':
                ultrasonicDistanceSensor()
                selectDevice = 0
            else:
                print("\nInvalid input, please input 1, 2, 3 or 4\n")
            selectDevice = input("\nSelect 1, 2, 3 or 4 for the stepper motor, AD/DA module, PWM LED or Ultrasonic Distance sensor, respectively (-1 to exit): \n")
    except: 
        KeyboardInterrupt 
    GPIO.cleanup()

if __name__ == "__main__":
    main()