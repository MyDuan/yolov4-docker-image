FROM ubuntu:18.04

# 必要なパッケージをインストールします
# インストールによって生じる不要なファイルは削除します
RUN apt -y update && apt install -y --no-install-recommends \
    wget \
    python3-distutils \
    nginx \
    ca-certificates \
    libgomp1 \
    libglib2.0-0\
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1-mesa-dev \
    && apt clean

RUN ln -s /usr/bin/python3 /usr/bin/python
RUN ln -s /usr/bin/pip3 /usr/bin/pip

# スクリプトをコピーする
COPY . /opt/program
WORKDIR /opt/program

# pythonパッケージをインストールします
# キャッシュファイルは重たいので、削除しておきます
RUN wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py && \
    pip install -r requirements.txt && \
    rm -rf /root/.cache

# コンテナ起動時に実行するファイルを実行可能にする
RUN chmod +x /opt/program/serve

# 環境変数の設定
# pythonからの出力をバッファしないようにする（ログが早く届くようにするため）
ENV PYTHONUNBUFFERED=TRUE
# .pycファイルを作成しないようにする
ENV PYTHONDONTWRITEBYTECODE=TRUE
# スクリプトがあるディレクトリへパスを通しておく(コンテナ起動時に実行するtrainとserveファイルのパスを意識しないで済むようにするため)
ENV PATH="/opt/program:${PATH}"
