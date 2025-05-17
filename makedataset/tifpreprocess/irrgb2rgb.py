import os
import numpy as np
from osgeo import gdal


def listdir(path, list_name):
    """递归获取文件夹中的所有符合条件的文件"""
    supported_formats = {".tif", ".tiff", ".img"}  # 支持的影像格式

    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            listdir(file_path, list_name)
        elif os.path.isfile(file_path):
            if os.path.splitext(file_path)[1].lower() in supported_formats:
                list_name.append(file_path)


def read_tif(filename):

    dataset = gdal.Open(filename, gdal.GA_ReadOnly)
    if dataset is None:
        print(f"无法打开文件: {filename}")
        return None, None, None, None, None, None

    width = dataset.RasterXSize
    height = dataset.RasterYSize
    bands = dataset.RasterCount
    geo_transform = dataset.GetGeoTransform()
    projection = dataset.GetProjectionRef()

    return dataset, width, height, bands, geo_transform, projection


def write_tif(filename, width, height, bands, geo_transform, projection, data):
    """将处理后的8位数据写入文件"""
    driver = gdal.GetDriverByName("GTiff")
    out_dataset = driver.Create(filename, width, height, bands, gdal.GDT_Byte)
    out_dataset.SetGeoTransform(geo_transform)
    out_dataset.SetProjection(projection)

    for i in range(bands):
        out_band = out_dataset.GetRasterBand(i + 1)
        out_band.WriteArray(data[i])
        out_band.FlushCache()

    out_dataset = None
    print("图像已成功保存到:", filename)
def extract_rgb_bands(in_filename, out_filename):
    """从8位图像中提取前三个波段，并生成RGB图像保存到指定路径"""
    dataset = gdal.Open(in_filename, gdal.GA_ReadOnly)
    if dataset is None:
        print(f"无法打开文件: {in_filename}")
        return

    # 获取影像的基本信息
    width = dataset.RasterXSize
    height = dataset.RasterYSize
    bands = dataset.RasterCount

    # 确保影像至少有3个波段
    if bands < 3:
        print(f"文件 {in_filename} 只有 {bands} 个波段，无法生成RGB图像")
        dataset = None
        return

    # 读取前三个波段
    rgb_data = []
    for i in range(3):
        band = dataset.GetRasterBand(i + 1)
        rgb_data.append(band.ReadAsArray())

    rgb_data = [rgb_data[2], rgb_data[1], rgb_data[0]]

    # 将数据转换为numpy数组，并准备写入
    rgb_data = np.array(rgb_data)

    # 获取地理信息
    geo_transform = dataset.GetGeoTransform()
    projection = dataset.GetProjection()

    # 关闭输入文件
    dataset = None

    # 保存RGB图像
    write_tif(out_filename, width, height, 3, geo_transform, projection, rgb_data)
    print(f"RGB图像已成功保存到: {out_filename}")


def process_rgb_directory(input_dir, output_dir):
    """批量处理文件夹中的影像文件，提取前3个波段生成RGB彩色图片"""
    file_list = []
    listdir(input_dir, file_list)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for in_filepath in file_list:
        filename = os.path.basename(in_filepath)
        out_filepath = os.path.join(output_dir, filename)

        print(f"\n正在处理文件: {in_filepath}")
        extract_rgb_bands(in_filepath, out_filepath)


if __name__ == '__main__':
    process_rgb_directory(r"E:\liutian\wetlanddataset\images", r"E:\liutian\wetlanddataset\images_rgb")