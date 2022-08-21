#!/usr/bin/env python3

README = """
Emulate keystrokes with hand poses to play Tetris.

The game of Tetris is there: https://tetris.com/play-tetris/

The hand poses used to play are:
- FIVE (open hand) to move left or right the falling piece.
The direction of the move is given by the rotation of the hand.
- ONE to rotate the piece.
- FIST (closed hand) to accelarate the fall.

Good luck !
"""

print(README)

from HandController import HandController
from interpreter import InterpreterHelper


# Controlling the keyboard
try:
    from pynput.keyboard import Key, Controller
except ModuleNotFoundError:
    print("To run this demo, you need the python package: pynput")
    print("Can be installed with: pip install pynput")
    import sys
    sys.exit()

kbd = Controller()


ip = "192.168.213.80"

ur_itp = InterpreterHelper(ip)
if ur_itp.connect():
    print("{} 연결완료".format(ip))
if ur_itp.execute_command("clear_interpreter()"):
    print("인터프리터 버퍼 초기화")

command_id = ur_itp.execute_command("movej(p[0.132, -0.298, 0.85, 0, -3.141592, 0)")



def move(event):
    event.print_line()
    rotation = event.hand.rotation
    if -1 < rotation < -0.2:
        ur_itp.execute_command("movej({p[{x}, {y}, 0.85, 0, -3.141592, 0)")
    elif 0.4 < rotation < 1.5:
        press_key(Key.left)

def rotate(event):
    event.print_line()
    press_key(Key.up)
    
def down(event): 
    event.print_line()
    press_key(Key.down)

config = {
    'renderer' : {'enable': True},
    
    'pose_actions' : [

        {'name': 'MOVE', 'pose':'FIVE', 'callback': 'move', "trigger":"periodic", "first_trigger_delay":0, "next_trigger_delay": 0.2},
        {'name': 'ROTATE', 'pose':'ONE', 'callback': 'rotate', "trigger":"periodic", "first_trigger_delay":0, "next_trigger_delay": 0.4},
        {'name': 'DOWN', 'pose':'FIST', 'callback': 'down', "trigger":"periodic", "first_trigger_delay":0.05, "next_trigger_delay": 0.05}
    ]
}

HandController(config).loop()