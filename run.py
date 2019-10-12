#!/usr/bin/env micropython
from ev3dev2.motor import LargeMotor, OUTPUT_C, OUTPUT_B, SpeedPercent, MoveTank, follow_for_ms
from ev3dev2.sensor import INPUT_2
from ev3dev2.sensor.lego import TouchSensor, ColorSensor
from ev3dev2.led import Leds
import time

#m1 = LargeMotor(OUTPUT_C)
#m2 = LargeMotor(OUTPUT_B)

tank = MoveTank(OUTPUT_C, OUTPUT_B)
tank.cs = ColorSensor()

print("Calibrate")
time.sleep(2)
tank.calibrate_white()
print("Done, following")

#tank_drive = MoveTank(OUTPUT_C, OUTPUT_B).follow_line(1, 1, 1, SpeedPercent(10))

try:
    # Follow the line for 4500ms
    tank.follow_line(
        kp=11.3, ki=0.05, kd=3.2,
        speed=SpeedPercent(30),
        ms=4500
    )
except Exception as e:
    print(e)
    tank.stop()
    raise

