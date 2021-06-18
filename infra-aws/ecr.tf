locals {
  ecr-lifecycle-policy = {
    rules = [
      {
        action = {
          type = "expire"
        }
        description  = "最新の5つを残してイメージを削除する"
        rulePriority = 1
        selection = {
          countNumber = 5
          countType   = "imageCountMoreThan"
          tagStatus   = "any"
        }
      },
    ]
  }
}

resource "aws_ecr_repository" "yolov4-model-ecr-repository" {
  encryption_configuration {
    encryption_type = "AES256"
  }

  image_scanning_configuration {
    scan_on_push = "true"
  }

  image_tag_mutability = "MUTABLE"
  name                 = "yolov4-model"
}

resource "aws_ecr_lifecycle_policy" "yolov4-model-ecr-repository" {
  repository = aws_ecr_repository.yolov4-model-ecr-repository.name
  policy     = jsonencode(local.ecr-lifecycle-policy)
}