import os
from osgeo import gdal
import numpy as np

def readTif(tif_path):
    dataset = gdal.Open(tif_path, gdal.GA_ReadOnly)
    if dataset is None:
        print(f"无法打开文件: {tif_path}")
    return dataset

def writeTiff(im_data, im_geotrans, im_proj, path):
    # im_data应为3维数组: Bands x Height x Width
    # 通常RGB 3个波段，数据类型为Byte
    driver = gdal.GetDriverByName("GTiff")
    bands, height, width = im_data.shape
    dataset = driver.Create(path, width, height, bands, gdal.GDT_Byte)
    if dataset is not None:
        dataset.SetGeoTransform(im_geotrans)
        dataset.SetProjection(im_proj)
    for i in range(bands):
        dataset.GetRasterBand(i+1).WriteArray(im_data[i])
    del dataset

def mask_to_rgb(mask_path, rgb_path, color_map):
    dataset = readTif(mask_path)
    if dataset is None:
        return
    width = dataset.RasterXSize
    height = dataset.RasterYSize
    proj = dataset.GetProjection()
    geotrans = dataset.GetGeoTransform()

    # 读取数据为数组 (Height x Width)
    mask_data = dataset.ReadAsArray()

    # 创建RGB数组，3通道
    rgb_data = np.zeros((3, height, width), dtype=np.uint8)

    # 为mask中的每个类别映射到相应的RGB颜色
    for val, color in color_map.items():
        rgb_data[0][mask_data == val] = color[0]
        rgb_data[1][mask_data == val] = color[1]
        rgb_data[2][mask_data == val] = color[2]

    writeTiff(rgb_data, geotrans, proj, rgb_path)
    print(f"{mask_path} 已转换为RGB并保存至 {rgb_path}")

# 定义color_map，示例中假设0为背景(黑色)，1为前景(白色)
# 若有多类别，可自行扩展，如：2:(0,255,0),3:(0,0,255)
color_map = {
    0: (0, 0, 0),
    1: (128, 0, 0),
    2: (0, 128, 0),
    3: (128, 128, 0),
    4: (0, 0, 128),
}

# color_map = {
#     0: [178, 178, 178],  # 未利用地
#     1: [202, 122, 245],  # 建筑
#     2: [255, 0, 0],  # 道路
#     3: [0, 169, 230],  # 水体
#     4: [255, 255, 255],  # 雪地
#     5: [255, 170, 0],  # 农田
#     6: [38, 115, 0],  # 林地
#     7: [163, 255, 115]  # 草地
# }

# color_map = {
#     0: [255, 255, 255],
#     1: [255, 0, 0],
#     2: [255, 255, 0],
#     3: [0, 0, 255],
#     4: [159, 129, 183],
#     5: [0, 255, 0],
#     6: [255, 195, 128]
# }

# 设置输入和输出文件夹路径
input_mask_folder = r"D:\DeepLearning\airs\data\siluan\test\labels"
output_rgb_folder = r"D:\DeepLearning\airs\data\siluan\test\labels_rgb"

os.makedirs(output_rgb_folder, exist_ok=True)

# 遍历输入mask文件夹中的所有tif文件，并批量转换
for mask_file in os.listdir(input_mask_folder):
    if mask_file.lower().endswith('.tif'):
        mask_path = os.path.join(input_mask_folder, mask_file)
        # 输出文件名可根据需要更改，这里使用原文件名
        # 若想加后缀，可用 mask_file.replace('.tif','_rgb.tif')
        rgb_path = os.path.join(output_rgb_folder, mask_file)
        mask_to_rgb(mask_path, rgb_path, color_map)