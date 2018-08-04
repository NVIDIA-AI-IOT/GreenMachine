# XLT Labeling Tool
A simple image labeling tool that generates KITTI label files, created by Isaac Wilcove during summer 2018.

## Running XLT

```
cd src/
python XLT.py
```

## Using XLT

### Opening a directory

Click the "Open Directory" button at the bottom of the window and open the directory containing the images. Your images will then all be loaded and a progress indicator in the bottom left will show your progress through that folder of images.

### Creating and saving labels

To create a label, first type your class name(s) in the boxes on the right. Select which class you would like to use with the radio buttons, and click to start placing a bounding box. This should create a green square. Move your mouse to the other corner of the object you are highlighting and click again. The green square should now turn a different color and stay in place. This means that the label is saved to the file. Label files are in the labels folder that is automatically generated in the same folder as the images. Labels are saved to the file as soon as you place them, so you can just close the application window when you are done labeling.

### Keyboard Shortcuts
`Del` - Deletes the most recently placed bounding box in the current image

`Esc` - De-focuses all textboxes and reloads class names

` ➡️ ` - Goes to the next image

` ⬅️ ` - Goes to the previous image

`1-9` - Switches the current class to that number

### Convert to TFRecord

If you want to use your XLT labels for training Tensorflow models, you can convert them to TFRecord with `kitti-to-tfrecord.py`.

Just change the following 3 variables in the script to configure the conversion:

`data_path` - the path to your dataset. Do not include the `/labels/` folder at the end of the path.

`class_key` - Change this dict to match the class numbers used in XLT to their names. Format for each item is as follows, with each item on a new line separated by commas:

`[class number]: b[class name]`

`saveas_filename` - the name of the file to save. The file naming format is as follows:

`[name].tfrecord`

To run the script, just run `python kitti-to-tfrecord.py`.
