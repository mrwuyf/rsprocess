import os
import numpy as np
from PIL import Image

# 颜色到类别ID的映射
COLOR_MAP = {
    (0, 0, 0): 0,
    (128, 0, 0): 1,
    (0, 128, 0): 2,
    (128, 128, 0): 3,
    (0, 0, 128): 4 # 可添加更多类别
}

def rgb_to_label(img, color_map):
    """
    将RGB图像转换为单通道标签图。
    """
    img = np.array(img)
    h, w, _ = img.shape
    label = np.zeros((h, w), dtype=np.uint8)

    for rgb, class_id in color_map.items():
        mask = np.all(img == rgb, axis=-1)
        label[mask] = class_id

    return Image.fromarray(label, mode='L')

def process_folder(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.tif'):
            img_path = os.path.join(input_folder, filename)
            img = Image.open(img_path).convert('RGB')
            label_img = rgb_to_label(img, COLOR_MAP)

            save_path = os.path.join(output_folder, filename)
            label_img.save(save_path)
            print(f"Saved: {save_path}")

# 用法示例
input_dir = r'E:\dataset\chitang\crop_jpg\target\masks_rgb'
output_dir = r'E:\dataset\chitang\crop_jpg\target\masks'
process_folder(input_dir, output_dir)