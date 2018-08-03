import tensorflow as tf
from tf_trt_models.detection import download_detection_model, build_detection_graph
import tensorflow.contrib.tensorrt as trt

class Model:
    def __init__(self, trt_graph, input_names):
        self.config = tf.ConfigProto()
        self.config.gpu_options.allow_growth = True

        self.tf_session = tf.Session(config=self.config)
        tf.import_graph_def(trt_graph, name='')

        self.tf_input = self.tf_session.graph.get_tensor_by_name(input_names[0] + ':0')
        self.tf_scores = self.tf_session.graph.get_tensor_by_name('scores:0')
        self.tf_boxes = self.tf_session.graph.get_tensor_by_name('boxes:0')
        self.tf_classes = self.tf_session.graph.get_tensor_by_name('classes:0')
        
    def predict(self, image):
        scores, boxes, classes = self.tf_session.run([self.tf_scores, self.tf_boxes, self.tf_classes], feed_dict={
            self.tf_input: image[None, ...]
        })
        return scores[0], boxes[0], classes[0]
        
    def getTFSession():
        return self.tf_session
