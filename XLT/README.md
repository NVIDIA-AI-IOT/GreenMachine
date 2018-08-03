# XLT Labeling Tool
A simple image labeling tool that generates KITTI label files for NVIDIA DIGITS

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
