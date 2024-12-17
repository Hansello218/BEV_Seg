import os
import numpy as np
from PIL import Image
import cv2
import matplotlib.pyplot as plt
from skimage.morphology import skeletonize
from scipy.interpolate import splprep, splev
from shapely.geometry import LineString
import argparse
from tqdm import tqdm

def parse_args():
    parser = argparse.ArgumentParser(description="Process images with configurable options.")
    parser.add_argument("--input_dir", default=r'D:\python_projects\workplace\bytetree\SegFormer\tools\preprocess_data\check', type=str, help="Directory containing input images.")
    parser.add_argument("--output_dir", default=r'D:\python_projects\workplace\bytetree\SegFormer\tools\preprocess_data\check_show', type=str, help="Directory to save output images and data.")
    parser.add_argument("--enable_morphology", default=True, action="store_true", help="Enable morphological operations to close gaps.")
    parser.add_argument("--enable_contour_detection", default=True, action="store_true", help="Enable contour detection for extracting shapes.")
    parser.add_argument("--enable_rd_simplification", default=False, action="store_true", help="Enable Ramer-Douglas-Peucker simplification for lines.")
    return parser.parse_args()

def process_image(image_path, save_dir, args):
    img = Image.open(image_path).convert('L')
    img_array = np.array(img)

    # 二值化处理
    mask = (img_array >= 70) & (img_array <= 130)
    img_array[mask] = 255
    img_array[~mask] = 0

    if args.enable_morphology:
        kernel = np.ones((5, 5), np.uint8)
        img_array = cv2.morphologyEx(img_array, cv2.MORPH_CLOSE, kernel)
        img_array = cv2.morphologyEx(img_array, cv2.MORPH_OPEN, kernel)

    if args.enable_contour_detection:
        contours, _ = cv2.findContours(img_array, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
        for contour in contours:
            if args.enable_rd_simplification:
                simplified_contour = simplify_contour(contour)
                cv2.drawContours(img_array, [simplified_contour], -1, (0, 255, 0), 2)
            else:
                cv2.drawContours(img_array, [contour], -1, (0, 255, 0), 2)

    #Save the processed image
    plt.figure(figsize=(20, 20))
    plt.imshow(img_array)
    plt.axis('off')
    plt.savefig(os.path.join(save_dir, os.path.basename(image_path)))
    plt.close()

def simplify_contour(contour, epsilon=1.0):
    """ Simplify contour using Ramer-Douglas-Peucker algorithm """
    polyline = LineString(contour.reshape(-1, 2))
    simplified = polyline.simplify(epsilon, preserve_topology=False)
    return np.array(simplified.coords).reshape(-1, 1, 2)

def batch_process_images(input_dir, output_dir, args):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for img_name in tqdm(os.listdir(input_dir)):
        if img_name.lower().endswith('.jpg'):
            img_path = os.path.join(input_dir, img_name)
            process_image(img_path, output_dir, args)
def main():
    args = parse_args()
    batch_process_images(args.input_dir, args.output_dir, args)  # 确保传递 args 参数

if __name__ == "__main__":
    main()




# input_dir = r'D:\python_projects\workplace\bytetree\SegFormer\tools\preprocess_data\check'
# output_dir = r'D:\python_projects\workplace\bytetree\SegFormer\tools\preprocess_data\check'
#
# # 批量处理图片
# batch_process_images(input_dir, output_dir)
# print("Batch processing complete.")
