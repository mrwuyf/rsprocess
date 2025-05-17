from osgeo import gdal
import numpy as np
import math
# import torch
# from torchvision import transforms as T

import os


def writeTiff(im_data, im_geotrans, im_proj, path):
    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_Uint16
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


# 像素坐标和地理坐标仿射变换
def CoordTransf(Xpixel, Ypixel, GeoTransform):
    XGeo = GeoTransform[0] + GeoTransform[1] * Xpixel + Ypixel * GeoTransform[2]
    YGeo = GeoTransform[3] + GeoTransform[4] * Xpixel + Ypixel * GeoTransform[5]
    return XGeo, YGeo


def TifStitch(OriTif, TifArrayPath, ResultPath, RepetitionRate):
    RepetitionRate = float(RepetitionRate)
    print("--------------------拼接影像-----------------------")
    dataset_img = gdal.Open(OriTif)
    width = dataset_img.RasterXSize  # 获取行列数
    height = dataset_img.RasterYSize
    bands = dataset_img.RasterCount  # 获取波段数
    proj = dataset_img.GetProjection()  # 获取投影信息
    geotrans = dataset_img.GetGeoTransform()  # 获取仿射矩阵信息
    ori_img = dataset_img.ReadAsArray(0, 0, width, height)  # 获取数据
    print("波段数为：", bands)

    # 先创建一个空矩阵
    if bands == 1:
        shape = [height, width]
    else:
        shape = [bands, height, width]
    result = np.zeros(shape, dtype='uint8')

    # 读取裁剪后的影像
    OriImgArray = []  # 创建队列
    NameArray = []
    imgList = os.listdir(TifArrayPath)  # 读入文件夹

    # imgList.sort(key=lambda x: int(x.split('.')[0]))  # 按照数字进行排序后按顺序读取文件夹下的图片
    for TifPath in imgList:
        # 读取tif影像
        img = gdal.Open(TifArrayPath + TifPath)
        width_crop = img.RasterXSize  # 获取行列数
        height_crop = img.RasterYSize
        bands_crop = img.RasterCount  # 获取波段数
        img = img.ReadAsArray(0, 0, width_crop, height_crop)  # 获取数据

        # 读取png影像
        # img = Image.open(TifArrayPath + TifPath)
        # height_crop = img.height
        # width_crop = img.width
        # img = np.array(img)
        #
        OriImgArray.append(img)  # 将影像按顺序存入队列
        name = TifPath.split('.')[0]
        # print(name)
        NameArray.append(name)
    print("读取全部影像数量为：", len(OriImgArray))

    #  行上图像块数目
    RowNum = int((height - height_crop * RepetitionRate) / (height_crop * (1 - RepetitionRate)))
    #  列上图像块数目
    ColumnNum = int((width - width_crop * RepetitionRate) / (width_crop * (1 - RepetitionRate)))
    # 获取图像总数
    sum_img = RowNum * ColumnNum + RowNum + ColumnNum + 1
    print("行影像数为：", RowNum)
    print("列影像数为：", ColumnNum)
    print("图像总数为：", sum_img)

    # 前面读取的是剔除了背景影像的剩余影像，拼接按照图像名称拼接，因此需再创建全为背景的影像，填充影像列表
    # 创建空矩阵
    if bands_crop == 1:
        shape_crop = [height_crop, width_crop]
    else:
        shape_crop = [bands_crop, height_crop, width_crop]
    img_crop = np.zeros(shape_crop)  # 创建空矩阵
    # 创建整体图像列表
    ImgArray = []
    count = 0
    for i in range(sum_img):
        img_name = i + 1
        for j in range(len(OriImgArray)):
            if img_name == int(NameArray[j]):
                image = OriImgArray[j]
                count = count + 1
                break
            else:
                image = img_crop
        ImgArray.append(image)

    print("包含目标的图象数量为：", count)
    print("整个影像列表数量为：", len(ImgArray))

    # 开始赋值
    num = 0
    for i in range(RowNum):
        for j in range(ColumnNum):
            # 如果图像是单波段
            if (bands == 1):
                result[
                int(i * height_crop * (1 - RepetitionRate)): int(i * height_crop * (1 - RepetitionRate)) + height_crop,
                int(j * width_crop * (1 - RepetitionRate)): int(j * width_crop * (1 - RepetitionRate)) + width_crop] = \
                ImgArray[num]
            # 如果图像是多波段
            else:
                result[:,
                int(i * height_crop * (1 - RepetitionRate)): int(i * height_crop * (1 - RepetitionRate)) + height_crop,
                int(j * width_crop * (1 - RepetitionRate)): int(j * width_crop * (1 - RepetitionRate)) + width_crop] = \
                ImgArray[num]
            num = num + 1
    # 最后一行
    for i in range(RowNum):
        if (bands == 1):
            result[
            int(i * height_crop * (1 - RepetitionRate)): int(i * height_crop * (1 - RepetitionRate)) + height_crop,
            (width - width_crop): width] = ImgArray[num]
        else:
            result[:,
            int(i * height_crop * (1 - RepetitionRate)): int(i * height_crop * (1 - RepetitionRate)) + height_crop,
            (width - width_crop): width] = ImgArray[num]
        num = num + 1
    # 最后一列
    for j in range(ColumnNum):
        if (bands == 1):
            result[(height - height_crop): height,
            int(j * width_crop * (1 - RepetitionRate)): int(j * width_crop * (1 - RepetitionRate)) + width_crop] = \
            ImgArray[num]
        else:
            result[:,
            (height - height_crop): height,
            int(j * width_crop * (1 - RepetitionRate)): int(j * width_crop * (1 - RepetitionRate)) + width_crop] = \
            ImgArray[num]
        num = num + 1
    # 右下角
    if (bands == 1):
        result[(height - height_crop): height,
        (width - width_crop): width] = ImgArray[num]
    else:
        result[:,
        (height - height_crop): height,
        (width - width_crop): width] = ImgArray[num]
    num = num + 1
    # 生成Tif影像

    writeTiff(result, geotrans, proj, ResultPath)

