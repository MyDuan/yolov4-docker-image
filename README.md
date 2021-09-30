# yolov4-docker-image

### local run steps:

- open a terminal
- run `$ cd models/predict`
- run `$ mkdir model`
  - prepare your own yolov4-416.tflite model file
      - you can see [here](https://github.com/hunglc007/tensorflow-yolov4-tflite#tensorflow-yolov4-tflite) to prepare it
      - you also can download it [here](https://drive.google.com/file/d/1w3s9ml_uiS51r07DrA9aJuwFoCfvfEIg/view?usp=sharing)
- run `$ . local_build_and_serve.sh`
- after the docker image is runing
- open a new terminal
- run `$ cd models/predict`
- prepare your own test.jpg
- run `$ . local_build_and_serve.sh test.jpg`


### create sagemaker endpoint

- `$cd infra-aws`
- s3 bucket:
  -  ```$ terraform apply `cat s3.tf | terraform fmt - | grep -E 'resource |module ' | tr -d '"' | awk '{printf("-target=%s.%s ",$2,$3);}'` ```
- ecr 
  -  ```$ terraform apply `cat ecr.tf | terraform fmt - | grep -E 'resource |module ' | tr -d '"' | awk '{printf("-target=%s.%s ",$2,$3);}'` ```
- iam role 
  -  ```$ terraform apply `cat iam.tf | terraform fmt - | grep -E 'resource |module ' | tr -d '"' | awk '{printf("-target=%s.%s ",$2,$3);}'` ```
- upload your model file to s3
- `$cd ../models/predict`
- push your docker images to ecr
    - `. build_and_push_to_ecr.sh {your account id}`
- sagemaker endpoint:
  -  ```$ terraform apply `cat sagemaker.tf | terraform fmt - | grep -E 'resource |module ' | tr -d '"' | awk '{printf("-target=%s.%s ",$2,$3);}'` ```
- test endpoint
    - `$ python test_sagemaker_endpoint.py`
