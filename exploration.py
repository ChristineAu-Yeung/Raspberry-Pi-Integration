from RPLCD import i2c
import RPi.GPIO as GPIO
import time
import smbus
import datetime

GPIO.setmode(GPIO.BCM)

#-------------LCD setup----------------------
lcdmode = 'i2c'
cols = 16 # LCD columns
rows = 2 # LCD rows
charmap = 'A00'
i2c_expander = 'PCF8574' # chip on LCD
address = 0x27 # i2caddress (command to find: i2cdetect -y 1)
port = 1

#-------------stepper motor setup-----------------
stepperPins = [18,23,24,25]
GPIO.setup(stepperPins,GPIO.OUT)

#-------------PWM LED setup-----------------------
GPIO.setup(26, GPIO.OUT)
pinLED = GPIO.PWM(26, 60)  # pin=26 frequency=60Hz

#-------------initialize LCD-----------------
lcd = i2c.CharLCD(i2c_expander, address, port=port, charmap=charmap,
                  cols=cols, rows=rows)

def LCD():
    userStr = userInputString()
    lcd.write_string(userStr)
    time.sleep(5)
    lcd.clear()
    
def userInputString():
    userStr = str(input("Enter a string (0-32 characters): "))
    check = False
    while check:
        if len(userStr) > 0 and len(userStr) <= 32:
            check = True
            break
        elif len(userStr) > 32:
            print("The inputted string is too long")
        else: 
            print("Please enter a valid string")
        userStr = str(input("Enter a string (0-32 characters): "))
    return userStr

def stepperMotor(): # added LCD
    lcd.write_string("Stepper motor starting...")

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
            degreeStr = "Degree entered: " + str(degree)
            lcd.clear()
            lcd.write_string(degreeStr)
            while step < steps:
                for row in stepperSequence: 
                    GPIO.output(stepperPins,row)
                    time.sleep(0.01)
                    step += 1
            degree = int(input("Enter a degree (-1 to exit): "))
        print("Stepper motor finished...\n")
        time.sleep(2)
        lcd.clear()
    except KeyboardInterrupt:		
        pass

def PWMLED(): # added LCD
    lcd.write_string("LED starting...")

    pinLED.start(0)
    try:
        test = input("Would you like to choose the brightness (Y or N):")
        if test == 'Y' or test == 'y':
            temp = int(input("Enter a brightness between 0-100 (-1 to exit): "))
            while temp != -1:
                if temp >= 0 and temp <= 100:
                    dutyStr = "Brightness: " + str(temp)
                    lcd.clear()
                    lcd.write_string(dutyStr)
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
                dutyStr = "Brightness: " + str(i)
                lcd.clear()
                lcd.write_string(dutyStr)
        print("PWM LED finished...\n")
        time.sleep(2)
        lcd.clear()
    except KeyboardInterrupt:
        pass
    pinLED.stop()

def main():
    selectDevice = input("Select 1, 2 or 3 for the stepper motor, PWM LED or LCD Screen, respectively (-1 to exit): ")
    try:
        while selectDevice != '-1':
            if selectDevice == '1':
                stepperMotor()
                selectDevice = 0
            elif selectDevice == '2':
                PWMLED()
                selectDevice = 0
            elif selectDevice == '3':
                LCD() 
                selectDevice = 0              
            else:
                print("\nInvalid input, please input 1, 2 or 3\n")
            selectDevice = input("Select 1, 2 or 3 for the stepper motor, PWM LED or LCD Screen, respectively (-1 to exit): ")
    except: 
        KeyboardInterrupt 
    GPIO.cleanup()

if __name__ == "__main__":
    main()

