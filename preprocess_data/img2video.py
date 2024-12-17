import cv2
import os

def images_to_video(images_folder, output_video, fps=60):
    # 获取图片文件夹中的所有图片文件名，并按照文件名排序
    #image_files = sorted([os.path.join(images_folder, file) for file in os.listdir(images_folder) if file.endswith(('jpg', 'jpeg', 'png'))])
    image_files = sorted([os.path.join(images_folder, file) for file in os.listdir(images_folder) if
                          file.endswith(('jpg', 'jpeg', 'png'))], key=lambda x: int(''.join(filter(str.isdigit, x))))

    # 读取第一张图片以获取其尺寸
    img = cv2.imread(image_files[0])
    height, width, _ = img.shape

    # 创建视频编写器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    # 逐个将图片写入视频
    for image_file in image_files:
        img = cv2.imread(image_file)
        video_writer.write(img)

    # 释放资源
    video_writer.release()

# 指定图片文件夹路径和输出视频路径
images_folder = r'D:\python_projects\workplace\bytetree\PhysGaussian\test'
output_video = r'D:\python_projects\workplace\bytetree\PhysGaussian\test\output.mp4'

# 指定帧率

fps = 30

# 调用函数将图片转换为视频
images_to_video(images_folder, output_video, fps)
