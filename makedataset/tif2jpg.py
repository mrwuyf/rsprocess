from PIL import Image
import os


def convert_tif_to_jpg(input_folder, output_folder, quality=95):
    """
    将指定文件夹中的TIFF图像转换为JPEG格式并保存到目标文件夹

    参数：
    input_folder (str): 源文件夹路径（存放TIF图片）
    output_folder (str): 目标文件夹路径（保存转换后的JPG图片）
    quality (int): 可选参数，JPEG保存质量（默认95）
    """
    # 创建目标文件夹（如果不存在）
    os.makedirs(output_folder, exist_ok=True)

    # 遍历源文件夹中的所有文件
    for filename in os.listdir(input_folder):
        # 检查文件扩展名是否为.tif或.tiff（不区分大小写）
        if filename.lower().endswith(('.tif', '.tiff')):
            input_path = os.path.join(input_folder, filename)

            try:
                # 打开并转换图像
                with Image.open(input_path) as img:
                    rgb_img = img.convert('RGB')

                    # 构造输出路径
                    output_filename = os.path.splitext(filename)[0] + '.jpg'
                    output_path = os.path.join(output_folder, output_filename)

                    # 保存为JPEG格式
                    rgb_img.save(output_path, quality=quality)
                    print(f"已转换: {filename} -> {output_filename}")

            except Exception as e:
                print(f"处理 {filename} 时出错: {str(e)}")


# 使用示例
if __name__ == "__main__":
    input_dir = r'E:\dataset\chitang\crop2_rgb'
    output_dir = r'E:\dataset\chitang\crop2_jpg\images'
    convert_tif_to_jpg(input_dir, output_dir)