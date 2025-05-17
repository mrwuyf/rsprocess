import cv2
from osgeo import gdal
import numpy as np
import os
os.environ['PROJ_LIB'] = r'C:\Users\wu\.conda\envs\airs\Lib\site-packages\osgeo\data\proj'

def readTif(fileName, xoff=0, yoff=0, data_width=0, data_height=0):
    dataset = gdal.Open(fileName)
    if dataset is None:
        print(fileName + "文件无法打开")
        return None, None, None, None, None, None
    width = dataset.RasterXSize
    height = dataset.RasterYSize
    bands = dataset.RasterCount
    if (data_width == 0 and data_height == 0):
        data_width = width
        data_height = height
    data = dataset.ReadAsArray(xoff, yoff, data_width, data_height)
    geotrans = dataset.GetGeoTransform()
    proj = dataset.GetProjection()
    return width, height, bands, data, geotrans, proj

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



def augment_and_save(image_path, label_path, output_image_path, output_label_path):
    imageList = os.listdir(image_path)
    labelList = os.listdir(label_path)
    tran_num = len(imageList) + 1

    for i in range(len(imageList)):
        img_file = os.path.join(image_path, imageList[i])
        im_width, im_height, im_bands, im_data, im_geotrans, im_proj = readTif(img_file)

        label_file = os.path.join(label_path, labelList[i])
        label = cv2.imread(label_file, 0)

        # Horizontal flip
        im_data_hor = np.flip(im_data, axis=2)
        hor_path = os.path.join(output_image_path, f"{os.path.splitext(imageList[i])[0]}_hor.tif")
        writeTiff(im_data_hor, im_geotrans, im_proj, hor_path)
        Hor = cv2.flip(label, 1)
        hor_path = os.path.join(output_label_path, f"{os.path.splitext(imageList[i])[0]}_hor.tif")
        cv2.imwrite(hor_path, Hor)
        tran_num += 1

        # Vertical flip
        im_data_vec = np.flip(im_data, axis=1)
        vec_path = os.path.join(output_image_path, f"{os.path.splitext(imageList[i])[0]}_ver.tif")
        writeTiff(im_data_vec, im_geotrans, im_proj, vec_path)
        Vec = cv2.flip(label, 0)
        vec_path = os.path.join(output_label_path, f"{os.path.splitext(imageList[i])[0]}_ver.tif")
        cv2.imwrite(vec_path, Vec)
        tran_num += 1

        # Diagonal mirror
        # im_data_dia = np.flip(im_data_vec, axis=2)
        # dia_path = os.path.join(output_image_path, f"{os.path.splitext(imageList[i])[0]}_mir.tif")
        # writeTiff(im_data_dia, im_geotrans, im_proj, dia_path)
        # Dia = cv2.flip(label, -1)
        # dia_path = os.path.join(output_label_path, f"{os.path.splitext(imageList[i])[0]}_mir.tif")
        # cv2.imwrite(dia_path, Dia)
        # tran_num += 1

if __name__ == '__main__':
    # Paths
    train_image_path = r"E:\liutian\wetlanddataset\wetlandataset\train\images"
    train_label_path = r"E:\liutian\wetlanddataset\wetlandataset\train\labels"
    output_image_path = r"E:\liutian\wetlanddataset\wetlandataset\train\images"
    output_label_path = r"E:\liutian\wetlanddataset\wetlandataset\train\labels"

    # Create output directories if they don't exist
    os.makedirs(output_image_path, exist_ok=True)
    os.makedirs(output_label_path, exist_ok=True)

# Augment and save
    augment_and_save(train_image_path, train_label_path, output_image_path, output_label_path)