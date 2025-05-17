# -*- coding: utf-8 -*-
# @Time    : 2024/8/26 10:20
# @Author  : xuxing
# @Site    : 
# @File    : visualization.py
# @Software: PyCharm

from PIL import Image
import numpy as np
import os
from tqdm import tqdm
from config.load_config import DatasetConfig
import matplotlib.pyplot as plt


def gray_color(input_dir, output_dir, color_mapping):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in tqdm(os.listdir(input_dir)):
        if filename.endswith(".tif"):
            gray_image_path = os.path.join(input_dir, filename)
            gray_image = Image.open(gray_image_path).convert('L')
            gray_array = np.array(gray_image)

            # Create a color image array
            color_image = np.zeros((*gray_array.shape, 3), dtype=np.uint8)

            for cls_id, color in color_mapping.items():
                color_image[gray_array == cls_id] = color

            # Convert the color image array back to a PIL image
            color_image_pil = Image.fromarray(color_image)

            # Save the color image
            color_image_path = os.path.join(output_dir, filename)
            color_image_pil.save(color_image_path)
            # print(f"Saved colored image: {color_image_path}")



class ImageDisplay:
    def __init__(self, image_folder, label_folder, preds_folder, display_folder):
        self.image_folder = image_folder
        self.label_folder = label_folder
        self.preds_folder = preds_folder
        self.display_folder = display_folder
        
        if not os.path.exists(display_folder):
            os.mkdir(display_folder)
        
    def display_single_image(self, image_name):
        img = Image.open(os.path.join(self.image_folder, image_name))
        label = Image.open(os.path.join(self.label_folder, image_name))
        pred = Image.open(os.path.join(self.preds_folder, image_name))
        
        plt.figure(figsize=(15, 5))
        
        plt.subplot(1, 3, 1)
        plt.imshow(img)
        plt.title('Image')
        plt.axis('off')
        
        plt.subplot(1, 3, 2)
        plt.imshow(label)
        plt.title('Label')
        plt.axis('off')
        
        plt.subplot(1, 3, 3)
        plt.imshow(pred)
        plt.title('Prediction')
        plt.axis('off')
        
        plt.tight_layout()
        # 保存文件名与原始图像 basename 一致
        basename = os.path.splitext(image_name)[0]
        plt.savefig(os.path.join(self.display_folder, f'{basename}.png'))
        plt.close()
    
    def display_all_images(self):
        images = sorted(os.listdir(self.image_folder))
        
        for image_name in tqdm(images):
            self.display_single_image(image_name)


if __name__ == '__main__':
    # config = DatasetConfig("../config/config_dataset.yaml")
    # color_mapping = {info['cls']: tuple(info['color']) for info in config.cls_dict.values()}
    # input_dir = r'E:\work\data\potsdam\test\preds'
    # output_dir = r'E:\work\data\potsdam\test\preds_color'
    # gray_color(input_dir, output_dir, color_mapping)
    
    image_fp = r'E:\work\data\potsdam\test\images'
    label_fp = r'E:\work\data\potsdam\test\labels'
    preds_fp = r'E:\work\data\potsdam\test\preds_color'
    save_fp = r'E:\work\data\potsdam\test\display'
    image_display = ImageDisplay(image_fp, label_fp, preds_fp, save_fp)

    image_display.display_all_images()
    
    