import os
from pathlib import Path

import cv2
import numpy as np
import matplotlib.pyplot as plt



# for working with yolo formatted data

def setup_yolo(ds_name):
    os.makedirs(ds_name, exist_ok=True)
    os.makedirs(os.path.join(ds_name, 'images'), exist_ok=True)
    os.makedirs(os.path.join(ds_name, 'labels'), exist_ok=True)

def normalize(raw, max):
    return raw /max

def to_xywh(x1, y1, x2, y2):
    x = (x1 + x2) / 2.0
    y = (y1 + y2) / 2.0
    w = x2 - x1
    h = y2 - y1
    return x, y, w, h

def to_xyxy(x, y, w, h):
    x1 = x - w / 2
    y1 = y - h / 2
    x2 = x + w / 2
    y2 = y + h / 2
    return x1, y1, x2, y2


## given absolute path to an image, find its corresponding label
def image_to_label(img_path: str) -> str:
    p = Path(img_path)
    ds_path = Path(*p.parts[:-2])
    img_name = str(p.parts[-1])
    return ds_path.joinpath('labels', img_name[:-3] + 'txt')


def get_labels(self, img_path):
    label_path = image_to_label(img_path=img_path)
    with open(label_path) as f:
        label, x, y, w, h = f.readline().split(" ")[:5]
        return label, x, y, w, h
    
    # takes xywh norm 
def plot(img: np.array, labels: list): 
    image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB for matplotlib

    # Plot the image and boxes
    fig, ax = plt.subplots(1, figsize=(12, 9))      
    ax.imshow(image_rgb)

    # Draw boxes
    x_center, y_center, width, height = labels
    # print(image.shape)
    img_height, img_width, _ = img.shape

    x_left = (x_center - (width/2)) * img_width
    y_top = (y_center - (height/2)) * img_height
    true_width = width * img_width
    true_height = height * img_height
    prev = (x_center, y_center, width, height)
    ax.set_title(f'{x_center}, {y_center}, {width}, {height}')
    rect = plt.Rectangle((x_left, y_top), true_width,
                        true_height, fill=False, color='red', linewidth=2)
    ax.add_patch(rect)
    
    fig.canvas.mpl_connect('scroll_event', zoom_and_pan)
    fig.canvas.mpl_connect('button_press_event', zoom_and_pan)
    fig.canvas.mpl_connect('motion_notify_event', zoom_and_pan)
    fig.canvas.mpl_connect('button_release_event', zoom_and_pan)
    
    plt.axis('off')
    plt.show(block=False)
    plt.pause(100.0)
    plt.close()
    # Add zoom and pan functionality to the plot

pan_start = None

def zoom_and_pan(event):
    global pan_start
    axtemp = event.inaxes
    if axtemp is None:
        return

    x_min, x_max = axtemp.get_xlim()
    y_min, y_max = axtemp.get_ylim()
    x_delta = (x_max - x_min) / 10
    y_delta = (y_max - y_min) / 10

    if event.name == 'scroll_event':
        if event.button == 'up':
            axtemp.set(xlim=(x_min + x_delta, x_max - x_delta))
            axtemp.set(ylim=(y_min + y_delta, y_max - y_delta))
        elif event.button == 'down':
            axtemp.set(xlim=(x_min - x_delta, x_max + x_delta))
            axtemp.set(ylim=(y_min - y_delta, y_max + y_delta))
        axtemp.figure.canvas.draw()
    elif event.name == 'button_press_event' and event.button == 1:
        pan_start = (event.xdata, event.ydata)
    elif event.name == 'motion_notify_event' and pan_start:
        dx = event.xdata - pan_start[0]
        dy = event.ydata - pan_start[1]
        axtemp.set_xlim(x_min - dx, x_max - dx)
        axtemp.set_ylim(y_min - dy, y_max - dy)
        axtemp.figure.canvas.draw()
    elif event.name == 'button_release_event' and event.button == 1:
        pan_start = None



