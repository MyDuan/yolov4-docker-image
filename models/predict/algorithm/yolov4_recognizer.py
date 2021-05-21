import tensorflow as tf
import cv2
import numpy as np
from PIL import Image
import random
import os


class YoloV4:
    def __init__(self, model_path, input_size=416, score=0.4, iou=0.17):
        self.model_path = model_path
        self.input_size = input_size
        self.score = score
        self.iou = iou
        self.class_file_name = 'classes'

    def _boxes_filter(self, box_xywh, scores, input_shape=tf.constant([416, 416])):
        # filtered_scores = tf.where(list(zip(list(scores[0][:, 0] >= 0.4), list(scores[0][:, 1] >= 0.4))), scores[0], [[0, 0]])

        scores_max = tf.reshape(tf.math.reduce_max(scores, axis=-1), [1, -1])

        mask = scores_max >= self.score
        class_boxes = tf.boolean_mask(box_xywh, mask)
        pred_conf = tf.boolean_mask(scores, mask)
        class_boxes = tf.reshape(
            class_boxes, [tf.shape(scores)[0], -1, tf.shape(class_boxes)[-1]]
        )
        pred_conf = tf.reshape(
            pred_conf, [tf.shape(scores)[0], -1, tf.shape(pred_conf)[-1]]
        )

        box_xy, box_wh = tf.split(class_boxes, (2, 2), axis=-1)

        input_shape = tf.cast(input_shape, dtype=tf.float32)

        box_yx = box_xy[..., ::-1]
        box_hw = box_wh[..., ::-1]

        box_mins = (box_yx - (box_hw / 2.0)) / input_shape
        box_maxes = (box_yx + (box_hw / 2.0)) / input_shape
        boxes = tf.concat(
            [
                box_mins[..., 0:1],  # y_min
                box_mins[..., 1:2],  # x_min
                box_maxes[..., 0:1],  # y_max
                box_maxes[..., 1:2],  # x_max
            ],
            axis=-1,
        )
        # return tf.concat([boxes, pred_conf], axis=-1)
        return (boxes, pred_conf)

    def _read_class_names(self):
        names = {}
        with open(self.class_file_name, 'r') as data:
            for ID, name in enumerate(data):
                names[ID] = name.strip('\n')
        return names

    def _draw_bbox(self, image, bboxes, show_label=True):
        classes = self._read_class_names()
        print(classes)
        num_classes = len(classes)
        image_h, image_w, _ = image.shape
        hsv_tuples = [(1.0 * x / num_classes, 1.0, 1.0) for x in range(num_classes)]
        # colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
        # colors = list(map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)), colors))

        random.seed(0)
        # random.shuffle(colors)
        random.seed(None)

        out_boxes, out_scores, out_classes, num_boxes = bboxes
        ok_num = 0
        key_points = []
        for i in range(num_boxes[0]):
            if int(out_classes[0][i]) < 0 or int(out_classes[0][i]) > num_classes:
                continue
            score = out_scores[0][i]
            coor = out_boxes[0][i]
            coor[0] = int(coor[0] * image_h)
            coor[2] = int(coor[2] * image_h)
            coor[1] = int(coor[1] * image_w)
            coor[3] = int(coor[3] * image_w)
            a = max(abs(coor[3] - coor[1]), abs(coor[2] - coor[0]))
            b = min(abs(coor[3] - coor[1]), abs(coor[2] - coor[0]))
            if int(out_classes[0][i]) == 0 and score >= 0.8:
                key_points.append(coor)
                bbox_color = (0, 255, 0)
            else:
                bbox_color = (255, 0, 0)
            fontScale = 0.5
            class_ind = int(out_classes[0][i])
            bbox_thick = int(0.6 * (image_h + image_w) / 600)
            c1, c2 = (coor[1], coor[0]), (coor[3], coor[2])
            cv2.rectangle(image, c1, c2, bbox_color, bbox_thick)

            if show_label:
                if score >= 0.8:
                    bbox_mess = "%s: %.2f" % (
                        classes[class_ind],
                        score,
                    )
                t_size = cv2.getTextSize(
                    bbox_mess, 0, fontScale, thickness=bbox_thick // 2
                )[0]
                c3 = (c1[0] + t_size[0], c1[1] - t_size[1] - 3)
                cv2.rectangle(
                    image, c1, (np.float32(c3[0]), np.float32(c3[1])), bbox_color, -1
                )  # filled

                cv2.putText(
                    image,
                    bbox_mess,
                    (c1[0], np.float32(c1[1] - 2)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale,
                    (0, 0, 0),
                    bbox_thick // 2,
                    lineType=cv2.LINE_AA,
                )
        return image, key_points

    def _fit_and_mark(self, interpreter, image_path):
        original_image = cv2.imread(image_path)
        original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

        image_data = cv2.resize(original_image, (self.input_size, self.input_size))
        image_data = image_data / 255.0
        images_data = []
        for i in range(1):
            images_data.append(image_data)
        images_data = np.asarray(images_data).astype(np.float32)
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        interpreter.set_tensor(input_details[0]["index"], images_data)
        interpreter.invoke()
        pred = [
            interpreter.get_tensor(output_details[i]["index"])
            for i in range(len(output_details))
        ]
        boxes, pred_conf = self._boxes_filter(
            pred[0],
            pred[1],
            input_shape=tf.constant([self.input_size, self.input_size]),
        )
        (
            boxes,
            scores,
            classes,
            valid_detections,
        ) = tf.image.combined_non_max_suppression(
            boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
            scores=tf.reshape(
                pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])
            ),
            max_output_size_per_class=10,
            max_total_size=10,
            iou_threshold=self.iou,
            score_threshold=self.score,
        )

        pred_bbox = [
            boxes.numpy(),
            scores.numpy(),
            classes.numpy(),
            valid_detections.numpy(),
        ]
        print(pred_bbox)
        image, key_points = self._draw_bbox(original_image, pred_bbox)
        image = Image.fromarray(image.astype(np.uint8))
        return key_points, cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)

    def predict(self, interpreter, image_path):
        key_points, scr_output = self._fit_and_mark(interpreter, image_path)
        return scr_output, key_points

    def load_model(self):
        if not os.path.exists(self.model_path):
            return False
        interpreter = tf.lite.Interpreter(model_path=self.model_path)
        interpreter.allocate_tensors()
        return interpreter

if __name__ == '__main__':
    print("--------start----------")
    predictor = YoloV4(model_path="../model/yolov4-416.tflite")
    print("--------clasess----------")
    model = predictor.load_model()
    scr_output, key_points = predictor.predict(model, 'test.jpg')
    print("--------key----------")
    print(key_points)
    cv2.imshow("result", scr_output)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

