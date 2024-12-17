import os
import numpy as np
from PIL import Image
from tqdm import tqdm


def process_image(image_path, save_path):
    # 打开图像
    img = Image.open(image_path)
    # 转换为numpy数组
    img_array = np.array(img)

    # 将像素值在70到130之间的像素转换为100
    mask = (img_array >= 70) & (img_array <= 130)
    img_array[mask] = 100

    # 转换回PIL图像并保存
    result_img = Image.fromarray(img_array)
    result_img.save(save_path)


def batch_process_images(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    img_names = os.listdir(input_dir)

    for img_name in tqdm(img_names):
        if img_name.endswith('.jpg') or img_name.endswith('.png'):
            img_path = os.path.join(input_dir, img_name)
            save_path = os.path.join(output_dir, img_name)
            process_image(img_path, save_path)


# 输入和输出文件夹路径
input_dir = r'D:\python_projects\workplace\bytetree\SegFormer\tools\preprocess_data\result2_20230824_2.43km_LTZJ186'  # 请替换为你的输入文件夹路径
output_dir = r'D:\python_projects\workplace\bytetree\SegFormer\tools\preprocess_data\result2'  # 请替换为你的输出文件夹路径

# 批量处理图片
batch_process_images(input_dir, output_dir)

print("Batch processing complete.")
