__author__ = 'elfx'
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from get_data import get_data
import cv2
import numpy as np
import datetime as dt
from random import shuffle
import os
import requests
import json
class CamApp(App):

    def get_images(self):
        images = get_data()
        return images

    def get_meme(self):
        shuffle(self.images)
        folder,image = self.images[0]
        image_name = os.path.join("images",folder,image)
        img = cv2.imread(image_name)
        return (folder,image,img)

    def date_string(self):
        today = dt.datetime.today()
        year = today.year
        mont = today.month
        day = today.day
        hour = today.hour
        minu = today.minute
        sec = today.second
        dstring = "{:04d}-{:02d}-{:02d}-{:02d}-{:02d}-{:02d}".format(year,mont,day,hour,minu,sec)
        return dstring

    def write_log(self,message):
        with open("emotions.log","a") as log:
            log.write(message + "\n")
    def build(self):
        self.graph = self.set_graph()
        self.frame_count = 0
        self.images = self.get_images()
        self.img1=Image()
        layout = BoxLayout()
        layout.add_widget(self.img1)
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0/30.0)

        return layout

    def update(self, dt):
        # display image from cam in opencv window
        if(self.frame_count==0):
             self.meme = self.get_meme()
        if(self.frame_count%5==0):
              self.meme = self.get_meme()
        self.frame_count += 1
        ret, frame = self.capture.read()

        subscription_key = ""
        face_api_url = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0/detect'
        cv2.imwrite("frame.jpg",frame)
        data = open('frame.jpg', 'rb')
        headers = {'Content-Type': 'application/octet-stream','Ocp-Apim-Subscription-Key': subscription_key}
        params = { 'returnFaceId': 'true', 'returnFaceLandmarks': 'false','returnFaceAttributes': 'emotion',}
        response = requests.post(face_api_url, params=params,
                         headers=headers,data=data )
        emotion_json = json.dumps(response.json())
        if(emotion_json):
            human_string =  ", ".join("=".join((k,str(v))) for k,v in sorted(emotion_json['faceAttributes']['emotion'].items()))
            date_log = self.date_string()
            self.write_log("{}:{}:{}:{}".format(date_log,human_string,self.meme[0],self.meme[1]))
        buf1 = cv2.flip( self.meme[-1], 0)
        buf = buf1.tostring()
        texture1 = Texture.create(size=( self.meme[-1].shape[1],  self.meme[-1].shape[0]), colorfmt='bgr')
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.img1.texture = texture1

if __name__ == '__main__':
    CamApp().run()
    cv2.destroyAllWindows()
