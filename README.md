# yolov4-docker-image

### steps:

- open a terminal
- run $ cd models/predict
- run $ mkdir model
  - prepare your own yolov4-416.tflite model file
- run $ . local_build_and_serve.sh
- after the docker image is runing
- open a new terminal
- run $ cd models/predict
- prepare your own test.jpg
- run $ . local_build_and_serve.sh test.jpg