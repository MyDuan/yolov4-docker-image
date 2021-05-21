absolute_model_path_in_host=$(pwd)$line/model

docker build -t yolov4-model .

docker run -p 8080:8080 --mount type=bind,src=$absolute_model_path_in_host,dst=/opt/ml/model yolov4-model serve
