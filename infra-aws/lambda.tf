# =========================================
# Lambda
# =========================================

data "archive_file" "upload-lambda-archive-file" {
  type        = "zip"
  source_dir  = "./lambda/img-upload"
  output_path = "./lambda/img-upload.zip"
}

resource "aws_lambda_function" "img-upload-lambda" {
  filename         = "./lambda/img-upload.zip"
  function_name    = "img-upload-function"
  role             = aws_iam_role.img-upload-lambda-role.arn
  handler          = "lambda_function.handler"
  source_code_hash = data.archive_file.img-upload-lambda-archive-file.output_base64sha256
  runtime          = "python3.8"
  memory_size      = 128
  package_type     = "Zip"
  timeout          = 100
}