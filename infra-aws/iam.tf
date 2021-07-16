####################
# IAM role for sagemaker
####################

resource "aws_iam_role" "yolov4-model-execution-role" {
  name               = "yolov4-model-sagemaker-role"
  assume_role_policy = data.aws_iam_policy_document.yolov4-model-execution-assume-role-policy-doc.json
}

data "aws_iam_policy_document" "yolov4-model-execution-assume-role-policy-doc" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["sagemaker.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "yolov4-model-execution-sagemaker-role-policy-attach" {
  role       = aws_iam_role.yolov4-model-execution-role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

resource "aws_iam_role_policy_attachment" "yolov4-model-execution-role-policy-attach" {
  role       = aws_iam_role.yolov4-model-execution-role.name
  policy_arn = aws_iam_policy.yolov4-model-execution-role-policy.arn
}

resource "aws_iam_policy" "yolov4-model-execution-role-policy" {
  name = "yolov4-model-role-policy"
  policy = jsonencode({
    Statement = [
      {
        "Action" : [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ],
        "Effect" : "Allow",
        "Resource" : [
          "*"
        ]
      }
    ]
    Version = "2012-10-17"
  })
}


#######################
# IAM role for lambda #
#######################
# img-upload-lambda
resource "aws_iam_role" "img-upload-lambda-role" {
  name = "img-upload-lambda-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_policy" "img-upload-lambda-policy" {
  name = "img-upload-lambda-policy"
  path = "/"

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "GetS3data",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket",
        "s3:PutObject"
      ],
      "Resource": "*"
    }
  ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "img-upload-lambda-policy-attachment" {
  role       = aws_iam_role.img-upload-lambda-role.name
  policy_arn = aws_iam_policy.img-upload-lambda-policy.arn
}