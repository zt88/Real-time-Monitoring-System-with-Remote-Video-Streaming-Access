import time
import apriltag
import argparse
import cv2
from flask import Flask, render_template, Response, app

from camera_frame_processing import VideoCamera

'''
########################
    Input Arguments
########################
'''
# def get_args():
#     parser = argparse.ArgumentParser()
#
#     parser.add_argument("--width", help='frame width', type=int, default=1280)
#     parser.add_argument("--height", help='frame height', type=int, default=960)
#
#     parser.add_argument("--family", type=str, default='tag36h11')
#     # parser.add_argument("--nthreads", type=int, default=1)
#     # parser.add_argument("--quad_decimate", type=float, default=2.0)
#     # parser.add_argument("--quad_sigma", type=float, default=0.0)
#     # parser.add_argument("--refine_edges", type=int, default=1)
#     # parser.add_argument("--decode_sharpening", type=float, default=0.25)
#     # parser.add_argument("--debug", type=int, default=0)
#
#     args = parser.parse_args()
#
#     return args


'''
########################
    Motor Config
########################
'''
# pin number
vert_motor_pin = 19
hori_motor_pin = 12

# initial angles: middle position
vert_base_angle = 85 * 1000
hori_base_angle = 55 * 1000

# current angles
cur_vert_angle = 0
cur_hori_angle = 0

def motor_set():
    global cur_hori_angle, cur_vert_angle
    vert_sum_angle = vert_base_angle + cur_vert_angle * 1000
    hori_sum_angle = hori_base_angle + cur_hori_angle * 1000
    print("horizontal: pi.hardware_PWM(" + str(hori_motor_pin) + ", " + "50, " + str(hori_sum_angle) + ")")
    print("vertical: pi.hardware_PWM(" + str(vert_motor_pin) + ", " + "50, " + str(vert_sum_angle) + ")")


'''
########################
    Main Function
########################
'''
# def main():
#     args = get_args()
cur_hori_angle, cur_vert_angle
print("Initialize motor position:")
motor_set()

# arguments
frame_width = 1280
frame_height = 960
tag_families = 'tag36h11'


# turn on camera
capture = VideoCamera(flip=False)

# cv2.namedWindow("Monitor", cv2.WINDOW_NORMAL)
# cv2.resizeWindow("Monitor", 1280, 1080)

# cannot set via argument
# capture.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
# capture.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

# apriltag processing

options = apriltag.DetectorOptions(families=tag_families, border=1, nthreads=1, quad_decimate=1.0, quad_blur=0.0,
                                   refine_edges=True, refine_decode=False, refine_pose=False, debug=False,
                                   quad_contours=True)
detector = apriltag.Detector(options)


# App Globals (do not edit)
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # you can customze index.html here

def gen(camera):
    while True:
        # Camera Input
        # has_frame, frame = capture.read()
        # if not has_frame:
        #     print(" Cannot open camera to get frame!")
        #     break

        # frame = cv2.resize(frame, (frame_width, frame_height))
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        processed_frame = camera.get_frame()


        # apriltag processing
        result = detector.detect(processed_frame)  # input of apriltag must be grayscale


        # servo motor control
        if(len(result) != 0):
            # center coordinates of apriltag
            x = round(result[0].center[0])
            y = round(result[0].center[1])

            # hori motor angle: left low, right high, range 150
            if(x < frame_width / 2 - 150):
                cur_hori_angle = min(75, cur_hori_angle + 2)    # tag too right: camera turn right
            elif(x > frame_width / 2 + 150):
                cur_hori_angle = max(-75, cur_hori_angle - 2)   # tag too left: camera turn left

            # vert motor angle: low low, high high, range 150
            if (y < frame_height / 2 - 150):
                cur_vert_angle = min(75, cur_vert_angle + 2)  # tag too high: camera turn high
            elif (y > frame_height / 2 + 150):
                cur_vert_angle = max(-75, cur_vert_angle - 2)  # tag too left: camera turn left

            # control servo motors
            print("detected:")
            print("x = " + str(x) + ", y = " + str(y))
            motor_set()


        # Display video frame
        color_frame = cv2.cvtColor(processed_frame, cv2.COLOR_GRAY2BGR)
        cv2.imshow("Monitor", color_frame)  # output colorful frame


        # take photo if cry is detected
        try:
            cry_signal = open('cry.txt', 'r')
            cry = cry_signal.readline()
            print(cry)
            if cry == "True":
                print("cry")
                cv2.imwrite('cry.jpg', color_frame)
                open('cry.txt', 'w').close()
        except:
            pass


        # take photo if loud sound is detected
        try:
            loud_signal = open('loud_sound.txt', 'r')
            loud = loud_signal.readline()
            print(loud)
            if loud == "True":
                print("loud")
                cv2.imwrite('loud_sound.jpg', color_frame)
                open('loud_sound.txt', 'w').close()
        except:
            pass


        _, jpeg = cv2.imencode(".jpg", color_frame)
        jpeg = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + color_frame + b'\r\n\r\n')


        # Quit
        key = cv2.waitKey(3)  # unit is ms
        if key == 27:
            camera.release()
            cv2.destroyAllWindows()
            print("Pressed Esc.")
            break



@app.route('/video_feed')
def video_feed():
    return Response(gen(capture),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# Take a photo when pressing camera button
@app.route('/picture')
def take_picture():
    capture.take_picture()
    return "None"


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False)
