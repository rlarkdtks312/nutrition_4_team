yolo v5 code

yolo v5의 깃허브를 clone하고 필수 패키지와 pytorch를 install 한다.

git clone https://github.com/ultralytics/yolov5  # clone
cd yolov5
pip install -r requirements.txt  # install


inferrence

import torch

# Model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # or yolov5m, yolov5l, yolov5x, custom

# Images
img = 'https://ultralytics.com/images/zidane.jpg'  # or file, Path, PIL, OpenCV, numpy, list

# Inference
results = model(img)

# Results
results.print()  # or .show(), .save(), .crop(), .pandas(), etc.

python detect.py --source 0   # 웹캠 
                          img.jpg   # 이미지 
                          vid.mp4   # 비디오 
                          경로/   # 디렉토리 
                          경로/ * .jpg   # glob 
                          ' https://youtu.be/Zgi9g1ksQHc '   # YouTube 
                          ' rtsp://example .com/media.mp4 '   # RTSP, RTMP, HTTP 스트림

