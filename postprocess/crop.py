import os
from osgeo import gdal
import numpy as np

os.environ['PROJ_LIB'] = r'C:\Users\wu\.conda\envs\airs\Lib\site-packages\osgeo\data\proj'
#  读取tif数据集
def readTif(fileName):
    dataset = gdal.Open(fileName)
    if dataset == None:
        print(fileName + "文件无法打开")
    return dataset


#  保存tif文件函数
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
    # 创建文件
    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(path, int(im_width), int(im_height), int(im_bands), datatype)
    if (dataset != None):
        dataset.SetGeoTransform(im_geotrans)  # 写入仿射变换参数
        dataset.SetProjection(im_proj)  # 写入投影
    for i in range(im_bands):
        dataset.GetRasterBand(i + 1).WriteArray(im_data[i])
    del dataset


'''
滑动窗口裁剪函数
TifPath 影像路径
SavePath 裁剪后保存目录
CropSize 裁剪尺寸
RepetitionRate 重复率
'''


def TifCrop(TifPath, SavePath, CropSize, RepetitionRate):
    os.makedirs(SavePath, exist_ok=True)
    dataset_img = readTif(TifPath)
    width = dataset_img.RasterXSize
    height = dataset_img.RasterYSize
    proj = dataset_img.GetProjection()
    geotrans = dataset_img.GetGeoTransform()
    img = dataset_img.ReadAsArray(0, 0, width, height)  # 获取数据

    #  获取当前文件夹的文件个数len,并以len+1命名即将裁剪得到的图像
    new_name = len(os.listdir(SavePath)) + 1
    #  裁剪图片,重复率为RepetitionRate

    def format_filename(num):
        return '{:09d}'.format(num)

    for i in range(int((height - CropSize * RepetitionRate) / (CropSize * (1 - RepetitionRate)))):
        for j in range(int((width - CropSize * RepetitionRate) / (CropSize * (1 - RepetitionRate)))):
            #  如果图像是单波段
            if (len(img.shape) == 2):
                cropped = img[
                          int(i * CropSize * (1 - RepetitionRate)): int(i * CropSize * (1 - RepetitionRate)) + CropSize,
                          int(j * CropSize * (1 - RepetitionRate)): int(j * CropSize * (1 - RepetitionRate)) + CropSize]
            #  如果图像是多波段
            else:
                cropped = img[:,
                          int(i * CropSize * (1 - RepetitionRate)): int(i * CropSize * (1 - RepetitionRate)) + CropSize,
                          int(j * CropSize * (1 - RepetitionRate)): int(j * CropSize * (1 - RepetitionRate)) + CropSize]
            #  写图像
            writeTiff(cropped, geotrans, proj, os.path.join(SavePath, format_filename(new_name) + ".tif"))
            #  文件名 + 1
            new_name = new_name + 1
    #  向前裁剪最后一列
    for i in range(int((height - CropSize * RepetitionRate) / (CropSize * (1 - RepetitionRate)))):
        if (len(img.shape) == 2):
            cropped = img[int(i * CropSize * (1 - RepetitionRate)): int(i * CropSize * (1 - RepetitionRate)) + CropSize,
                      (width - CropSize): width]
        else:
            cropped = img[:,
                      int(i * CropSize * (1 - RepetitionRate)): int(i * CropSize * (1 - RepetitionRate)) + CropSize,
                      (width - CropSize): width]
        #  写图像
        writeTiff(cropped, geotrans, proj, os.path.join(SavePath, format_filename(new_name) + ".tif"))
        new_name = new_name + 1
    #  向前裁剪最后一行
    for j in range(int((width - CropSize * RepetitionRate) / (CropSize * (1 - RepetitionRate)))):
        if (len(img.shape) == 2):
            cropped = img[(height - CropSize): height,
                      int(j * CropSize * (1 - RepetitionRate)): int(j * CropSize * (1 - RepetitionRate)) + CropSize]
        else:
            cropped = img[:,
                      (height - CropSize): height,
                      int(j * CropSize * (1 - RepetitionRate)): int(j * CropSize * (1 - RepetitionRate)) + CropSize]
        writeTiff(cropped, geotrans, proj, os.path.join(SavePath, format_filename(new_name) + ".tif"))
        #  文件名 + 1
        new_name = new_name + 1
    #  裁剪右下角
    if (len(img.shape) == 2):
        cropped = img[(height - CropSize): height,
                  (width - CropSize): width]
    else:
        cropped = img[:,
                  (height - CropSize): height,
                  (width - CropSize): width]
    writeTiff(cropped, geotrans, proj, os.path.join(SavePath, format_filename(new_name) + ".tif"))
    new_name = new_name + 1

def batchProcessImages(image_folder, save_image_folder, crop_size, repetition_rate):
    os.makedirs(save_image_folder, exist_ok=True)
    image_files = os.listdir(image_folder)

    for image_file in image_files:
        image_path = os.path.join(image_folder, image_file)

        print(f"正在处理影像: {image_path}")
        TifCrop(image_path, save_image_folder, crop_size, repetition_rate)
        print(f"处理完成: {image_file}")


# 设置文件夹路径和裁剪参数
# image_folder = r"D:\GraduateFile\program\test\8bit"  # 原始影像文件夹
# mask_folder = r"E:\dataset\huanghe\original_masks"  # 掩膜文件夹
# save_image_folder = r"E:\dataset\huanghe\selected_images"  # 裁剪后影像保存文件夹
# save_mask_folder = r"E:\dataset\huanghe\selected_masks"  # 裁剪后掩膜保存文件夹

crop_size = 512  # 裁剪尺寸
repetition_rate = 0.1  # 重复率

# 批量处理所有影像和掩膜
# batchProcessImages(image_folder, mask_folder, save_image_folder, save_mask_folder, crop_size, repetition_rate)
#  将影像1裁剪为重复率为0.1的256×256的数据集
TifCrop(r"E:\liutian\image\GF2_PMS1_E119.2_N37.8_20230407_L1A0007210166-pansharpen.tiff",
        r"E:\liutian\2022", 512, 0)
# TifCrop(r"E:\liutian\label.tif",
#        r"E:\liutian\wetlanddataset\masks", 512, 0)