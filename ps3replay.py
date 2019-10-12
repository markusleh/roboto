#!/usr/bin/env python3
__author__ = 'Anton Vanhoucke'
 
import evdev
import ev3dev.auto as ev3
import threading
<<<<<<< HEAD
import time
from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C, SpeedNativeUnits
=======
from ev3dev2.button import Button
>>>>>>> a8c48c65c6d579f8ca2327fecb62b4938fa7c3bb
from queue import Queue

 
## Some helpers ##
def scale(val, src, dst):
    """
    Scale the given value from the scale of src to the scale of dst.
 
    val: float or int
    src: tuple
    dst: tuple
 
    example: print(scale(99, (0.0, 99.0), (-1.0, +1.0)))
    """
    return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]
 
def scale_stick(value):
    return scale(value,(0,255),(-100,100))
 
def clamp(value, floor=-100, ceil=100):
    """
    Clamp the value within the floor and ceiling values.
    """
    return max(min(value, ceil), floor)
 
## Initializing ##
print("Finding ps3 controller...")
devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
for device in devices:
    if device.name == 'PLAYSTATION(R)3 Controller':
        ps3dev = device.fn
 
gamepad = evdev.InputDevice(ps3dev)
 
# Initialize globals
speed = 0
turn = 0
drop = 0
hand = 0
record = Queue()

global replay
replay = False

global do_record
do_record = False

global running
running = True

 
# Within this thread all the motor magic happens
class MotorThread(threading.Thread):
    def __init__(self):
        # Add more sensors and motors here if you need them
<<<<<<< HEAD
        #self.left_motor = ev3.LargeMotor(ev3.OUTPUT_C)
        #self.right_motor = ev3.LargeMotor(ev3.OUTPUT_B)
        self.tank = MoveTank(OUTPUT_C, OUTPUT_B)

=======
        self.left_motor = ev3.LargeMotor(ev3.OUTPUT_C)
        self.right_motor = ev3.LargeMotor(ev3.OUTPUT_B)
        self.hand_motor = ev3.MediumMotor(ev3.OUTPUT_A)
        #self.drop_motor = ev3.MediumMotor(ev3.OUTPUT_D)
        self.replay = replay # Are we recording or not?
	    self.handpos=self.hand_motor.position
	    self.handmin=0
	    self.handmax=0
>>>>>>> a8c48c65c6d579f8ca2327fecb62b4938fa7c3bb
        threading.Thread.__init__(self)

    def calibrate(self):
         while True:
            if "up" in button.buttons_pressed:
				break
         self.handmin=self.hand_motor.position

         while True:
            if "up" in button.buttons_pressed:
				break
         self.handmax=self.hand_motor.position

    def run(self):
        print("Engine running!")
		if self.handmax!=0:
			self.calibrate()
        # Change this function to suit your robot. 
        # The code below is for driving a simple tank.
        while running:
            # We have run out of records
            if replay and record.empty():
                continue
            # Do normal replay
            elif replay:
                cur_record = record.get()
                left_dc = cur_record[0][0]
                left_speed = SpeedNativeUnits(cur_record[0][1])
                right_dc = cur_record[1][0]
                right_speed = SpeedNativeUnits(cur_record[1][1])
                print(left_speed, left_dc, right_speed, right_dc)
                self.tank.right_motor.on_to_position(right_speed, right_dc)
                self.tank.left_motor.on_to_position(left_speed, left_dc, block=True)

            # Run by controller
            else:
                right_dc = clamp(-speed-turn)
                left_dc = clamp(-speed+turn)
                self.tank.on(left_dc, right_dc)
                if do_record:
                    record.put(([self.tank.left_motor.position, self.tank.left_motor.speed], [self.tank.right_motor.position, self.tank.left_motor.speed]))



            #self.right_motor.on_fo(duty_cycle_sp=right_dc)
            #self.left_motor.run_direct(duty_cycle_sp=left_dc)

			if hand:
				self.movehand()
				hand=0
            self.movedrop(drop)

        #self.right_motor.stop()
        #self.left_motor.stop()
        self.tank.stop()


    def movehand(self):
        if abs(self.hand_motor.position - self.handmax) < 10:
            self.hand_motor.run_to_abs_pos(position_sp=self.handmin, speed_sp=100)
        elif abs(self.hand_motor.position - self.handmin) < 10:
            self.hand_motor.run_to_abs_pos(position_sp=self.handmax,speed_sp=100)

    def movedrop(self, direction):
        if direction == 1:
            pass
            #self.hand_motor.run_to_abs_pos(position_sp=self.dropraised, speed_sp=100)
        elif direction == 2:
            pass
            #self.hand_motor.run_to_abs_pos(position_sp=self.dropraised-50, speed_sp=100)
        else:
            pass
            #self.hand_motor.run_to_abs_pos(position_sp=self.dropraised-100,speed_sp=100)
        #if direction != self.hand:
        #    self.hand_motor.run_to_abs_pos(position_sp=self.hand_motor.position + direction*50, speed_sp=100)
        #    self.hand = direction



# Multithreading magics
button = Button()
motor_thread = MotorThread()
motor_thread.setDaemon(True)
motor_thread.start()


from queue import Empty

def clear(q):
    try:
        while True:
            q.get_nowait()
    except Empty:
        pass
 
for event in gamepad.read_loop():   #this loops infinitely
    if event.type == 3:             #One of the sticks is moved
        # Add if clauses here to catch more values for your robot.
        if event.code == 4:         #Y axis on right stick
            speed = scale_stick(event.value)
        if event.code == 3:         #X axis on right stick
            turn = scale_stick(event.value)
        #if event.code == 0:
            #drop = scale_stick(event.value)
        #if event.code == 1:
            #hand = scale_stick()

    if event.type == 1:
        pass
        #print(event.code)
        #print(event.value)


    if record.empty() and replay:
        replay = False
        do_record = False

    # Kuutio käsi alas, x
    if event.type == 1 and event.code == 304 and event.value == 1:
        hand = -1

    # Kuutio käsi ylös, kolmio
    if event.type == 1 and event.code == 307 and event.value == 1:
        hand = 1

    # Drop hand, nuoliylös
    if event.type == 1 and event.code == 544 and event.value == 1:
        drop += 1 
        if drop == 3:
            drop = 0

    # start replay, ympyrä
    if event.type == 1 and event.code == 305 and event.value == 1:
        print("Start replay")
        replay = True
        do_record = False

    # start record, neliö
    if event.type == 1 and event.code == 308 and event.value == 1:
        print("Start record")
        clear(record)
        replay = False
        do_record = True
