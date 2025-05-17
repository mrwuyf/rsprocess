import glob
import os
import shutil
from unpackage import unpackage
from ortho import ortho
from pansharpen import gdal_pansharpen
from osgeo import gdal
from build_pyramid import build_pyramid
import warnings
import arosics
import argparse
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

warnings.filterwarnings('ignore')
gdal.UseExceptions()


def preprocess(dem_path, tar_dir, output_dir):
    """
    Preprocesses geospatial data by unpacking, orthorectifying, registering,
    pansharpening, building pyramids, and saving the fused TIFF files to the output directory.

    Parameters:
    dem_path (str): Path to the DEM file used for orthorectification.
    tar_dir (str): Directory containing the .tar.gz compressed files.
    output_dir (str): Directory where the fused TIFF files will be saved.
    """

    # 创建输出目录（如果不存在）
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"创建输出目录: {output_dir}")

    tar_paths = glob.glob(os.path.join(tar_dir, "*.tar.gz"))
    tar_unpackage_dirs = []
    logging.info("开始解压...")

    for tar_index, tar_path in enumerate(tar_paths):
        logging.info(f"解压 {tar_index + 1}/{len(tar_paths)}: {os.path.basename(tar_path)}")
        try:
            tar_unpackage_dir = unpackage(tar_path)
            tar_unpackage_dirs.append(tar_unpackage_dir)
        except Exception as e:
            logging.error(f"解压 {tar_path} 时出错: {e}")
            continue  # 跳过当前压缩包，继续下一个

    logging.info("开始正射校正与融合...")
    for tar_unpackage_index, tar_unpackage_dir in enumerate(tar_unpackage_dirs):
        logging.info(f"处理 {tar_unpackage_index + 1}/{len(tar_unpackage_dirs)}: {os.path.basename(tar_unpackage_dir)}")

        try:
            # 全色数据正射校正
            pan_files = glob.glob(os.path.join(tar_unpackage_dir, "*PAN*.tiff"))
            if not pan_files:
                logging.warning(f"{tar_unpackage_dir} 中未找到 PAN 图像")
                continue
            pan_path = pan_files[0]
            pan_ortho_path = pan_path.replace(".tiff", "_ortho.tiff")
            pan_res = 0.8
            logging.info(f"正射校正 PAN 图像: {os.path.basename(pan_path)}")
            ortho(pan_path, dem_path, pan_res, pan_ortho_path)

            # 多光谱数据正射校正
            mss_files = glob.glob(os.path.join(tar_unpackage_dir, "*MSS*.tiff"))
            if not mss_files:
                logging.warning(f"{tar_unpackage_dir} 中未找到 MSS 图像")
                continue
            mss_path = mss_files[0]
            mss_ortho_path = mss_path.replace(".tiff", "_ortho.tiff")
            mss_res = 3.2
            logging.info(f"正射校正 MSS 图像: {os.path.basename(mss_path)}")
            ortho(mss_path, dem_path, mss_res, mss_ortho_path)

            # 图像配准
            logging.info("图像配准...")
            ref_image = pan_ortho_path
            tgt_image = mss_ortho_path
            mss_registration_path = mss_path.replace(".tiff", "_registration.tiff")
            coreg = arosics.COREG(
                im_ref=ref_image,
                im_tgt=tgt_image,
                path_out=mss_registration_path,
                fmt_out='GTIFF',
                max_shift=20
            )

            coreg.calculate_spatial_shifts()
            coreg.correct_shifts()

            # 融合
            logging.info("图像融合...")
            pansharpen_path = pan_ortho_path.split("PAN")[0]+"pansharpen.tiff"
            gdal_pansharpen(["pass", pan_ortho_path, mss_registration_path, pansharpen_path])
            logging.info(f"融合图像生成: {os.path.basename(pansharpen_path)}")

            # 创建金字塔（可选，视情况保留或移除）
            logging.info("创建金字塔...")
            build_pyramid(pansharpen_path)

            # 将融合后的 TIFF 文件移动到输出目录
            dest_pansharpen_path = os.path.join(output_dir, os.path.basename(pansharpen_path))
            shutil.move(pansharpen_path, dest_pansharpen_path)
            logging.info(f"融合图像已移动到: {dest_pansharpen_path}")

        except Exception as e:
            logging.error(f"处理 {tar_unpackage_dir} 时出错: {e}")
            continue  # 继续处理下一个解压目录

        finally:
            # 删除解压后的临时文件夹
            try:
                shutil.rmtree(tar_unpackage_dir)
                logging.info(f"已删除临时文件夹: {tar_unpackage_dir}")
            except Exception as e:
                logging.error(f"删除临时文件夹 {tar_unpackage_dir} 时出错: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='预处理地理空间数据并保存融合后的 TIFF 文件。')
    parser.add_argument('--dem', default=r"C:\Program Files\Harris\ENVI56\data\GMTED2010.jp2", help='DEM 文件的路径。')
    parser.add_argument('--tar_dir', default=r"E:\dataset\bridge\1", help='包含 .tar.gz 压缩包的目录。')
    parser.add_argument('--output_dir', default=r"E:\dataset\bridge\fused_tiffs2", help='保存融合后 TIFF 文件的输出目录。')
    args = parser.parse_args()

    preprocess(args.dem, args.tar_dir, args.output_dir)
