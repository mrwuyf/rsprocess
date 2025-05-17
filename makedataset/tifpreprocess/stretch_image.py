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
    """读取16位图像，并返回影像数据集对象和元数据"""
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


def stretch_percent_16to8(src_data, nodata_values=[0]):
    """
    进行百分比拉伸，将16位图像数据转换为8位图像数据。
    排除无效数据（例如黑边或指定的nodata_values列表中的值）。
    """
    # 排除无效数据（假设无效数据为 nodata_values 列表中的值）
    valid_data = src_data[~np.isin(src_data, nodata_values)]

    # 检查是否有有效数据
    if valid_data.size == 0:
        print("没有有效数据，跳过处理")
        return np.zeros_like(src_data, dtype=np.uint8)

    # 统计有效数据的最大值和最小值
    src_max = np.max(valid_data)
    src_min = np.min(valid_data)
    print(f"有效数据范围 - 最大值: {src_max}, 最小值: {src_min}")

    # 计算直方图和累计频率
    hist, _ = np.histogram(valid_data, bins=np.arange(0, src_max + 2), range=(0, src_max + 1))
    freq = hist / valid_data.size
    cum_freq = np.cumsum(freq)

    # 使用累计频率来确定拉伸的最小值和最大值
    min_val, max_val = src_min, src_max
    for i in range(1, int(src_max)):
        if cum_freq[i] > 0.0015:
            min_val = i
            break

    for i in range(int(src_max) - 1, 0, -1):
        if cum_freq[i] < (cum_freq[-1] - 0.00012):
            max_val = i
            break

    print(f"拉伸区间: 最小值 {min_val}, 最大值 {max_val}")

    # 进行百分比拉伸，将无效数据区域保持为0
    stretched_data = np.clip((src_data - min_val) / (max_val - min_val) * 255, 0, 255).astype(np.uint8)
    dst_data = np.where(np.isin(src_data, nodata_values), 0, stretched_data)  # 保持无效数据为 0

    return dst_data


def process_image(in_filename, out_filename):
    po_in, width, height, bands, geo_transform, projection = read_tif(in_filename)
    if po_in is None:
        return

    output_data = []
    for band_idx in range(bands):
        print(f"处理第 {band_idx + 1} 波段")
        band = po_in.GetRasterBand(band_idx + 1)
        nodata_value = band.GetNoDataValue() or 65535  # 获取 NoData 值，默认 65535
        src_data = band.ReadAsArray().astype(np.float32)

        # 使用指定的 NoData 值列表
        dst_data = stretch_percent_16to8(src_data, nodata_values=[0, 65535])
        output_data.append(dst_data)

    write_tif(out_filename, width, height, bands, geo_transform, projection, output_data)
    po_in = None
    print("处理完成！")


def batch_stretch(input_dir, output_dir):
    """批量处理文件夹中的符合条件的影像文件"""
    file_list = []
    listdir(input_dir, file_list)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for in_filepath in file_list:
        filename = os.path.basename(in_filepath)
        out_filepath = os.path.join(output_dir, filename)

        print(f"\n正在处理文件: {in_filepath}")
        process_image(in_filepath, out_filepath)

if __name__ == '__main__':
    # 调用示例
    batch_stretch(r"E:\liutian\ori_image", r"E:\liutian\image")