import os
import tkinter as tk
from shutil import copy2
from tkinter.filedialog import askdirectory
from pathlib import Path
import cv2
import yolotools

from PIL import Image
from PIL.ImageTk import PhotoImage

class imagechooser:

    def __init__(self):
        self.current_index = 0
        self.input_image_dir = None
        self.output_image_dir = None

        self.image_gen = None
        self.tk_image = None

        self.seen = set()

        self.root = tk.Tk()
        self.root.title("Image Sorter")
        self.root.bind("<BackSpace>", lambda event: self.next_image())
        self.root.bind("<Return>", lambda event: self.save())
        self.root.bind("o", lambda event: self.get_input_dir())
        self.root.bind("s", lambda event: self.get_output_dir())
        self.root.bind("p", lambda event: self.plot_orig())

        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(fill = 'both', expand = True)

        self.root.mainloop()

    def plot_orig(self):
        _, *labels = self.get_labels(self.img_path)
        yolotools.plot(img = cv2.imread(self.img_path), labels=map(float, labels))
    

    def get_input_dir(self):
        self.input_image_dir = askdirectory()
        self.refresh_paths()

    def get_output_dir(self):
        self.output_image_dir = askdirectory() 
        self.next_image()  
    def refresh_paths(self):
        self.image_gen = (image for image in os.listdir(self.input_image_dir) if image.endswith('jpg'))
        print(self.image_gen)

    def save(self):
        copy2(self.img_path, self.output_image_dir)
        copy2(yolotools.image_to_label(self.img_path), self.output_image_dir[:-6] + 'labels')
        self.seen = set(os.listdir(self.output_image_dir))
        self.next_image()
        

    def next_image(self):
        print('next')
        self.canvas.delete('all')
        try:
            img = next(self.image_gen)
            if not img or img not in self.seen:
                self.img_path = Path(self.input_image_dir).joinpath(img)
                self.pil_image = Image.open(self.img_path)
                self.current_index += 1
                resize_factor = max((self.pil_image.width / self.root.winfo_screenwidth()), (self.pil_image.height / self.root.winfo_height()))
                self.resized_image = self.pil_image.resize((int((self.pil_image.width / resize_factor)), int((self.pil_image.height / resize_factor))))
                self.tk_image = PhotoImage(self.resized_image)
                self.canvas.create_image(0, 0, image = self.tk_image, anchor=tk.NW)
                self.draw_rectangle(img_path=self.img_path)
                self.canvas.pack()
            else:
                print('seen, trying agian')
                self.next_image()
        except StopIteration:
            print('no images left')
    
    def get_labels(self, img_path):
        label_path = yolotools.image_to_label(img_path=img_path)
        with open(label_path) as f:
            label, x, y, w, h = f.readline().split(" ")[:5]
            return label, x, y, w, h
    def draw_rectangle(self, img_path):
        label, x, y, w, h = self.get_labels(img_path)
        x1, y1, x2 ,y2 = yolotools.to_xyxy(float(x), float(y), float(w), float(h))
        img_width, img_height = self.tk_image.width(), self.tk_image.height()
        self.canvas.create_rectangle(x1 * img_width, y1 * img_height, x2 * img_width, y2 * img_height, outline='red', width=2)
        self.canvas.create_text(10, 10, text=label, anchor=tk.NW, fill='white', font=('Arial', 12))
imagechooser()
