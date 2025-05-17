import os
import shutil
from osgeo import gdal
import numpy as np


def readTif(fileName):
    dataset = gdal.Open(fileName)
    if dataset is None:
        print(fileName + " 文件无法打开")
    return dataset


def is_all_zero_tif(tif_path):
    dataset = readTif(tif_path)
    if dataset is None:
        return False
    width = dataset.RasterXSize
    height = dataset.RasterYSize
    img = dataset.ReadAsArray(0, 0, width, height)
    # 检查是否全为0
    return np.all(img == 0)


# 设置文件夹路径
image_folder = r"E:\liutian\2023\images"
mask_folder = r"E:\dataset\huanghe\5\labels"

# 可选：如果想移动全为0的图片到别的文件夹
# zero_image_folder = r"E:\dataset\huanghe\allzero_images"
# zero_mask_folder = r"E:\dataset\huanghe\allzero_masks"
# os.makedirs(zero_image_folder, exist_ok=True)
# os.makedirs(zero_mask_folder, exist_ok=True)

image_files = [f for f in os.listdir(image_folder) if f.lower().endswith('.tif')]

for image_file in image_files:
    image_path = os.path.join(image_folder, image_file)
    # 检查mask是否全为0
    if is_all_zero_tif(image_path):
        image_path = os.path.join(image_folder, image_file)

        # 确保对应的image存在
        if os.path.exists(image_path):
            # 方案一：直接删除
            # os.remove(mask_path)
            os.remove(image_path)
            print(f"{image_file} 全为0， 已删除。")

            # 方案二：移动到指定文件夹(如想保留，可注释掉上面删除行，启用此方案)
            # shutil.move(mask_path, os.path.join(zero_mask_folder, mask_file))
            # shutil.move(image_path, os.path.join(zero_image_folder, mask_file))
            # print(f"{mask_file} 全为0，对应的文件已移动至 {zero_image_folder} 和 {zero_mask_folder}。")
        else:
            print(f"对应的影像文件 {image_path} 不存在，无法处理。")