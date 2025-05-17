from rs_process.makedataset.tifpreprocess import batch_stretch, process_rgb_directory

if __name__ == '__main__':
    input_dir = r"E:\huanghe\test\clip1"
    stretch_dir = r"E:\huanghe\test\clip1_8bit"
    rgb_dir = r"E:\huanghe\test\clip1_rgb"
    batch_stretch(input_dir, stretch_dir)
    process_rgb_directory(stretch_dir, rgb_dir)