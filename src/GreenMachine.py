print "Loading...\n"

import argparse, pip

parser = argparse.ArgumentParser(description='GreenMachine')
parser.add_argument('--screen', action="store_true")
parser.add_argument('--build', action="store_true")
parser.add_argument('--calibrate', action="store_true")
parser.add_argument('--install', action="store_true")
screen_mode = parser.parse_args().screen
build_graph = parser.parse_args().build

if parser.parse_args().install:
    pip.main(['install', 'numpy'])
    pip.main(['install', 'opencv-python'])
    pip.main(['install', 'matplotlib'])
    pip.main(['install', 'pillow'])
    pip.main(['install', 'tensorflow-1.8.0-cp27-cp27mu-linux_aarch64.whl'])

from Camera import Camera
from Model import Model
import cv2, thread, copy, time, os, difflib, sys, json
import numpy as np
from tf_trt_models.detection import download_detection_model, build_detection_graph
import tensorflow.contrib.tensorrt as trt
import tensorflow as tf

# Turn off TensorFlow debug logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

# Directory of the model data
DATA_DIR = os.path.abspath('../models/LunchNet/')

# Relates class numbers to their colors
COLOR_DICT = {
    1: (73, 135, 71),
    2: (244, 65, 181),
    3: (73, 135, 71),
    4: (73, 135, 71),
    5: (244, 65, 181),
    6: (73, 135, 71),
    7: (73, 135, 71),
    8: (244, 134, 66),
    9: (66, 134, 244)
}

# Relates class numbers to their full names
CLASS_DICT = {
    1: "Cup/Soup Bowl (Compost)",
    2: "Silverware (Reusable)",
    3: "Plastic Utensil (Compost)",
    4: "Container/To-Go Box (Compost)",
    5: "Bowl/Plate (Reusable)",
    6: "Napkin (Compost)",
    7: "Stick (Compost)",
    8: "Plastic Bottle (Recycle)",
    9: "Food/Candy Wrapper (Non-Compost)"
}

# Relates class numbers to their render order
ORDER_DICT = {
    1: 7,
    2: 2,
    3: 3,
    4: 6,
    5: 9,
    6: 1,
    7: 8,
    8: 4,
    9: 5
}

prev_bboxes = []
prev_classes = []
on_prev_frame = []

def createModel(config_path, checkpoint_path, graph_path):
    """ Create a TensorRT Model.
    config_path (string) - The path to the model config file.
    checkpoint_path (string) - The path to the model checkpoint file(s).
    graph_path (string) - The path to the model graph.
    returns (Model) - The TRT model built or loaded from the input files.
    """

    global build_graph, prev_classes

    trt_graph = None
    input_names = None
    
    if build_graph:
        frozen_graph, input_names, output_names = build_detection_graph(
            config=config_path,
            checkpoint=checkpoint_path
        )
    
        trt_graph = trt.create_inference_graph(
            input_graph_def=frozen_graph,
            outputs=output_names,
            max_batch_size=1,
            max_workspace_size_bytes=1 << 25,
            precision_mode='FP16',
            minimum_segment_size=50
        )

        with open(graph_path, 'wb') as f:
            f.write(trt_graph.SerializeToString())

        with open('config.txt', 'r+') as json_file:  
            data = json.load(json_file)
            data['model'] = []
            data['model'] = [{'input_names': input_names}]
            json_file.seek(0)
            json_file.truncate()
            json.dump(data, json_file)

    else:
        with open(graph_path, 'rb') as f:
            trt_graph = tf.GraphDef()
            trt_graph.ParseFromString(f.read())
        with open('config.txt') as json_file:  
            data = json.load(json_file)
            input_names = data['model'][0]['input_names']

    return Model(trt_graph, input_names)
        
def greater_bbox(x, y):
    if ORDER_DICT[x[1]] > ORDER_DICT[y[1]]:
        return True
    else:
        return False

def bbox_sort(detected):
    list_sorted = True
    for i in range(len(detected) - 1):
        if greater_bbox(detected[i + 1], detected[i]):
            temp = detected[i]
            detected[i] = detected[i + 1]
            detected[i + 1] = temp
            list_sorted = False
    if not list_sorted:
        return bbox_sort(detected)
    return detected
            
def matchBBoxes(curr_bboxes, prev_bboxes, similarity_threshold):
    matched_indices = []
    prev_aggregates = []

    for prev_bbox in prev_bboxes:
        prev_aggregates.append(prev_bbox[0] + prev_bbox[1] + prev_bbox[2] + prev_bbox[3])

    for i in range(len(curr_bboxes)):
        curr_aggregate = curr_bboxes[i][0] + curr_bboxes[i][1] + curr_bboxes[i][2] + curr_bboxes[i][3]
        for j in range(len(prev_aggregates)):
            if abs(curr_aggregate - prev_aggregates[j]) <= similarity_threshold:
                matched_indices.append((i, j))

    return matched_indices
            
