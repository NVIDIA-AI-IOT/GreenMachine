import jetcam, cv2, time, json
import numpy as np
from Camera import Camera

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

cv2.namedWindow("Camera", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Camera", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    img = camera.read()
    new_image = np.zeros((1080, 1920, 3), dtype=np.uint8)
    cv2.rectangle(new_image, (0, 0), (1920, 1080), (255, 0, 0), 5)
    cv2.imshow("Camera", new_image)
    cv2.waitKey(1000)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    cv2.imwrite("collected_imgs/" + str(int(time.time())) + ".png", img)
    print "Image saved."
