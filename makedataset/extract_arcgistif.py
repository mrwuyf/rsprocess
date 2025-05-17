import os
import shutil


def extract_tif_files(src_folder, dst_folder):
    # 如果目标文件夹不存在则创建
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)

    # 遍历源文件夹中的所有文件和子文件夹
    for filename in os.listdir(src_folder):
        file_path = os.path.join(src_folder, filename)

        # 检查是否为文件，并判断后缀名是否为.tif
        if os.path.isfile(file_path) and filename.lower().endswith('.tif'):
            # 构造目标文件路径
            dst_file_path = os.path.join(dst_folder, filename)

            # 复制文件
            shutil.copy2(file_path, dst_file_path)

    print("tif文件已全部复制到目标文件夹。")

def rename_images_in_folder(folder_path):
    # 获取上上级目录名（即文件夹本身的父级目录的目录名）
    # 当前目录为 images，则一层上去是 GF2_99642001，再上一层是 makelabel
    # 本例中需要的是 GF2_99642001，即文件夹的上一级目录名
    parent_folder = os.path.dirname(folder_path)  # D:\GraduateFile\program\makelabel\GF2_99642001
    parent_folder_name = os.path.basename(parent_folder)  # GF2_99642001

    # 遍历文件夹中的每一个文件
    for filename in os.listdir(folder_path):
        old_file_path = os.path.join(folder_path, filename)

        # 确保是文件
        if os.path.isfile(old_file_path):
            # 新的文件名格式：上上级目录名_原文件名
            new_filename = f"{parent_folder_name}_{filename}"
            new_file_path = os.path.join(folder_path, new_filename)
            os.rename(old_file_path, new_file_path)

    print("重命名完成！")


def normalize_filenames(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.tif'):
            old_path = os.path.join(folder_path, filename)

            if os.path.isfile(old_path):
                # 分离文件名和扩展名
                name_part, ext = os.path.splitext(filename)

                # 假设格式为 [prefix]_[number]，例如：GF2_99642001_000000000016
                # 以最后一个下划线为分隔点
                parts = name_part.rsplit('_', 1)
                if len(parts) == 2:
                    prefix = parts[0]  # GF2_99642001
                    num_str = parts[1]  # 000000000016

                    # 转为整数再格式化为6位数字
                    num_int = int(num_str)
                    new_num_str = f"{num_int:06d}"

                    new_filename = f"{prefix}_{new_num_str}{ext}"
                    new_path = os.path.join(folder_path, new_filename)

                    # 重命名
                    os.rename(old_path, new_path)
    print("文件名格式化完成。")



if __name__ == '__main__':
    extract_tif_files(r"E:\dataset\chitang\bridge197\1", r"E:\dataset\chitang\crop2")
    # rename_images_in_folder(r"E:\dataset\chitang\bridge197\1")
    # normalize_filenames(r"E:\dataset\chitang\bridge197\1")