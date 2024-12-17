from PIL import Image
import os
import re
from PIL import Image
import os
from tqdm import tqdm
import cv2


def convert_to_single_channel(input_folder, output_folder):
    # 确保输出文件夹存在，如果不存在则创建
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 获取输入文件夹中的图片文件列表，并按数字编号排序
    image_files = sorted(
        [filename for filename in os.listdir(input_folder) if filename.endswith(".jpg") or filename.endswith(".png")],
        key=lambda x: int(re.search(r'\d+', os.path.splitext(x)[0]).group()))

    # 使用 tqdm 显示进度条
    for filename in tqdm(image_files, desc="Converting images", unit="image"):
        # 打开图像
        img = Image.open(os.path.join(input_folder, filename))

        # 将图像转换为灰度图像
        gray_img = img.convert("L")

        # 获取图像的宽度和高度
        width, height = gray_img.size

        # 创建一个新的图像，模式为单通道 (L)
        single_channel_img = Image.new("L", (width, height))

        # 遍历图像的每个像素
        for y in range(height):
            for x in range(width):
                # 获取当前像素的颜色值 (R, G, B)
                r, g, b = img.getpixel((x, y))

                # 将颜色映射为单通道值
                if r == 255 and g == 0 and b == 0:  # 红色
                    single_channel_img.putpixel((x, y), 1)
                elif r == 0 and g == 255 and b == 0:  # 绿色
                    single_channel_img.putpixel((x, y), 2)
                elif r == 0 and g == 0 and b == 255:  # 蓝色
                    single_channel_img.putpixel((x, y), 3)
                else:  # 其他颜色，即黑色
                    single_channel_img.putpixel((x, y), 0)

        # 构建输出文件名
        output_filename = os.path.splitext(filename)[0] + ".png"
        output_path = os.path.join(output_folder, output_filename)
        # 保存单通道图像为 PNG 格式
        single_channel_img.save(output_path, format='PNG')

input_folder = "Masks_output"  # 输入图像文件夹路径
output_folder = "Labels_output"  # 输出图像文件夹路径
convert_to_single_channel(input_folder, output_folder)
# img = cv2.imread("Labels_output/mask_0_single_channel.png", cv2.IMREAD_GRAYSCALE)
# print(img)
