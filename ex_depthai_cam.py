import time
import cv2
import depthai as dai
import numpy as np

def getFrame(queue):
    # Get frame from queue
    frame = queue.get()
    # Convert frame to OpenCV format and return
    return frame.getCvFrame()

def getMonoCamera(pipeline, isLeft):
    # Configure mono camera
    mono = pipeline.createMonoCamera()

    # Set Camera Resolution
    mono.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)

    if isLeft:
        # Get left camera
        mono.setBoardSocket(dai.CameraBoardSocket.LEFT)
    else:
        # Get right camera
        mono.setBoardSocket(dai.CameraBoardSocket.RIGHT)
    return mono

def getStereoPair(pipeline, monoLeft, monoRight):
    # Configure stereo pair for depth estimation
    stereo = pipeline.createStereoDepth()
    # Checks occluded pixels and marks them as invalid
    # False 체크 시 퍼포먼스 향상
    stereo.setLeftRightCheck(False)

    # Configure left and right cameras to work as a stereo pair
    monoLeft.out.link(stereo.left)
    monoRight.out.link(stereo.right)

    return stereo

def mouseCallback(event, x, y, flags, param):
    global mouseX, mouseY
    if event == cv2.EVENT_LBUTTONDOWN:
        mouseX = x
        mouseY = y

if __name__ == '__main__':
    mouseX = 0
    mouseY = 640
    # Start defining a pipeline
    pipeline = dai.Pipeline()

    # Set up left and right cameras
    monoLeft = getMonoCamera(pipeline, isLeft=True)
    monoRight = getMonoCamera(pipeline, isLeft=False)

    # Combine left and right cameras to form a stereo pair
    stereo = getStereoPair(pipeline, monoLeft, monoRight)

    # Define and name output depth map
    xoutDepth = pipeline.createXLinkOut()
    xoutDepth.setStreamName("depth")

    xoutDisp = pipeline.createXLinkOut()
    xoutDisp.setStreamName("disparity")

    xoutRectifiedLeft = pipeline.createXLinkOut()
    xoutRectifiedLeft.setStreamName("rectifiedLeft")

    xoutRectifiedRight = pipeline.createXLinkOut()
    xoutRectifiedRight.setStreamName("rectifiedRight")

    stereo.disparity.link(xoutDisp.input)

    stereo.rectifiedLeft.link(xoutRectifiedLeft.input)
    stereo.rectifiedRight.link(xoutRectifiedRight.input)

    # Pipeline is defined, now we can connect to the device

    with dai.Device(pipeline) as device:
        # Outpit queues will be used to get the rgb frames and nn data from the outputs defined adove
        disparityQueue = device.getOutputQueue(name="disparity", maxSize=1, blocking=False)
        rectifiedLeftQueue = device.getOutputQueue(name="rectifiedLeft", maxSize=1, blocking=False)
        rectifiedRightQueue = device.getOutputQueue(name="rectifiedRight", maxSize=1, blocking=False)

        # Calculate a multiplier for colormapping disparity map
        disparityMultiplier = 255/stereo.getMaxDisparity()

        cv2.namedWindow("Stereo Pair")
        cv2.setMouseCallback("Stereo Pair", mouseCallback)

        # Variable use to toggle between side by side view and one frame view.
        sideBySide = False

        while True:

            # Get disparity map
            disparity = getFrame(disparityQueue)

            # Colormap disparity for display
            disparity = (disparity * disparityMultiplier).astype(np.uint8)
            disparity = cv2.applyColorMap(disparity, cv2.COLORMAP_JET)

            # Get left and right rectified frame
            leftFrame = getFrame(rectifiedLeftQueue)
            rightFrame = getFrame(rectifiedRightQueue)

            imOut1 = np.hstack((leftFrame, rightFrame))
            imOut2 = np.uint8(leftFrame/2 + rightFrame/2)


            imOut1 = cv2.cvtColor(imOut1, cv2.COLOR_GRAY2RGB)

            imOut1 = cv2.line(imOut1, (mouseX, mouseY), (1280, mouseY), (0, 0, 255), 2)
            imOut1 = cv2.circle(imOut1, (mouseX, mouseY), 2, (255, 255, 128), 2)

            imOut2 = cv2.cvtColor(imOut2, cv2.COLOR_GRAY2RGB)

            imOut2 = cv2.line(imOut2, (mouseX, mouseY), (1280, mouseY), (0, 0, 255), 2)
            imOut2 = cv2.circle(imOut2, (mouseX, mouseY), 2, (255, 255, 128), 2)

            cv2.imshow("stereo Camera", imOut1)
            cv2.imshow("stereo Pair", imOut2)
            cv2.imshow("Disparity", disparity)

            # Check for keyborad input
            key = cv2.waitKey(1)
            if key == ord('q'):
                break
            elif key == ord('t'):
                sideBySide = not sideBySide