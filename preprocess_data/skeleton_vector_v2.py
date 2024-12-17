import os
import numpy as np
from PIL import Image
import cv2
from skimage.morphology import skeletonize
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev
import argparse
from tqdm import tqdm
import json


def process_image(image_path, save_dir, args):
    img = Image.open(image_path).convert('L')
    img_array = np.array(img)

    # 二值化处理
    mask = (img_array >= 70) & (img_array <= 130)
    img_array[mask] = 255
    img_array[~mask] = 0

    if not args.disable_morphology:
        kernel = np.ones((5, 5), np.uint8)
        img_array = cv2.morphologyEx(img_array, cv2.MORPH_CLOSE, kernel)
        img_array = cv2.morphologyEx(img_array, cv2.MORPH_OPEN, kernel)

    # 骨架提取
    skeleton = skeletonize(img_array // 255).astype(np.uint8)
    y, x = np.where(skeleton)  # 获取骨架中非零元素的坐标

    if len(x) >= 4:
        # B样条拟合
        tck, u = splprep([x, y], s=1)
        u_new = np.linspace(u.min(), u.max(), 100)
        x_new, y_new = splev(u_new, tck)

        # 准备图像显示
        img_array_color = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
        for i in range(len(x_new) - 1):
            cv2.line(img_array_color, (int(x_new[i]), int(y_new[i])), (int(x_new[i+1]), int(y_new[i+1])), (0, 255, 0), 2)

        # 保存最终处理后的图像
        final_image_path = os.path.join(save_dir, os.path.splitext(os.path.basename(image_path))[0] + '_final.png')
        cv2.imwrite(final_image_path, img_array_color)

        # 保存矢量点数据到JSON文件
        vector_points = list(zip(x_new, y_new))
        vector_data_path = os.path.join(save_dir, os.path.splitext(os.path.basename(image_path))[0] + '_vectors.json')
        with open(vector_data_path, 'w') as f:
            json.dump(vector_points, f)

def batch_process_images(input_dir, output_dir, args):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    img_names = os.listdir(input_dir)
    for img_name in tqdm(img_names):
        if img_name.endswith('.jpg'):
            img_path = os.path.join(input_dir, img_name)
            process_image(img_path, output_dir, args)

def parse_args():
    parser = argparse.ArgumentParser(description="控制形态学操作开关")
    parser.add_argument("--input_dir", default=r'D:\python_projects\workplace\bytetree\SegFormer\tools\preprocess_data\result2_20230824_2.43km_LTZJ186', type=str)
    parser.add_argument("--output_dir", default=r'D:\python_projects\workplace\bytetree\SegFormer\tools\preprocess_data\vis_skeleton_b_0824_186_v3', type=str)
    parser.add_argument("--disable_morphology", default=True, action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    batch_process_images(args.input_dir, args.output_dir, args)

if __name__ == "__main__":
    main()