def extract_first_band(input_tif, output_tif):
    # 打开输入TIF文件
    dataset = gdal.Open(input_tif, gdal.GA_ReadOnly)
    if not dataset:
        print(f"无法打开文件 {input_tif}")
        return

    # 获取第一个波段
    band1 = dataset.GetRasterBand(1)
    if not band1:
        print("无法获取第一个波段")
        return

    # 获取波段数据
    band1_data = band1.ReadAsArray()

    # 获取地理变换参数和投影信息
    geo_transform = dataset.GetGeoTransform()
    projection = dataset.GetProjection()

    # 获取图像大小
    xsize = band1.XSize
    ysize = band1.YSize

    # 创建输出TIF文件
    driver = gdal.GetDriverByName('GTiff')
    out_dataset = driver.Create(output_tif, xsize, ysize, 1, band1.DataType)
    if not out_dataset:
        print(f"无法创建文件 {output_tif}")
        return

    # 设置地理变换参数和投影信息
    out_dataset.SetGeoTransform(geo_transform)
    out_dataset.SetProjection(projection)

    # 写入第一个波段的数据
    out_band = out_dataset.GetRasterBand(1)
    out_band.WriteArray(band1_data)

    # 清理
    out_band.FlushCache()
    del out_band
    del out_dataset
    del band1
    del dataset

    print(f"已提取第一个波段并保存到 {output_tif}")


if __name__ == '__main__':
    # 拼接影像
    ori_tif = r"E:\liutian\image\GF2_PMS1_E119.2_N37.8_20230407_L1A0007210166-pansharpen.tiff"
    tif_path = r"D:/DeepLearning/airs/fig_results/wetland/cmtfnet_2023/"
    ResultPath = r"E:\liutian\result\2023_cls.tif"
    TifStitch(ori_tif,
              tif_path,
              ResultPath, 0.0)
    output_tif = r"E:\liutian\result\wetland2023.tif"
    extract_first_band(ResultPath, output_tif)

    # 删除res.tif文件
    if os.path.exists(ResultPath):
        os.remove(ResultPath)
        print(f"已删除临时文件 {ResultPath}")