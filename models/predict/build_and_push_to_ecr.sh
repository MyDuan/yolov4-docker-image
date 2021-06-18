%%sh

# repository
repository_name=yolov4-model

# ファイルを実行可能にする
chmod +x serve

# アカウントID取得
account=$1

# リージョン名
region='ap-northeast-1'

# リポジトリarn
fullname="${account}.dkr.ecr.${region}.amazonaws.com/${repository_name}:latest"

echo $fullname

# ECRへのログインコマンドを取得し、ログインする
aws ecr get-login-password --region ${region} | docker login --username AWS --password-stdin "https://${account}.dkr.ecr.${region}.amazonaws.com"

# コンテナイメージをビルドする
docker build  -t ${repository_name} .
docker tag ${repository_name} ${fullname}

# ECRのリポジトリへプッシュする
docker push ${fullname}