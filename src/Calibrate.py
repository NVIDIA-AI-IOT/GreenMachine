import cv2, qrcode, pyqrcode, Image, json
from pyzbar.pyzbar import decode, ZBarSymbol
from Camera import Camera
import numpy as np

def resizeQR(qr, multiplier):
    new_qr = np.zeros((qr.shape[0]*multiplier, qr.shape[1]*multiplier), dtype=np.uint8)
    for y in range(qr.shape[0]):
        for x in range(qr.shape[1]):
            new_x = 0
            new_y = 0
            for n in range(multiplier * multiplier):
                new_qr[new_y + y * multiplier][new_x + x * multiplier] = qr[y][x]
                new_x += 1
                if (new_x == multiplier):
                    new_y += 1
                    new_x = 0                
    return new_qr

def addQR(image, data, x, y):
    qr = pyqrcode.create(data).text().split("\n")[:-1]
    np_qr = np.zeros((len(qr), len(qr[0])), dtype=np.uint8)
    for row in range(len(qr)):
        np_qr[row] = list(qr[row])

    np_qr = np_qr[4:np_qr.shape[0] - 4, 4:np_qr.shape[1] - 4]
    np_qr = np_qr[:,:] * 255
    np_qr = np_qr

    np_qr = resizeQR(np_qr, 15)
    
    image[x:x+np_qr.shape[0], y:y+np_qr.shape[1], 0] = np_qr
    image[x:x+np_qr.shape[0], y:y+np_qr.shape[1], 1] = np_qr
    
def updateConfig(x0, y0, x1, y1):
    with open('config.txt', 'r+') as json_file:  
        data = json.load(json_file)
        data['crop'] = []
        data['crop'] = [{'x0': str(x0), 'y0': str(y0), 'x1': str(x1), 'y1': str(y1)}]
        json_file.seek(0)
	json_file.truncate()
        json.dump(data, json_file)
        print "Config updated"
    
camera = Camera(0, (1920, 1080), 0, 0, 1, 1, True)
    
image = np.zeros((1080, 1920, 3), dtype=np.uint8)
addQR(image, "top_left", 0, 0)
addQR(image, "bottom_right", 705, 1545)

thresh = np.array([[200, 200, 0], [255, 255, 255]])

cv2.namedWindow("Calibrate", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Calibrate", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.imshow("Calibrate", image)
cv2.waitKey(1000)
read = camera.read()
mask = 255 - cv2.inRange(read, thresh[0], thresh[1])

cv2.imshow("Calibrate", mask)
cv2.waitKey(2000)

top = 0
bottom = 0
left = 0
right = 0

qr_codes = decode(mask, symbols=[ZBarSymbol.QRCODE])
for qrcode in qr_codes:
    if qrcode.data == "top_left":
        top = qrcode.rect.top
        left = qrcode.rect.left
    if qrcode.data == "bottom_right":
        bottom = qrcode.rect.top + qrcode.rect.height
        right = qrcode.rect.left + qrcode.rect.width

top_normalized = top / 1080.0
left_normalized = left / 1920.0
bottom_normalized = bottom / 1080.0
right_normalized = right / 1920.0
        
print "\n\nNORMALIZED COORDINATES:"
print left_normalized, top_normalized, right_normalized, bottom_normalized

updateConfig(left_normalized, top_normalized, right_normalized, bottom_normalized)

read = cv2.cvtColor(read, cv2.COLOR_BGR2RGB)
