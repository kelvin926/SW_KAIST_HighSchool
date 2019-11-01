# 소프트웨어 동아리 경진대회 Main Python 파일
# 파일 이름: Object_detection_picamera.py
# 제작: 장현서(kelvin926@naver.com) / 일산대진고등학교 2학년 '재간둥이'팀
# 최근 업데이트: 19.11.1 (Ver 1.5)
# Original Code Made by Evan(EdjeElectronics)


#-*- coding:utf-8 -*-


# 패키지들
from utils import visualization_utils as vis_util
from utils import label_map_util
import os
import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import tensorflow as tf
import argparse
import sys

#아두이노 연계
import serial

#소리 출력
import pygame
import time

#키보드 연결
#import keyboard (오류로 인해 비활성화)


ser = serial.Serial('/dev/ttyACM0', 9600)


'''
----아두이노 기본 코드 ----
void setup(){
    serial.begin(9600);
}
void loop(){
    Serial.println("hello Pi");
    delay(1000);
}
'''

# 카메라 세팅
IM_WIDTH = 1280
IM_HEIGHT = 720
# IM_WIDTH = 640
# IM_HEIGHT = 480
'''
2160p =  3840 * 2160
1440p = 2560 * 1440
1080p = 1920 * 1080
720p = 1280 * 720
480p = 854 * 480
360p = 640 * 360
'''
# --usbcam => usb웹캠 사용,
# 기본 : 내장 카메라 사용
camera_type = 'picamera'
parser = argparse.ArgumentParser()
parser.add_argument('--usbcam', help='Use a USB webcam instead of picamera',
                    action='store_true')
args = parser.parse_args()
if args.usbcam:
    camera_type = 'usb'

# object_detection 폴더 지정
sys.path.append('..')

# utilites 모듈 입력 (선택)

# 러닝된 모델 이름
MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09'

# 작업 폴더 위치 확인
CWD_PATH = os.getcwd()

# frozen_detection_graph.pb 의 위치, 이 파일은 오브젝트 탐지에 이용됨
PATH_TO_CKPT = os.path.join(CWD_PATH, MODEL_NAME, 'frozen_inference_graph.pb')

# 레이블 파일 위치
PATH_TO_LABELS = os.path.join(CWD_PATH, 'data', 'mscoco_label_map.pbtxt')

# 한번에 최대 몇개의 오브젝트를 탐지할지
NUM_CLASSES = 90

# 레이블 파일 로드
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(
    label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

# 메모리에 텐서플로우 모델 위치
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    sess = tf.Session(graph=detection_graph)


# 입/출력 데이터 정의

# tensor 이미지 로드
image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

# detection boxes, scores, classes 출력
# 각 box는 매 회 감지를 나타냄
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

# 각 점수는 각 객체에 대한 신뢰도를 나타냄
# 등급 레이블과 함께 결과 영상에 점수가 표시됨
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

# 감지된 오브젝트 수
num_detections = detection_graph.get_tensor_by_name('num_detections:0')

# 프레임 계산 초기화
frame_rate_calc = 1
freq = cv2.getTickFrequency()
font = cv2.FONT_HERSHEY_SIMPLEX

# 카메라, 감지모델 초기화
# 파이 내장 카메라와 usb웹캠 구동 방식이 상이함

### 파이 내장 카메라 ###################################################################
if camera_type == 'picamera':
    # 감지 모델 초기화, 입력된 RAW데이터 정의
    camera = PiCamera()
    camera.resolution = (IM_WIDTH, IM_HEIGHT)
    camera.framerate = 10
    rawCapture = PiRGBArray(camera, size=(IM_WIDTH, IM_HEIGHT))
    rawCapture.truncate(0)

    for frame1 in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

        t1 = cv2.getTickCount()

        # 프레임 획득 및 프레임 치수를 형상화: [1, None, None, 3]
        # 단일 열 배열로, 열의 각 항목에는 픽셀 RGB 값이 있음
        frame = np.copy(frame1.array)
        frame.setflags(write=1)
        frame_expanded = np.expand_dims(frame, axis=0)

        # 감지 모델을 이용하여 실제 연산
        (boxes, scores, classes, num) = sess.run(
            [detection_boxes, detection_scores, detection_classes, num_detections],
            feed_dict={image_tensor: frame_expanded})

        # 감지된 부분을 프레임에 Draw
        vis_util.visualize_boxes_and_labels_on_image_array(
            frame,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            category_index,
            use_normalized_coordinates=True,
            line_thickness=8,
            min_score_thresh=0.40)

        cv2.putText(frame, "FPS: {0:.2f}".format(
            frame_rate_calc), (30, 50), font, 1, (255, 255, 0), 2, cv2.LINE_AA)

        # 프레임에 Draw된 부분을 실제 화면에 표시
        cv2.imshow('Object detector', frame)

        t2 = cv2.getTickCount()
        time1 = (t2 - t1) / freq
        frame_rate_calc = 1 / time1

        # 키보드의 Q 버튼을 통해 종료
        if cv2.waitKey(1) == ord('q'):
            break

        if cv2.waitKey(1) == ord('r'): #사고 감지 시뮬레이션용 키보드 입력 : R
            #cv2.putText(img, 'WARNING', (10,500), cv2.FONT_HERSHEY_SIMPLEX, 4, (255,255,255), 2)
            break

        rawCapture.truncate(0) #다음 프레임 준비 클리어 작업(?)

    camera.close()

### USB webcam ###
elif camera_type == 'usb':
    # 웹캠 입력값 초기화
    camera = cv2.VideoCapture(0)
    ret = camera.set(3, IM_WIDTH)
    ret = camera.set(4, IM_HEIGHT)

    while(True):

        t1 = cv2.getTickCount()

        # 프레임 획득 및 프레임 치수를 형상화: [1, None, None, 3]
        # 단일 열 배열로, 열의 각 항목에는 픽셀 RGB 값이 있음
        ret, frame = camera.read()
        frame_expanded = np.expand_dims(frame, axis=0)

        # 실제로 감지된 이미지를 넣어 모델에 돌림
        (boxes, scores, classes, num) = sess.run(
            [detection_boxes, detection_scores, detection_classes, num_detections],
            feed_dict={image_tensor: frame_expanded})

        # 감지된 부분을 프레임에 Draw
        vis_util.visualize_boxes_and_labels_on_image_array(
            frame,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            category_index,
            use_normalized_coordinates=True,
            line_thickness=8,
            min_score_thresh=0.85)

        cv2.putText(frame, "FPS: {0:.2f}".format(
            frame_rate_calc), (30, 50), font, 1, (255, 255, 0), 2, cv2.LINE_AA)

        # 프레임에 Draw된 부분을 실제 화면에 표시
        cv2.imshow('Object detector', frame)

        t2 = cv2.getTickCount()
        time1 = (t2 - t1) / freq
        frame_rate_calc = 1 / time1

        # 키보드의 Q버튼을 통해 종료
        if cv2.waitKey(1) == ord('q'):
            break

        if cv2.waitKey(1) == ord('r'): #사고 감지 시뮬레이션용 키보드 입력 : R
            #cv2.putText(img, 'WARNING', (10,500), cv2.FONT_HERSHEY_SIMPLEX, 4, (255,255,255), 2)
            break

    camera.release()

cv2.destroyAllWindows()
print('print Test')