def predict(model, image, score_thresh, screen_mode, fill):
    """ Predict objects on an image.
    model (Model) - The model to predict with.
    image (nd.nparray) - The image to predict on.
    returns (nd.nparray) - The modified image with bounding boxes and item list.
    """

    global COLOR_DICT, prev_bboxes, prev_classes

    # Run the prediction
    scores, boxes, classes = model.predict(image)
    
    # Prepare the images for augmentation
    if screen_mode:
        new_image = image
    else:
        new_image = np.zeros((1080, 1920, 3), dtype=np.uint8)
        cv2.rectangle(new_image, (0, 0), (1920, 1080), (255, 0, 0), 5)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Go through each bounding box and only draw and save the ones above the score threshold
    detected = []
    for i in range(len(scores)):
        if scores[i] > score_thresh:
            detected.append([i, classes[i] + 1])
    detected = bbox_sort(detected)     
    
    text_list = []   
    bboxes = []
    classes = []
    for i in range(len(detected)):
        box = boxes[detected[i][0]] * np.array([image.shape[0], image.shape[1], image.shape[0], image.shape[1]])
        bboxes.append(box)
        classes.append(detected[i][0])
        
    matched_indices = matchBBoxes(bboxes, prev_bboxes, 100)
    
    for i in range(len(detected)):
        color = COLOR_DICT[detected[i][1]]
        
        x0 = bboxes[i][1] - 20
        y0 = bboxes[i][0] - (1080 - bboxes[i][0]) * 50 / 1080
        x1 = bboxes[i][3] + 20
        y1 = bboxes[i][2]
        
        num_pairs = 0
        
        for index_pair in matched_indices:
            if index_pair[0] == i and detected[i][0] == prev_classes[index_pair[1]]:
                num_pairs += 1
                x0 = ((x0 * num_pairs) + prev_bboxes[index_pair[1]][1] - 20) / (num_pairs + 1.0)
                y0 = ((y0 * num_pairs) + prev_bboxes[index_pair[1]][0] - (1080 - prev_bboxes[index_pair[1]][1]) * 50 / 1080) / (num_pairs + 1.0)
                x1 = ((x1 * num_pairs) + prev_bboxes[index_pair[1]][3] + 20) / (num_pairs + 1.0)
                y1 = ((y1 * num_pairs) + prev_bboxes[index_pair[1]][2]) / (num_pairs + 1.0)
                
        line_type = 3
        if fill:
            line_type = cv2.FILLED
            
        cv2.rectangle(new_image, (int(x0), int(y0)), (int(x1), int(y1)), color, line_type)

        name = CLASS_DICT[detected[i][1]]
        
    prev_bboxes = bboxes
    prev_classes = classes
    dy = 50 # Change in y position for each item
    for text in text_list:
        color = COLOR_DICT[text[2]]
        cv2.putText(new_image, str(text[1]) + "x " + text[0], (1500, y), cv2.FONT_HERSHEY_DUPLEX, 0.5, color, lineType=cv2.LINE_AA)
        y += dy

    return new_image

def main():
    """ Run this script.
    """

    global DATA_DIR, screen_mode

    config_path = os.path.join(DATA_DIR, 'model.config')
    checkpoint_path = os.path.join(DATA_DIR, 'model.ckpt')
    graph_path = os.path.join(DATA_DIR, 'graph.pbtxt')

    # Create an OpenCV window
    cv2.namedWindow("Inference", cv2.WND_PROP_FULLSCREEN)
    if not screen_mode:
        cv2.setWindowProperty("Inference", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    empty = np.zeros((1080, 1920, 3), dtype=np.uint8)
    cv2.waitKey(50)
    cv2.putText(empty, "Loading...", (441, 387), cv2.FONT_HERSHEY_DUPLEX, 2.5, (0, 255, 0), lineType=cv2.LINE_AA)
    cv2.putText(empty, "Green Machine", (521, 700), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 0, 0), lineType=cv2.LINE_AA)
    cv2.imshow("Inference", empty)
    cv2.waitKey(5)

    # Create Camera object
    x0 = None
    y0 = None
    x1 = None
    y1 = None
    with open('config.txt') as json_file:  
        data = json.load(json_file)
        x0 = data['crop'][0]['x0']
        y0 = data['crop'][0]['y0']
        x1 = data['crop'][0]['x1']
        y1 = data['crop'][0]['y1']
    if x0 == None:
        print "ERROR: Run config.py first!"
        exit()
        
    camera = Camera(0, (1920, 1080), float(x0), float(y0), float(x1), float(y1), True)
    camera.startVideoStream()

    # Create Model object
    model = createModel(config_path, checkpoint_path, graph_path)

    image = None
    warmup_img = None
    
    score_thresh = 0.65 # Change this to set the score threshold

    i = 0
    fill = True

    while warmup_img is None:
        warmup_img = camera.read()
        prev_img = warmup_img

    print "Starting Inference..."
    while True:
        read_img = camera.read()
        image = predict(model, read_img, score_thresh, screen_mode, fill)
        # Show inference only if camera is ready
        if image is not None:
            cv2.imshow("Inference", image)
            key = cv2.waitKey(1)
            if key == ord('f'):
                fill = not fill

# Run the script
main()
