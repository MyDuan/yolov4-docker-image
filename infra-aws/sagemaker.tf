####################
# SageMaker Model
####################
resource "aws_sagemaker_model" "yolov4-model" {
  name               = "yolov4-model"
  execution_role_arn = aws_iam_role.yolov4-model-execution-role.arn

  primary_container {
    image          = "${aws_ecr_repository.yolov4-model-ecr-repository.repository_url}:latest"
    model_data_url = "https://s3-ap-northeast-1.amazonaws.com/${aws_s3_bucket.yolov4-models.bucket}/yolov4-416.tar.gz"
  }
}

####################
# SageMaker EndpointConfig
####################

resource "aws_sagemaker_endpoint_configuration" "yolov4-model-endpoint-config" {
  name = "yolov4-model-endpoint-config"

  production_variants {
    variant_name           = "yolov4-model-variant"
    model_name             = aws_sagemaker_model.yolov4-model.name
    initial_instance_count = 1
    instance_type          = "ml.t2.medium"
  }
}

####################
# SageMaker Endpoint
####################

resource "aws_sagemaker_endpoint" "yolov4-model-endpoint" {
  name                 = "yolov4-model-endpoint"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.yolov4-model-endpoint-config.name
}
