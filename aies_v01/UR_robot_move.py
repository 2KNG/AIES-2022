#!/usr/bin/env python3

README = """
Move your mouse pointer with your hand. 
The pointer moves when your hand is doing the ONE or TWO pose.
The difference between ONE and TWO is that in TWO the left button
is also pressed.

The mouse location is calculated from the index finger tip location.
An double exponential filter is used to limit jittering.

If you have multiple screens, you may have to modify the line:
monitor = get_monitors()[0]

"""

from interpreter import InterpreterHelper
#
print(README)
from HandTracker import HandTracker
from HandController import HandController
from interpreter import InterpreterHelper

# Controlling the mouse
try:
    from pynput.mouse import Button, Controller
except ModuleNotFoundError:
    print("To run this demo, you need the python package: pynput")
    print("Can be installed with: pip install pynput")
    import sys
    sys.exit()
mouse = Controller()

# Get screen resolution 
try:
    from screeninfo import get_monitors
except ModuleNotFoundError:
    print("To run this demo, you need the python package: screeninfo")
    print("Can be installed with: pip install screeninfo")
    import sys
    sys.exit()
monitor = get_monitors()[0] # Replace '0' by the index of your screen in case of multiscreen
print(monitor)

# Smoothing filter
import numpy as np
class DoubleExpFilter:
    def __init__(self,smoothing=0.65,
                 correction=1.0,
                 prediction=0.85,
                 jitter_radius=250.,
                 max_deviation_radius=540.,
                 out_int=False):
        self.smoothing = smoothing
        self.correction = correction
        self.prediction = prediction
        self.jitter_radius = jitter_radius
        self.max_deviation_radius = max_deviation_radius
        self.count = 0
        self.filtered_pos = 0
        self.trend = 0
        self.raw_pos = 0
        self.out_int = out_int
        self.enable_scrollbars = False
    
    def reset(self):
        self.count = 0
        self.filtered_pos = 0
        self.trend = 0
        self.raw_pos = 0
    
    def update(self, pos):
        raw_pos = np.asanyarray(pos)
        if self.count > 0:
            prev_filtered_pos = self.filtered_pos
            prev_trend = self.trend
            prev_raw_pos = self.raw_pos

        if self.count == 0:
            self.shape = raw_pos.shape
            filtered_pos = raw_pos
            trend = np.zeros(self.shape)
            self.count = 1
        elif self.count == 1:
            filtered_pos = (raw_pos + prev_raw_pos)/2
            diff = filtered_pos - prev_filtered_pos
            trend = diff*self.correction + prev_trend*(1-self.correction)
            self.count = 2
        else:
            # First apply jitter filter
            diff = raw_pos - prev_filtered_pos
            length_diff = np.linalg.norm(diff)
            if length_diff <= self.jitter_radius:
                alpha = pow(length_diff/self.jitter_radius,1.5)
                # alpha = length_diff/self.jitter_radius
                filtered_pos = raw_pos*alpha \
                                + prev_filtered_pos*(1-alpha)
            else:
                filtered_pos = raw_pos
            # Now the double exponential smoothing filter
            filtered_pos = filtered_pos*(1-self.smoothing) \
                        + self.smoothing*(prev_filtered_pos+prev_trend)
            diff = filtered_pos - prev_filtered_pos
            trend = self.correction*diff + (1-self.correction)*prev_trend
        # Predict into the future to reduce the latency
        predicted_pos = filtered_pos + self.prediction*trend
        # Check that we are not too far away from raw data
        diff = predicted_pos - raw_pos
        length_diff = np.linalg.norm(diff)
        if length_diff > self.max_deviation_radius:
            predicted_pos = predicted_pos*self.max_deviation_radius/length_diff \
                        + raw_pos*(1-self.max_deviation_radius/length_diff)
        # Save the data for this frame
        self.raw_pos = raw_pos
        self.filtered_pos = filtered_pos
        self.trend = trend
        # Output the data
        if self.out_int:
            return predicted_pos.astype(int)
        else:
            return predicted_pos

smooth = DoubleExpFilter(smoothing=0.3, prediction=0.1, jitter_radius=700, out_int=True)

# Camera image size
cam_width = 1152
cam_height = 648
#
#
# default_x = 0
# default_y = 0
# default_z = 0
#
# default_axis = [0.13, -0.400, 0.35, 0, 2.222, -2.222]
# default_axis_s = "p[0.13, -0.400, 0.35, 0, 2.222, -2.222]"

