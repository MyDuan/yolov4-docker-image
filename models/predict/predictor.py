import os
import json
import flask

from algorithm.yolov4_recognizer import YoloV4

prefix = "/opt/program/"
model_path = os.path.join("/opt/ml/model", "yolov4-416.tflite")
app = flask.Flask(__name__)


class RecognizeService(object):
    """
    モデルをラップするクラス
    """
    model = None
    predictor = YoloV4(model_path=model_path)

    @classmethod
    def get_model(cls):
        """
        クラスが保持しているモデルを返します。モデルを読み込んでなければ読み込みます。
        """
        if cls.model == None:
            cls.model = cls.predictor.load_model()
        return cls.model

    @classmethod
    def predict(cls, image_path):
        """
        推論処理

        Args:
            input (array-like object): 推論を行う対象の特徴量データ"""
        interpreter = cls.get_model()
        print(interpreter)
        return cls.predictor.predict(image_path, interpreter)


@app.route("/ping", methods=["GET"])
def ping():
    """ヘルスチェックリクエスト
    コンテナが正常に動いているかどうかを確認する。ここで200を返すことで正常に動作していることを伝える。
    """
    health = RecognizeService.get_model() is not None

    status = 200 if health else 404
    return flask.Response(response="\n", status=status, mimetype="application/json")


@app.route("/invocations", methods=["POST"])
def transformation():
    """
    推論リクエスト

    画像データが送られてくるので、そのデータを推論する。推論結果をjsonデータに変換して返す。
    """

    if flask.request.content_type == "image/jpeg":
        with open("input.jpg", "wb") as f:
            f.write(flask.request.data)

    else:
        return flask.Response(
            response="This predictor only supports image data",
            status=415,
            mimetype="text/plain",
        )

    # 推論実行
    _, _, a_list, b_list = RecognizeService.predict("input.jpg")

    # レスポンスを返す
    result = json.dumps({"a_list": a_list, "b_list": b_list})
    return flask.Response(response=result, status=200, mimetype="text/json")
