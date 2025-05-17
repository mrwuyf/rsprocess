import os
from osgeo import gdal
import numpy as np

os.environ['PROJ_LIB'] = r'C:\Users\wu\.conda\envs\airs\Lib\site-packages\osgeo\data\proj'

# 读取tif数据集
def readTif(fileName):
    dataset = gdal.Open(fileName)
    if dataset is None:
        print(fileName + " 文件无法打开")
    return dataset

# 保存tif文件函数
def writeTiff(im_data, im_geotrans, im_proj, path):
    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32

    if len(im_data.shape) == 3:
        im_bands, im_height, im_width = im_data.shape
    elif len(im_data.shape) == 2:
        im_data = np.array([im_data])
        im_bands, im_height, im_width = im_data.shape

    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(path, int(im_width), int(im_height), int(im_bands), datatype)
    if dataset is not None:
        dataset.SetGeoTransform(im_geotrans)
        dataset.SetProjection(im_proj)
    for i in range(im_bands):
        dataset.GetRasterBand(i + 1).WriteArray(im_data[i])
    del dataset

def TifCrop(TifPath, SavePath, CropSize, RepetitionRate, base_name):
    dataset_img = readTif(TifPath)
    if dataset_img is None:
        return
    width = dataset_img.RasterXSize
    height = dataset_img.RasterYSize
    proj = dataset_img.GetProjection()
    geotrans = dataset_img.GetGeoTransform()
    img = dataset_img.ReadAsArray(0, 0, width, height)  # 获取数据

    # 每次处理一张图像时，从1开始计数裁剪块编号
    block_counter = 1

    def format_filename(num):
        return f"{base_name}_{num:06d}.tif"

    # 计算步长（非重叠部分长度）
    step_size = CropSize * (1 - RepetitionRate)

    # 正常裁剪（非边缘部分）
    vert_steps = int((height - CropSize * RepetitionRate) / step_size)
    horiz_steps = int((width - CropSize * RepetitionRate) / step_size)

    for i in range(vert_steps):
        for j in range(horiz_steps):
            row_start = int(i * step_size)
            col_start = int(j * step_size)
            row_end = row_start + CropSize
            col_end = col_start + CropSize

            if len(img.shape) == 2:  # 单波段
                cropped = img[row_start:row_end, col_start:col_end]
            else:  # 多波段
                cropped = img[:, row_start:row_end, col_start:col_end]

            writeTiff(cropped, geotrans, proj, os.path.join(SavePath, format_filename(block_counter)))
            block_counter += 1

    # 向前裁剪最后一列
    last_col_start = width - CropSize
    for i in range(vert_steps):
        row_start = int(i * step_size)
        if len(img.shape) == 2:
            cropped = img[row_start: row_start + CropSize, last_col_start: width]
        else:
            cropped = img[:, row_start: row_start + CropSize, last_col_start: width]
        writeTiff(cropped, geotrans, proj, os.path.join(SavePath, format_filename(block_counter)))
        block_counter += 1

    # 向前裁剪最后一行
    last_row_start = height - CropSize
    for j in range(horiz_steps):
        col_start = int(j * step_size)
        if len(img.shape) == 2:
            cropped = img[last_row_start: height, col_start: col_start + CropSize]
        else:
            cropped = img[:, last_row_start: height, col_start: col_start + CropSize]
        writeTiff(cropped, geotrans, proj, os.path.join(SavePath, format_filename(block_counter)))
        block_counter += 1

    # 裁剪右下角区域
    if len(img.shape) == 2:
        cropped = img[last_row_start: height, last_col_start: width]
    else:
        cropped = img[:, last_row_start: height, last_col_start: width]
    writeTiff(cropped, geotrans, proj, os.path.join(SavePath, format_filename(block_counter)))
    block_counter += 1

def batchProcessImages(image_folder, mask_folder, save_image_folder, save_mask_folder, crop_size, repetition_rate):
    os.makedirs(save_image_folder, exist_ok=True)
    os.makedirs(save_mask_folder, exist_ok= True)
    image_files = os.listdir(image_folder)

    for image_file in image_files:
        image_path = os.path.join(image_folder, image_file)
        mask_path = os.path.join(mask_folder, image_file)  # 假设mask文件与影像文件同名

        if not os.path.exists(mask_path):
            print(f"没有找到与 {image_file} 对应的掩膜文件 {mask_path}")
            continue

        # 获取原文件名（不包含扩展名）
        base_name = os.path.splitext(image_file)[0]

        # print(f"正在处理影像: {image_path} 和掩膜: {mask_path}")
        TifCrop(image_path, save_image_folder, crop_size, repetition_rate, base_name)
        TifCrop(mask_path, save_mask_folder, crop_size, repetition_rate, base_name)
        print(f"处理完成: {image_file}")

# 示例参数设置
image_folder = r"E:\dataset\huanghe\5\images_rgb"
mask_folder = r"E:\dataset\huanghe\5\masks"
save_image_folder = r"E:\dataset\huanghe\5\images"
save_mask_folder = r"E:\dataset\huanghe\5\labels"

crop_size = 512
repetition_rate = 0.0

# 批量处理所有影像和掩膜
batchProcessImages(image_folder, mask_folder, save_image_folder, save_mask_folder, crop_size, repetition_rate)