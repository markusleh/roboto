#!/usr/bin/env micropython
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, OUTPUT_D, Motor, SpeedPercent, MoveTank, OUTPUT_C
from ev3dev2.sensor import INPUT_2, INPUT_4
from myrobot import MyMoveTank
from ev3dev2.sensor.lego import TouchSensor, ColorSensor, UltrasonicSensor, InfraredSensor
from ev3dev2.led import Leds

from stopwatch import StopWatch
import time


#cs = ColorSensor()
#ts = TouchSensor()

#lift.on_for_degrees(SpeedPercent(10), -60)
def follow_for_ms(tank, ms):
    """
    ``tank``: the MoveTank object that is following a line
    ``ms`` : the number of milliseconds to follow the line
    """
    if not hasattr(tank, 'stopwatch') or tank.stopwatch is None:
        tank.stopwatch = StopWatch()
        tank.stopwatch.start()

    if tank.stopwatch.value_ms >= ms:
        tank.stopwatch = None
        return False
    else:
        return True


def follow_indef(tank):
    return True



class Roboto:
    def __init__(self):
        self.start_pos = -20
        #self.lift = MyMotor(OUTPUT_B)
        self.tank = MyMoveTank(OUTPUT_B, OUTPUT_C)
        self.tank.cs = ColorSensor(INPUT_2)
        self.tank.us = InfraredSensor()

    def set_initial(self):
        #self.lift.on_to_position(SpeedPercent(10), self.start_pos)
        print("Calibrating")
        time.sleep(2)
        self.tank.cs.calibrate_white()
        self.tank.us.mode = InfraredSensor.MODE_IR_PROX
        print("Done")

    def test_movement(self):
        self.tank.on_for_seconds(SpeedPercent(60), SpeedPercent(60), 2)

    def follow_line(self):
        try:
            # Follow the line for 4500ms
            self.tank.follow_line(
                kp=11.3, ki=0.05, kd=3.2,
                speed=SpeedPercent(30),
                follow_for=follow_indef,
                prox_treshold=40,
            )
        except Exception:
            self.tank.stop()
            raise



myRobot = Roboto()
myRobot.follow_line()

#print("Calibrate")
#time.sleep(5)
#cs.calibrate_white()
#print("Done")
#
#pos = lift.position_sp / lift.count_per_rot
#print(pos)
#lift.run_to_abs_pos()

