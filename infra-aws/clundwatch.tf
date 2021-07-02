# =========================================
# Cloud Watch
# =========================================

resource "aws_cloudwatch_event_rule" "image-upload-event-rule" {
  name           = "image-upload-event-rule"
  description    = "image upload events"
  event_bus_name = "default"

  event_pattern = <<PATTERN
{
  "source": [
    "aws.s3"
  ],
  "detail-type": [
    "AWS API Call via CloudTrail"
  ],
  "detail": {
    "eventName": [
      "PutObject",
      "CopyObject"
    ],
    "eventSource": [
      "s3.amazonaws.com"
    ],
    "requestParameters": {
      "bucketName": [
        "${aws_s3_bucket.images-data.bucket}"
      ]
    }
  }
}
PATTERN

  is_enabled = "true"
}

resource "aws_cloudwatch_event_target" "image-upload-event-target" {
  target_id = "image-upload-event"
  arn       = aws_lambda_function.image-upload-lambda.arn
  rule      = aws_cloudwatch_event_rule.image-upload-event-rule.name

  input_transformer {
    input_paths = {
      S3BucketValue = "$.detail.requestParameters.bucketName"
      S3KeyValue    = "$.detail.requestParameters.key"
    }
    input_template = <<INPUT_TEMPLATE_EOF
{
  "Parameters" : {
    "S3bucket": <S3BucketValue>,
    "S3key": <S3KeyValue>
  }
}
INPUT_TEMPLATE_EOF
  }
}

resource "aws_lambda_permission" "image-upload-lambda" {
   statement_id  = "AllowExecutionFromCloudWatch"
   action        = "lambda:InvokeFunction"
   function_name = aws_lambda_function.image-upload-lambda.function_name
   principal     = "events.amazonaws.com"
   source_arn    = aws_lambda_function.image-upload-event-rule.arn
}