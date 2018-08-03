import tensorflow as tf
import numpy as np
import base64
import csv
import os
from PIL import Image
import io

def int64_feature(value):
  return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

def int64_list_feature(value):
  return tf.train.Feature(int64_list=tf.train.Int64List(value=value))

def bytes_feature(value):
  return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

def bytes_list_feature(value):
  return tf.train.Feature(bytes_list=tf.train.BytesList(value=value))

def float_list_feature(value):
  return tf.train.Feature(float_list=tf.train.FloatList(value=value))

def readKITTI(filename):
    arr_out = []
    try:
        open(filename, 'r')
    except IOError:
        open(filename, 'w')
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            linearr = line.rstrip().split(" ")
            arr_out.append(linearr)
    return arr_out

def getImgDimensions(img_path):
    img = Image.open(img_path)
    return img.size

def create_tf_example(img_name, img_path, data, class_key):
    with tf.gfile.GFile(img_path, 'rb') as fid:
        encoded_jpg = fid.read()

    image_format = str.encode(img_name.split('.')[1])

    img_size = getImgDimensions(img_path)
    width = img_size[0]
    height = img_size[1]

    xmins = []
    xmaxs = []
    ymins = []
    ymaxs = []
    classes_text = []
    classes = []

    for label in data:
        curr_class = None
        for i in range(1, len(class_key) + 1):
            if class_key[i] == label[0]:
                curr_class = i
        if curr_class == None:
            break

        classes_text.append(label[0])
        classes.append(curr_class)

        xmins.append(float(float(label[4]) / width))
        xmaxs.append(float(float(label[6]) / width))
        ymins.append(float(float(label[5]) / height))
        ymaxs.append(float(float(label[7]) / height))

        continue

    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': int64_feature(height),
        'image/width': int64_feature(width),
        'image/filename': bytes_feature(str.encode(img_name)),
        'image/source_id': bytes_feature(img_name),
        'image/encoded': bytes_feature(encoded_jpg),
        'image/format': bytes_feature(image_format),
        'image/object/bbox/xmin': float_list_feature(xmins),
        'image/object/bbox/xmax': float_list_feature(xmaxs),
        'image/object/bbox/ymin': float_list_feature(ymins),
        'image/object/bbox/ymax': float_list_feature(ymaxs),
        'image/object/class/text': bytes_list_feature(classes_text),
        'image/object/class/label': int64_list_feature(classes),
    }))

    return tf_example

def main():
    data_path = '/home/nvidia/Desktop/CurrentDataset_June20/test'
    class_key = {
        1: b'cup',
        2: b'rutensil',
        3: b'tutensil',
        4: b'container',
        5: b'plate',
        6: b'paper',
        7: b'stick',
        8: b'bottle',
        9: b'wrapper'
    }
    saveas_filename = 'test.tfrecords'

    writer = tf.python_io.TFRecordWriter(saveas_filename)
    images = os.listdir(data_path)

    for i in range (0, len(images)):
        if len(images[i].split(".")) == 1:
            images.pop(i)
            break

    for i in range(0, len(images)):
        kitti = readKITTI(data_path + "/labels/" + images[i].split(".")[0] + ".txt")
        tf_example = create_tf_example(images[i], data_path + "/" + images[i], kitti, class_key)
        writer.write(tf_example.SerializeToString())

    writer.close()

main()
