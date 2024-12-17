import os
import shutil
import argparse
from tqdm import tqdm

def copy_images(root_folder, destination_folder):
    # 统计图片总数
    total_files = sum(len(files) for _, _, files in os.walk(root_folder))

    # 初始化进度条
    progress_bar = tqdm(total=total_files, desc="Copying images", unit="image")

    # 遍历根目录下的所有文件夹
    for subdir in os.listdir(root_folder):
        subdir_path = os.path.join(root_folder, subdir)
        if os.path.isdir(subdir_path):
            # 目标文件夹中子文件夹的路径
            destination_subdir = os.path.join(destination_folder, subdir)
            images_folder = os.path.join(destination_subdir, "images")
            os.makedirs(images_folder, exist_ok=True)

            # 查找当前文件夹下的 bev_output_2k 文件夹
            bev_output_2k_folder = os.path.join(subdir_path, "bev_output_2k")
            if os.path.exists(bev_output_2k_folder):
                # 遍历 bev_output_2k 文件夹中的所有文件
                for filename in os.listdir(bev_output_2k_folder):
                    source_file = os.path.join(bev_output_2k_folder, filename)
                    if os.path.isfile(source_file):
                        # 复制文件到目标文件夹的 images 文件夹中
                        destination_file = os.path.join(images_folder, filename)
                        shutil.copy(source_file, destination_file)
                        progress_bar.update(1)

    progress_bar.close()
    print("图片复制完成。")

def main():
    parser = argparse.ArgumentParser(description="Copy images.")
    parser.add_argument("-r", "--root_folder", type=str, required=True, help="Root folder path.")
    parser.add_argument("-d", "--destination_folder", type=str, required=True, help="Destination folder path.")
    args = parser.parse_args()

    copy_images(args.root_folder, args.destination_folder)

if __name__ == "__main__":
    main()
