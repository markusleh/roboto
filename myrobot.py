from ev3dev2.motor import LargeMotor, OUTPUT_C, OUTPUT_B, OUTPUT_D, Motor, SpeedPercent, MoveTank, SpeedNativeUnits
import time

# line follower functions
def follow_for_forever(tank):
    """
    ``tank``: the MoveTank object that is following a line
    """
    return True

turns = ["left", "left"]

class MyMoveTank(MoveTank):
    def __init__(self, left_motor_port, right_motor_port, desc=None, motor_class=LargeMotor):
        super().__init__(left_motor_port, right_motor_port, desc=None, motor_class=LargeMotor)

    def follow_line(self,
                    kp, ki, kd,
                    speed,
                    target_light_intensity=None,
                    follow_left_edge=True,
                    white=60,
                    off_line_count_max=20,
                    sleep_time=0.01,
                    follow_for=follow_for_forever,
                    prox_treshold=50,
                    **kwargs
                    ):
        """
        PID line follower
        ``kp``, ``ki``, and ``kd`` are the PID constants.
        ``speed`` is the desired speed of the midpoint of the robot
        ``target_light_intensity`` is the reflected light intensity when the color sensor
            is on the edge of the line.  If this is None we assume that the color sensor
            is on the edge of the line and will take a reading to set this variable.
        ``follow_left_edge`` determines if we follow the left or right edge of the line
        ``white`` is the reflected_light_intensity that is used to determine if we have
            lost the line
        ``off_line_count_max`` is how many consecutive times through the loop the
            reflected_light_intensity must be greater than ``white`` before we
            declare the line lost and raise an exception
        ``sleep_time`` is how many seconds we sleep on each pass through
            the loop.  This is to give the robot a chance to react
            to the new motor settings. This should be something small such
            as 0.01 (10ms).
        ``follow_for`` is called to determine if we should keep following the
            line or stop.  This function will be passed ``self`` (the current
            ``MoveTank`` object). Current supported options are:
            - ``follow_for_forever``
            - ``follow_for_ms``
        ``**kwargs`` will be passed to the ``follow_for`` function
        Example:
        .. code:: python
            from ev3dev2.motor import OUTPUT_A, OUTPUT_B, MoveTank, SpeedPercent, follow_for_ms
            from ev3dev2.sensor.lego import ColorSensor
            tank = MoveTank(OUTPUT_A, OUTPUT_B)
            tank.cs = ColorSensor()
            try:
                # Follow the line for 4500ms
                tank.follow_line(
                    kp=11.3, ki=0.05, kd=3.2,
                    speed=SpeedPercent(30),
                    follow_for=follow_for_ms,
                    ms=4500
                )
            except Exception:
                tank.stop()
                raise
        """
        assert self.cs, "ColorSensor must be defined"

        if target_light_intensity is None:
            target_light_intensity = self.cs.reflected_light_intensity

        integral = 0.0
        last_error = 0.0
        derivative = 0.0
        off_line_count = 0
        speed_native_units = speed.to_native_units(self.left_motor)
        MAX_SPEED = SpeedNativeUnits(self.max_speed)

        while follow_for(self, **kwargs):
            reflected_light_intensity = self.cs.reflected_light_intensity
            error = target_light_intensity - reflected_light_intensity
            integral = integral + error
            derivative = error - last_error
            last_error = error
            turn_native_units = (kp * error) + (ki * integral) + (kd * derivative)
            prox = self.us.proximity
            print("prox: {:^20} light: {:^20} turn_units: {:^20.2}".format(prox, reflected_light_intensity, turn_native_units))

            if not follow_left_edge:
                turn_native_units *= -1

            left_speed = SpeedNativeUnits(speed_native_units - turn_native_units)
            right_speed = SpeedNativeUnits(speed_native_units + turn_native_units)

            # Is distance to wall too close?
            if prox < prox_treshold:
                print("Too close")
                self.stop()
                raise LineFollowErrorLostLine("Lost line")

            # Have we lost the line?
            if reflected_light_intensity >= white:
                off_line_count += 1

                if off_line_count >= off_line_count_max:
                    self.stop()
                    print("Lost line")
                    raise LineFollowErrorLostLine("we lost the line")
            else:
                off_line_count = 0

            if sleep_time:
                time.sleep(sleep_time)

            self.on(left_speed, right_speed)

        self.stop()

# line follower classes
class LineFollowErrorLostLine(Exception):
    """
    Raised when a line following robot has lost the line
    """
    pass


class LineFollowErrorTooFast(Exception):
    """
    Raised when a line following robot has been asked to follow
    a line at an unrealistic speed
    """
    pass

#if left_speed > MAX_SPEED:
#    self.stop()
#    raise LineFollowErrorTooFast("The robot is moving too fast to follow the line")

#if right_speed > MAX_SPEED:
#    self.stop()
#    raise LineFollowErrorTooFast("The robot is moving too fast to follow the line")

