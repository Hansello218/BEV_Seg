import os
import numpy as np
from PIL import Image
import cv2
from skimage.morphology import skeletonize
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev
import argparse
from tqdm import tqdm

def save_image(image, path, title):
    """保存并显示图像的辅助函数"""
    plt.figure(figsize=(10, 10))
    plt.imshow(image, cmap='gray' if len(image.shape) == 2 else None)
    plt.title(title)
    plt.axis('off')
    plt.savefig(path)
    plt.close()

def parse_args():
    parser = argparse.ArgumentParser(description="Process images with optional operations for lane detection.")
    parser.add_argument("--input_dir", type=str, required=True, help="Directory containing input images.")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory to save output images and data.")
    parser.add_argument("--disable_morphology", action="store_true", help="Disable morphological operations.")
    return parser.parse_args()

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

    save_image(img_array, os.path.join(save_dir, '01_morphed.png'), 'Morphed Image')

    # 轮廓检测
    contours, _ = cv2.findContours(img_array, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    img_array_color = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)

    for contour in contours:
        # 创建针对每个轮廓的掩码
        mask = np.zeros_like(img_array)
        cv2.drawContours(mask, [contour], -1, 255, -1)

        # 骨架提取
        skeleton = skeletonize(mask // 255).astype(np.uint8)

        # B样条拟合
        y, x = np.where(skeleton)  # 获取非零像素的坐标
        if len(x) >= 4:  # 确保有足够的点进行B样条拟合
            tck, u = splprep([x, y], s=1)
            u_new = np.linspace(u.min(), u.max(), 100)
            x_new, y_new = splev(u_new, tck)

            for i in range(len(x_new) - 1):
                cv2.line(img_array_color, (int(x_new[i]), int(y_new[i])), (int(x_new[i+1]), int(y_new[i+1])), (0, 255, 0), 2)

    save_image(img_array_color, os.path.join(save_dir, '02_processed.png'), 'Processed Image')

def batch_process_images(input_dir, output_dir, args):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    img_names = os.listdir(input_dir)
    for img_name in tqdm(img_names):
        if img_name.endswith('.jpg'):
            img_path = os.path.join(input_dir, img_name)
            process_image(img_path, output_dir, args)

def main():
    args = parse_args()
    batch_process_images(args.input_dir, args.output_dir, args)

if __name__ == "__main__":
    main()
