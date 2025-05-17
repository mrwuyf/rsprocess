from osgeo import gdal


def apply_projection(original_image_path, classified_image_path, output_image_path):
    # 打开原始影像并获取投影信息
    original_ds = gdal.Open(original_image_path)
    projection = original_ds.GetProjection()
    geotransform = original_ds.GetGeoTransform()

    # 创建新的分类结果影像文件
    driver = gdal.GetDriverByName('GTiff')
    classified_ds = driver.CreateCopy(output_image_path, gdal.Open(classified_image_path), 0)

    # 将原始影像的投影信息应用到新创建的影像文件中
    classified_ds.SetProjection(projection)
    classified_ds.SetGeoTransform(geotransform)

    # 关闭数据集
    original_ds = None
    classified_ds = None


# 有投影的影像
original_image_path = r'E:\PostgraduateFile\program\0523\5000clip.tif'
# 无投影的分类影像
classified_image_path = r'E:\PostgraduateFile\program\0523\Result.tif'
# 添加完投影的分类影像输出路径
output_image_path = r'E:\PostgraduateFile\program\0523\Result_proj.tif'

apply_projection(original_image_path, classified_image_path, output_image_path)
