from Tkinter import *
import Tkinter as tk
import tkFileDialog as filedialog
from time import sleep
import os
from PIL import Image, ImageTk, ImageFile
import time
import urllib2
import socket
import io
import struct
import ast

class GUI(tk.Frame):
    def __init__(self, master):
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        self.labeling_server = False
   
        print("Welcome to XLT Labeling Tool")
        
        self.class_colors = ["287aff", "fff200", "ff75d3", "c300ff", "28e6ff", "f58231", "28ffad", "ff4228", "007705"]
        
        self.currimgnum = -1
        self.currimg = ""
        self.imgnames = []
        self.dirlen = 0
        self.mousex = 0
        self.mousey = 0
        self.drawing_label = False
        self.labelstartx = 0
        self.labelstarty = 0

        self.dir_name = StringVar()
        self.dir_name.set("No directory selected")
        self.progress_str = StringVar()
        self.progress_str.set("Progress: 0 / 0")
        self.curr_img_name = StringVar()
        self.curr_img_name.set("No Image")

        self.master = master
        master.title("XLT Labeling Tool")
        master.geometry('1800x1050')
        master.configure(background='#d3d3d3')
        imgicon = PhotoImage(file=os.path.join(os.getcwd(),'favicon.png'))
        master.tk.call('wm', 'iconphoto', master._w, imgicon)  

        self.menubar = Menu(master)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open Directory...", command=self.askDir)
        self.filemenu.add_command(label="Save Labels")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Quit", command=master.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        self.helpmenu = Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="Usage Guide")
        self.helpmenu.add_command(label="Information")
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)

        self.aboutmenu = Menu(self.menubar, tearoff=0)
        self.aboutmenu.add_command(label="Contact")
        self.aboutmenu.add_separator()
        self.aboutmenu.add_command(label="Website")
        self.aboutmenu.add_command(label="Github")
        self.menubar.add_cascade(label="About", menu=self.aboutmenu)

        master.configure(menu=self.menubar)
        
        master.bind("<Right>", self.nextImgKey)
        master.bind("<Left>", self.prevImgKey)
        master.bind("<Delete>", self.delKey)
        master.bind("<Key>", self.keyDown)
        master.bind("<Escape>", self.deselect)

        self.title = Label(master, text="XLT Labeling Tool", font=("Helvetica", 18, "bold"), height=1, bg='#d3d3d3')
        self.title.grid(row=0, column=0, sticky=NW, pady=5, padx=5)

        self.prev = Button(master, text="<< Prev", command=self.prevImg, font=("Helvetica", 16), height=1)
        self.prev.grid(row=28, column=0, sticky=NE)
        self.next = Button(master, text="Next >>", command=self.nextImg, font=("Helvetica", 16), height=1)
        self.next.grid(row=28, column=1, sticky=NW, padx=(5, 0))
        
        self.delete_last_label = Button(master, text="Delete Last Label", command=self.delLastLabel, font=("Helvetica", 10), height=1)
        self.delete_last_label.grid(row=28, column=3, sticky=SE, padx=(5, 0))
        
       	self.clear_labels = Button(master, text="Clear Labels", command=self.clearLabels, font=("Helvetica", 10), height=1)
        self.clear_labels.grid(row=29, column=3, sticky=NE, padx=(5, 0))

        self.clear_labels = Button(master, text="Download Image from Server", command=self.download, font=("Helvetica", 8), height=1)
        self.clear_labels.grid(row=29, column=2, sticky=SW, padx=(5, 0))

        self.class_arr = []
        self.selected_class = IntVar()
        self.selected_class.set(1)

        self.label_class1 = StringVar()
        self.class1label = Label(master, text="class 1", font=("Helvetica", 12), bg='#d3d3d3')
        self.class1label.grid(row=4, column=3, sticky=NE, padx=5)
        self.class1entry = Entry(master, width=15, textvariable=self.label_class1)
        self.class1entry.grid(row=4, column=4, sticky=NW, padx=(5, 80))
        Radiobutton(master, variable=self.selected_class, value=1).grid(row=4, column=2, sticky=NE)
        
        self.label_class2 = StringVar()
       	self.class2label = Label(master, text="class 2", font=("Helvetica", 12), bg='#d3d3d3')
        self.class2label.grid(row=5, column=3, sticky=NE, padx=5)
        self.class2entry = Entry(master, width=15, textvariable=self.label_class2)
        self.class2entry.grid(row=5, column=4, sticky=NW, padx=5)
        Radiobutton(master, variable=self.selected_class, value=2).grid(row=5, column=2, sticky=NE)
        
        self.label_class3 = StringVar()
       	self.class3label = Label(master, text="class 3", font=("Helvetica", 12), bg='#d3d3d3')
        self.class3label.grid(row=6, column=3, sticky=NE, padx=5)
        self.class3entry = Entry(master, width=15, textvariable=self.label_class3)
        self.class3entry.grid(row=6, column=4, sticky=NW, padx=5)
        Radiobutton(master, variable=self.selected_class, value=3).grid(row=6, column=2, sticky=NE)
        
        self.label_class4 = StringVar()
       	self.class4label = Label(master, text="class 4", font=("Helvetica", 12), bg='#d3d3d3')
        self.class4label.grid(row=7, column=3, sticky=NE, padx=5)
        self.class4entry = Entry(master, width=15, textvariable=self.label_class4)
        self.class4entry.grid(row=7, column=4, sticky=NW, padx=5)
        Radiobutton(master, variable=self.selected_class, value=4).grid(row=7, column=2, sticky=NE)
        
        self.label_class5 = StringVar()
       	self.class5label = Label(master, text="class 5", font=("Helvetica", 12), bg='#d3d3d3')
        self.class5label.grid(row=8, column=3, sticky=NE, padx=5)
        self.class5entry = Entry(master, width=15, textvariable=self.label_class5)
        self.class5entry.grid(row=8, column=4, sticky=NW, padx=5)
        Radiobutton(master, variable=self.selected_class, value=5).grid(row=8, column=2, sticky=NE)

        self.label_class6 = StringVar()
       	self.class6label = Label(master, text="class 6", font=("Helvetica", 12), bg='#d3d3d3')
        self.class6label.grid(row=9, column=3, sticky=NE, padx=5)
        self.class6entry = Entry(master, width=15, textvariable=self.label_class6)
        self.class6entry.grid(row=9, column=4, sticky=NW, padx=5)
        Radiobutton(master, variable=self.selected_class, value=6).grid(row=9, column=2, sticky=NE)
        
        self.label_class7 = StringVar()
       	self.class7label = Label(master, text="class 7", font=("Helvetica", 12), bg='#d3d3d3')
        self.class7label.grid(row=10, column=3, sticky=NE, padx=5)
        self.class7entry = Entry(master, width=15, textvariable=self.label_class7)
        self.class7entry.grid(row=10, column=4, sticky=NW, padx=5)
        Radiobutton(master, variable=self.selected_class, value=7).grid(row=10, column=2, sticky=NE)
        
        self.label_class8 = StringVar()
       	self.class8label = Label(master, text="class 8", font=("Helvetica", 12), bg='#d3d3d3')
        self.class8label.grid(row=11, column=3, sticky=NE, padx=5)
        self.class8entry = Entry(master, width=15, textvariable=self.label_class8)
        self.class8entry.grid(row=11, column=4, sticky=NW, padx=5)
        Radiobutton(master, variable=self.selected_class, value=8).grid(row=11, column=2, sticky=NE)
        
        self.label_class9 = StringVar()
       	self.class9label = Label(master, text="class 9", font=("Helvetica", 12), bg='#d3d3d3')
        self.class9label.grid(row=12, column=3, sticky=NE, padx=5)
        self.class9entry = Entry(master, width=15, textvariable=self.label_class9)
        self.class9entry.grid(row=12, column=4, sticky=NW, padx=5)
        Radiobutton(master, variable=self.selected_class, value=9).grid(row=12, column=2, sticky=NE)
        
        self.class_arr.append(self.class1entry)
        self.class_arr.append(self.class2entry)
        self.class_arr.append(self.class3entry)
        self.class_arr.append(self.class4entry)
        self.class_arr.append(self.class5entry)
        self.class_arr.append(self.class6entry)
        self.class_arr.append(self.class7entry)
        self.class_arr.append(self.class8entry)
        self.class_arr.append(self.class9entry)
        

        self.directory = Label(master, textvariable=self.dir_name, bg="#ffffff", font=("Helvetica", 14), width=60, height=1, borderwidth=2, relief="sunken")
        self.directory.grid(row=29, column=0, sticky=SW, padx=(10,0), pady=(50, 0))

        self.open_dir = Button(master, text="Open Directory", command=self.askDir, font=("Helvetica", 10), height=1)
        self.open_dir.grid(row=29, column=1, sticky=SW)

        self.imgname = Label(master, textvariable=self.curr_img_name, bg="#d3d3d3", font=("Helvetica", 10))
        self.imgname.grid(row=30, column=0, sticky=SW, pady=(10,0), padx=(10,0))

        self.progress = Label(master, textvariable=self.progress_str, bg="#d3d3d3", font=("Helvetica", 10))
        self.progress.grid(row=31, column=0, sticky=SW, padx=(10,0))

        self.outputlabel = Label(master, text="Output", bg="#d3d3d3")
        self.outputlabel.grid(row=0, column=4, sticky=NE, pady=5, padx=5)
        self.defaultoutput = StringVar(master)
        self.defaultoutput.set("KITTI")
        self.output = OptionMenu(master, self.defaultoutput, "KITTI", "VOC")
        self.output.grid(row=0, column=5, sticky=NW)

        self.photo = PhotoImage(file="default.gif")
        self.photocanvas = Canvas(master, width=960, height=720, bg="#d3d3d3", bd=0, highlightthickness=0, relief='ridge')
        self.photocanvas.grid(row=1, column=0, sticky=NW, pady=30, padx=50, columnspan=3, rowspan=27)
        self.photocanvas.bind("<Motion>", self.motion)
        self.photocanvas.bind("<Button-1>", self.click)
        self.photocanvas.create_image((2,2), anchor=NW, image=self.photo)
        
        self.curr_vertical_line = self.photocanvas.create_rectangle(self.mousex, 0, self.mousex, 720, width=1, outline="#000000")
        self.curr_horizontal_line = self.photocanvas.create_rectangle(0, self.mousey, 960, self.mousey, width=1, outline="#000000")

    def recvall(self, sock):
        imgname = sock.recv(1024)
        self.curr_img_name.set(imgname)
        n = sock.recv(1024)
        sock.send("dlready")
        data = b''
        while len(data) < int(n):
            packet = sock.recv(200000000)
            data += packet
        return data

    def download(self):
        self.drawing_label = False
        self.labeling_server = True
        s = socket.socket()
        host = '10.110.35.56'
        port = 7308

        s.connect((host,port))
        s.send("getimg")
        data = self.recvall(s)
        image = Image.open(io.BytesIO(data))
        self.photo = ImageTk.PhotoImage(image)
        self.photocanvas.delete("all")
        self.photocanvas.create_image((2,2), anchor=NW, image=self.photo)
        self.curr_label = self.photocanvas.create_rectangle(0, 0, 0, 0, width=0, outline="#50ff00")
        s.send("labels")
        labels = s.recv(2048)
        labels = ast.literal_eval(labels)
        for line in labels:
            linearr = line.split(" ")
            color = "#ffffff"
            for i in range(0, 9):
                if linearr[0] == self.class_arr[i].get():
                    color = "#" + self.class_colors[i]
            self.photocanvas.create_rectangle(int(float(linearr[4])), int(float(linearr[5])), int(float(linearr[6])), int(float(linearr[7])), width=3, outline=color)
        s.close()

    def downloadPrevImg(self):
        self.drawing_label = False
        self.labeling_server = True
        s = socket.socket()
        host = '10.110.35.56'
        port = 7308

        s.connect((host,port))
        s.send("prev:" + self.curr_img_name.get())
        data = self.recvall(s)
        image = Image.open(io.BytesIO(data))
        self.photo = ImageTk.PhotoImage(image)
        self.photocanvas.delete("all")
        self.photocanvas.create_image((2,2), anchor=NW, image=self.photo)
        self.curr_label = self.photocanvas.create_rectangle(0, 0, 0, 0, width=0, outline="#50ff00")
        s.send("labels")
        labels = s.recv(2048)
        print labels
        labels = ast.literal_eval(labels)
        for line in labels:
            linearr = line.split(" ")
            color = "#ffffff"
            for i in range(0, 9):
                if linearr[0] == self.class_arr[i].get():
                    color = "#" + self.class_colors[i]
            self.photocanvas.create_rectangle(int(float(linearr[4])), int(float(linearr[5])), int(float(linearr[6])), int(float(linearr[7])), width=3, outline=color)
        s.close()

    def deselect(self, e):
    	self.master.focus_force()
    	self.reloadImg()

    def RepresentsInt(self, s):
        try: 
            int(s)
            return True
        except ValueError:
            return False

    def keyDown(self, e):
        if self.RepresentsInt(e.char):
            e_int = int(e.char)
            if e_int < 10 and e_int > 0:
        	    self.selected_class.set(e_int)

    def nextImgKey(self, e):
        if self.labeling_server == True:
            self.download()
        else:
            self.nextImg()

    def prevImgKey(self, e):
        if self.labeling_server == True:
            self.downloadPrevImg()
        else:
            self.prevImg()
    
    def delKey(self, e):
        self.delLastLabel()

    def clearLabels(self):
        self.drawing_label = False
        if self.labeling_server:
            s = socket.socket()
            host = '10.110.35.56'
            port = 7308

            s.connect((host,port))
            s.send("clearlabels:" + self.curr_img_name.get())
            s.close()
            self.download()
        else:
            if self.currimgnum > -1:
                fn = self.dir_name.get() + "/labels/" + self.imgnames[self.currimgnum].split('.')[0] + ".txt"
                f = open(fn, "w+")
                self.reloadImg()

    def delLastLabel(self):
        fn = self.dir_name.get() + "/labels/" + self.imgnames[self.currimgnum].split('.')[0] + ".txt"
        lines = ""
        with open(fn) as f:
            lines = f.readlines()
            lines = lines[:-1]
            lines = ''.join(map(str, lines))
        f = open(fn, "w+")
        f.write(lines)
        f.close()
        self.reloadImg()

    def askDir(self):
        dirname = filedialog.askdirectory()
        self.dir_name.set(dirname)
        self.loadDir(dirname)

    def loadDir(self, directory):
        self.drawing_label = False
        self.labeling_server = False
        if (directory != ""):

            self.imgnames =  os.listdir(directory)
            self.imgnames.sort()
            imgnameslen = len(self.imgnames)
            i = 0
            while i < imgnameslen:
            	f = self.imgnames[i]
            	if f[-4:] != '.jpg' and f[-4:] != '.png' and f[-4:] != '.gif':
            		del self.imgnames[i]
            		imgnameslen -= 1
            	i += 1
            self.dirlen = len(self.imgnames)
            self.currimgnum = 0
            self.progress_str.set("Progress: " + str(self.currimgnum + 1) + " / " + str(self.dirlen))

            self.curr_img_name.set(self.imgnames[self.currimgnum])

            currimg = directory + "/" + self.imgnames[self.currimgnum]
            image = Image.open(currimg)
            self.photo = ImageTk.PhotoImage(image)
            self.photocanvas.delete("all")
            self.photocanvas.create_image((2,2), anchor=NW, image=self.photo)
            self.curr_label = self.photocanvas.create_rectangle(0, 0, 0, 0, width=3, outline="#50ff00")

            if not os.path.exists(directory + "/labels"):
    		    os.makedirs(directory + "/labels")

            fn = self.dir_name.get() + "/labels/" + self.imgnames[self.currimgnum].split('.')[0] + ".txt"
            try:
                f = open(fn, 'r')
            except IOError:
                f = open(fn, 'w')
            with open(fn) as f:
				lines = f.readlines()
				for line in lines:
					linearr = line.split(" ")
					color = "#ffffff"
					for i in range(0, 9):
					    if linearr[0] == self.class_arr[i]:
					        color = "#" + self.class_colors[i]
					self.photocanvas.create_rectangle(int(float(linearr[4])), int(float(linearr[5])), int(float(linearr[6])), int(float(linearr[7])), width=3, outline=color)

    def nextImg(self):
        self.drawing_label = False
        if self.labeling_server == True:
            self.download()
        else:
            if (self.currimgnum < self.dirlen - 1):
                self.currimgnum += 1
                self.reloadImg()

    def prevImg(self):
        self.drawing_label = False
        if self.labeling_server == True:
            self.downloadPrevImg()
        else:
            if (self.currimgnum > 0):
                self.currimgnum -= 1
                self.reloadImg()

    def reloadImg(self):
        self.drawing_label = False
        self.labeling_server = False
        self.progress_str.set("Progress: " + str(self.currimgnum + 1) + " / " + str(self.dirlen))
        self.curr_img_name.set(self.imgnames[self.currimgnum])

        currimg = self.dir_name.get() + "/" + self.imgnames[self.currimgnum]
        image = Image.open(currimg)
        self.photo = ImageTk.PhotoImage(image)
        self.photocanvas.delete("all")
        self.photocanvas.create_image((2,2), anchor=NW, image=self.photo)

        fn = self.dir_name.get() + "/labels/" + self.imgnames[self.currimgnum].split('.')[0] + ".txt"
        try:
            f = open(fn, 'r')
        except IOError:
            f = open(fn, 'w')
        with open(fn) as f:
            lines = f.readlines()
            for line in lines:
                linearr = line.split(" ")
                color = "#ffffff"
                for i in range(0, 9):
                    if linearr[0] == self.class_arr[i].get():
                        color = "#" + self.class_colors[i]
                self.photocanvas.create_rectangle(int(float(linearr[4])), int(float(linearr[5])), int(float(linearr[6])), int(float(linearr[7])), width=3, outline=color)

    def motion(self, event):
        self.mousex = event.x
        self.mousey = event.y
        self.photocanvas.delete(self.curr_vertical_line)
        self.photocanvas.delete(self.curr_horizontal_line)
        self.curr_vertical_line = self.photocanvas.create_rectangle(self.mousex, 0, self.mousex, 720, width=1, outline="#FFFFFF")
        self.curr_horizontal_line = self.photocanvas.create_rectangle(0, self.mousey, 960, self.mousey, width=1, outline="#FFFFFF")
        if (self.drawing_label):
            self.photocanvas.delete(self.curr_label)
            self.curr_label = self.photocanvas.create_rectangle(self.labelstartx, self.labelstarty, self.mousex, self.mousey, width=3, outline="#50ff00")

    def click(self, event):
        self.mousex = event.x
        self.mousey = event.y
        if (self.drawing_label):
            self.drawing_label = False
            if not self.labeling_server:
                with open(self.dir_name.get() + "/labels/" + self.imgnames[self.currimgnum].split('.')[0] + ".txt", "a") as myfile:
                    left = self.labelstartx
                    right = self.mousex
                    if (self.labelstartx > self.mousex):
                        left = self.mousex
                        right = self.labelstartx
                    top = self.labelstarty
                    bottom = self.mousey
                    if (self.labelstarty > self.mousey):
                        top = self.mousey
                        bottom = self.labelstarty
                    myfile.write(str(eval('self.label_class' + str(self.selected_class.get()) + '.get()')) + " 0.0 0 0.0 " + str(left) + ".0 " + str(top) + ".0 " + str(right) + ".0 " + str(bottom) + ".0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
                color = "#" + self.class_colors[self.selected_class.get() - 1]
                self.photocanvas.create_rectangle(self.labelstartx, self.labelstarty, self.mousex, self.mousey, width=3, outline=color)
            else:
                left = self.labelstartx
                right = self.mousex
                if (self.labelstartx > self.mousex):
                    left = self.mousex
                    right = self.labelstartx
                top = self.labelstarty
                bottom = self.mousey
                if (self.labelstarty > self.mousey):
                    top = self.mousey
                    bottom = self.labelstarty

                s = socket.socket()
                host = '10.110.35.56'
                port = 7308

                s.connect((host,port))
                s.send(self.curr_img_name.get() + ":" + str(eval('self.label_class' + str(self.selected_class.get()) + '.get()')) + " 0.0 0 0.0 " + str(left) + ".0 " + str(top) + ".0 " + str(right) + ".0 " + str(bottom) + ".0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
                s.close()
                color = "#" + self.class_colors[self.selected_class.get() - 1]
                self.photocanvas.create_rectangle(self.labelstartx, self.labelstarty, self.mousex, self.mousey, width=3, outline=color)
        else:
            self.drawing_label = True
            self.photocanvas.delete(self.curr_label)
            self.labelstartx = self.mousex
            self.labelstarty = self.mousey
            left = self.labelstartx
            right = self.mousex
            if (self.labelstartx > self.mousex):
                left = self.mousex
                right = self.labelstartx
            top = self.labelstarty
            bottom = self.mousey
            if (self.labelstarty > self.mousey):
                top = self.mousey
                bottom = self.labelstarty
                
            self.curr_label = self.photocanvas.create_rectangle(left, top, right, bottom, width=3, outline="#50ff00")