#
# ip = "192.168.213.80"
#
# ur_itp = InterpreterHelper(ip)
# if ur_itp.connect():
#     print("{} 연결완료".format(ip))
# if ur_itp.execute_command("clear_interpreter()"):
#     print("인터프리터 버퍼 초기화")

# command_id = ur_itp.execute_command("movej({})".format(default_axis_s))


def move(event):

    # global default_x
    # global default_y
    # global default_z
    _, _, z = event.hand.xyz
    x, y = event.hand.landmarks[8]
    # if x != 0 and y != 0 and z != 0 and z < 1000:
    #     move_x = (int(x) - cam_width/2)/1000
    #     move_y = (int(y) - cam_height/2)/1000
    #     move_z = int(z)/1000
    #
    #     command_line = "movej(p[{x},{y},{z},0,-3.14,0)".format(x=move_x, y=move_y, z=move_z)
    #     ur_itp.execute_command(command_line)
            # ur_itp.execute_command("clear_interpreter()")
            # command_id = ur_itp.execute_command(command_line)
    #     else:
    #         default_x = x
    #         default_y = y
    #         default_z = z
    #
    # print(default_x, default_y, default_z)
    print(x, y, z)
    # Use location of index
    x, y = event.hand.landmarks[8,:2]
    # print(x, y)
    # x /= cam_width
    # x = 1 - x
    # y /= cam_height
    # e = 0.15
    # p1 = monitor.width/(1-2*e)
    # q1 = -p1*e
    # mx = int(max(0, min(monitor.width-1, p1*x+q1)))
    # et = 0.05
    # eb= 0.4
    # p2 = monitor.height/(1-et-eb)
    # q2 = -p2*et
    # my = int(max(0, min(monitor.height-1, p2*y+q2)))
    # mx,my = smooth.update((mx,my))
    # mouse.position = (mx+monitor.x, my+monitor.y)
    # command_line = "movej( x, 0.2, z, 0, 2.222, -2.222])), a = {a}, v = {v}, t={t}, r={r})"
    # command_id = ur_itp.execute_command(command_line)

def press_release(event):
    pass
    # if event.trigger == "enter":
    #     mouse.press(Button.left)
    # elif event.trigger == "leave":
    #     mouse.release(Button.left)

def click(event):
    pass
    # mouse.press(Button.left)
    # mouse.release(Button.left)

def rock_n_roll(event):
    print("로큰롤!!!")



def touch(event):
        # global default_x
        # global default_y
        # global default_z
    _, _, z = event.hand.xyz
    x, y = event.hand.landmarks[8]
    if x != 0 and y != 0 and z != 0 and z < 1000:
        move_x = int(x) / 1000 - cam_width / 2
        move_y = int(y) / 1000 - cam_height / 2
        move_z = int(z) / 1000
        #
        # print(ur_itp.execute_command("movej(p[{x}, {y}, {z}, 0, -3.141592, 0)"))


    # global x
    # global y
    # global z
    # if x + y + z == 0 :
    #     x, y, z = event.hand.xyz
    #     default_x = x
    #     default_y = y
    #     default_z = z
    # move_x = default_x + x
    # move_x = default_y + y
    # move_x = default_z + z


    # print(event.hand.xyz)
    # print(event.hand.distance)

    pass

#
# def idk_trigger(event):
#     h = HandController()
#     h.config['tracker']['args']['nn_detection'] = False
#
# def ok_trigger(event):
#     h = HandController()
#     h.config['tracker']['args']['nn_detection'] = True

config = {
    'renderer' : {'enable': True},
    
    'pose_actions' : [

        {'name': 'MOVE', 'pose':['ONE','TWO'], 'callback': 'move', "trigger":"periodic", "first_trigger_delay":0.1, "next_trigger_delay": 0.5},
        # {'name': 'CLICK', 'pose':'TWO', 'callback': 'press_release', "trigger":"enter_leave", "first_trigger_delay":0.1},
        {'name': 'TOUCH', 'pose':'FIVE', 'callback': 'touch', "trigger":"periodic", "first_trigger_delay":0.1, "next_trigger_delay": 1},
        # {'name': 'FIVE', 'pose':'SNAIL', 'callback': 'idk_trigger', "trigger":"enter", "first_trigger_delay":1, "next_trigger_delay": 1},
        # {'name': 'ROCK', 'pose':'SNAIL', 'callback': 'idk_trigger', "trigger":"enter", "first_trigger_delay":1, "next_trigger_delay": 1},
        # {'name': 'ROCK', 'pose': 'PROMISE', 'callback': 'ok_trigger', "trigger": "enter",
        #  "first_trigger_delay": 1, "next_trigger_delay": 1},
    ]
}

HandController(config).loop()