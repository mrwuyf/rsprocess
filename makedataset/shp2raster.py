from osgeo import ogr, gdal


def get_tif_meta(tif_path):
    dataset = gdal.Open(tif_path)
    width = dataset.RasterXSize
    height = dataset.RasterYSize
    geotrans = dataset.GetGeoTransform()
    proj = dataset.GetProjection()
    return width, height, geotrans, proj


def shp2tif(shp_path, refer_tif_path, target_tif_path, attribute_field="class", nodata_value=0):
    width, height, geotrans, proj = get_tif_meta(refer_tif_path)
    shp_file = ogr.Open(shp_path)
    shp_layer = shp_file.GetLayer()

    target_ds = gdal.GetDriverByName('GTiff').Create(
        target_tif_path,
        width,
        height,
        1,
        gdal.GDT_Byte
    )
    target_ds.SetGeoTransform(geotrans)
    target_ds.SetProjection(proj)

    band = target_ds.GetRasterBand(1)


    # 初始化整张图像为 0（即 nodata_value）
    band.Fill(nodata_value)

    # 执行矢量图层栅格化
    gdal.RasterizeLayer(
        target_ds,
        [1],
        shp_layer,
        options=[f"ATTRIBUTE={attribute_field}"]
    )

    band.FlushCache()
    target_ds.FlushCache()
    target_ds = None


# 示例路径
shp_path = r"C:\Users\wu\Documents\WeChat Files\wxid_7nr0jh5psd7c22\FileStorage\File\2025-05\femlei05\femlei05.shp"
refer_tif_path = r"C:\Users\wu\Downloads\GF2_PMS1_E119.2_N37.8_20220502_L1A0006445036-pansharpen.tiff"
target_tif_path = r"E:\liutian\label.tif"
attribute_field = "ID"
nodata_value = 0

shp2tif(shp_path, refer_tif_path, target_tif_path, attribute_field, nodata_value)