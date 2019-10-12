import ev3dev2
import ev3dev2.auto as ev3
import threading

def scale(val, src, dst):
    return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

def scale_stick(value):
    return scale(value, (0,255), (-100,100))

devices = [ev3dev2.InputDevice(fn) for fn in ev3dev2.list_devices()]
for device in devices:
    if device.name == "PLAYSTATION(R)3 Controller":
        ps3dev = device.fn

gamepad = evdev.InputDevice(ps3dev)
speed = 0
running = True

for event in gamepad.read_loop():
    speed = scale_stick(event.value)
    print("type: %s, value: %s" %(event.code, speed))
    if event.type == 3:
        if event.code == 5:
            speed = scale_stick(event.value)
            print(speed)
    if event.type == 1 and event.code == 302 and event.value == 1:
        print("X button is pressed. Stopping")
        running = False
        break
