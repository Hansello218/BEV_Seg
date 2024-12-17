import os
import shutil
import argparse
from tqdm import tqdm

def copy_folders(src, dst):
    # 获取所有一级子文件夹
    first_level_folders = [os.path.join(src, name) for name in os.listdir(src) if os.path.isdir(os.path.join(src, name))]

    # 统计所有二级子文件夹
    second_level_folders = []
    for first_level_folder in first_level_folders:
        second_level_folders.extend([os.path.join(first_level_folder, name) for name in os.listdir(first_level_folder) if os.path.isdir(os.path.join(first_level_folder, name))])

    # 复制二级子文件夹到目标路径
    for folder in tqdm(second_level_folders, desc="Copying folders", unit="folder"):
        shutil.copytree(folder, os.path.join(dst, os.path.basename(folder)))

def main():
    parser = argparse.ArgumentParser(description="Copy all second-level subfolders to a specified directory with progress visualization.")
    parser.add_argument("destination", type=str, help="The destination directory to copy the folders to.")
    args = parser.parse_args()

    # 获取当前目录
    current_dir = os.getcwd()

    # 创建目标路径如果不存在
    if not os.path.exists(args.destination):
        os.makedirs(args.destination)

    # 执行复制
    copy_folders(current_dir, args.destination)

if __name__ == "__main__":
    main()
