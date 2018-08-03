import argus_camera, thread, copy

class Camera:
    def __init__(self, port, size, cropX0, cropY0, cropX1, cropY1, reformat):
        self.camera = argus_camera.ArgusCamera(
          stream_resolution=size,
          video_converter_resolution=size, 
          source_clip_rect=(cropX0, cropY0, cropX1, cropY1),
        )

        #self.camera = argus_camera.ArgusCamera(port)
        #self.camera.set_shape(size[0], size[1])
        #test = self.camera.set_source_clip_rect(cropX0, cropY0, cropX1, cropY1)
        self.reformat = reformat
        self.image = None
        self.formatted_image = None
        self.video_thread = None
        self.streaming = False
        
    def readCamera(self):
        self.image = self.camera.read()
        
    def read(self):
        if not self.streaming:
            self.readCamera()
            if self.reformat:
                self.ConvertTensorRGBAtoNumpyRGB()
        if self.reformat:
            return self.formatted_image
        return self.image
        
    def setReformatting(self, reformat):
        self.reformat = reformat
        
    def ConvertTensorRGBAtoNumpyRGB(self):
        temp_image = copy.deepcopy(self.image)
        temp_image = temp_image[:,:,:3]
        self.formatted_image = temp_image.copy()

    def streamLoop(self):
        while self.streaming:
            self.readCamera()
            if self.reformat:
                self.ConvertTensorRGBAtoNumpyRGB()
        
    def startVideoStream(self):
        self.streaming = True
        self.video_thread = thread.start_new_thread(self.streamLoop, ())
    
    def stopVideoStream(self):
        self.streaming = False
        self.video_thread.exit()
    
    def close(self):
        self.camera.__del__()
    
    def __del__(self):
        self.close()
