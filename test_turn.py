from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, OUTPUT_D, Motor, SpeedPercent, MoveTank, SpeedNativeUnits
import time



tank = MoveTank(OUTPUT_A, OUTPUT_B)

tank.on_for_degrees(SpeedPercent(-10), SpeedPercent(10), 645/2)
