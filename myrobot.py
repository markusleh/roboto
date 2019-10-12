from ev3dev2.motor import LargeMotor, OUTPUT_C, OUTPUT_B, OUTPUT_D, Motor, SpeedPercent, MoveTank, SpeedNativeUnits
import time
from ev3dev2.button import Button
from ev3dev2.sound import Sound

# line follower functions
def follow_for_forever(tank):
    """
    ``tank``: the MoveTank object that is following a line
    """
    return True

turns = ["right"]
#TURN_DEG = 322
TURN_DEG = 280



class MyMoveTank(MoveTank):
    def __init__(self, left_motor_port, right_motor_port, desc=None, motor_class=LargeMotor):
        self.cur_turn_i = 0
        self.button = Button()
        super().__init__(left_motor_port, right_motor_port, desc=None, motor_class=LargeMotor)

    def get_next_turn(self):
        deg_p = 0
        speed_left = 0
        speed_rigth = 0

        # Next direction
        dir = turns[self.cur_turn_i]
        if dir == "left":
            deg_p = -TURN_DEG
            speed_left  = SpeedPercent(-10)
            speed_rigth = SpeedPercent(10)

        elif dir == "right":
            deg_p = TURN_DEG
            speed_left  = SpeedPercent(10)
            speed_rigth = SpeedPercent(-10)

        self.cur_turn_i = self.cur_turn_i + 1

        return [speed_left, speed_rigth, deg_p]


    def on_until_target(
            self,
            target_light_intensity
        ):
        while self.cs.reflected_light_intensity < target_light_intensity - 5:
            self.on(SpeedPercent(30), SpeedPercent(30))

        self.stop()
        return




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
        print(speed_native_units)
        MAX_SPEED = SpeedNativeUnits(self.max_speed)
        button = Button()

        while follow_for(self, **kwargs):
            if "down" in button.buttons_pressed:
                self.stop()
                return

            reflected_light_intensity = self.cs.reflected_light_intensity
            error =  reflected_light_intensity - target_light_intensity
            integral = integral + error
            derivative = error - last_error

            print("target: {:^20} light: {:^20}, deri: {:^5}, integral: {:^5}".format(
                target_light_intensity,
                reflected_light_intensity,
                derivative,
                integral
            ))

            if derivative > 6: #or abs(integral) > 100:
                self.stop()
                print("Wrong way")
                return
            #    self.on_for_degrees(SpeedPercent(-10), SpeedPercent(10), 100)
            #    integral = 0
            #    last_error = 0
            #    derivative = 0
            #    off_line_count = 0
            #    time.sleep(1)
            #    continue

            if integral > 150:
                self.stop()
                print("Too high integral")
                integral = -100.0
                # We are correcting heading too much to the left, make correction to right
                self.on_for_degrees(SpeedPercent(30), SpeedPercent(-30), 150)
                self.on_until_target(target_light_intensity)
                continue

            last_error = error
            turn_native_units = (kp * error) + (ki * integral) + (kd * derivative)


            if not follow_left_edge:
                turn_native_units *= -1

            left_speed = SpeedNativeUnits(speed_native_units - turn_native_units)
            right_speed = SpeedNativeUnits(speed_native_units + turn_native_units)


            # Is distance to wall too close?
            #if self.us.proximity < prox_treshold:
            #    print("Too close")
            #    self.stop()
            #    in_line = reflected_light_intensity >= white

            #    turn_help = self.get_next_turn()
            #    # If we are still in line, safe to turn straight away
            #    if in_line:
            #        self.on_for_degrees(turn_help[0], turn_help[1], turn_help[2])

            #    else:
            #        self.on_for_seconds(SpeedPercent(-10), SpeedPercent(-10), 1)
            #        self.on_for_degrees(turn_help[0], turn_help[1], turn_help[2])

            #    # Reset values for new straigth line
            #    integral = 0
            #    last_error = 0
            #    derivative = 0
            #    off_line_count = 0
            #    time.sleep(2)
            #    continue


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

