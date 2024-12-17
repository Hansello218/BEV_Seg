import os
import subprocess
from tqdm import tqdm

# 获取当前工作目录
current_dir = os.getcwd()

# 获取一级子文件夹列表
root, dirs, files = next(os.walk(current_dir))

# 设置外部进度条
outer_pbar = tqdm(total=len(dirs), desc='Processing top-level folders', unit='folder')

# 遍历一级子文件夹
for dir_name in dirs:
    sub_dir_path = os.path.join(root, dir_name)

    # 获取二级子文件夹列表
    sub_root, sub_dirs, sub_files = next(os.walk(sub_dir_path))

    # 设置内部进度条
    inner_pbar = tqdm(total=len(sub_dirs), desc=f'Processing {dir_name}', unit='folder', leave=False)

    # 遍历二级子文件夹
    for sub_dir_name in sub_dirs:
        second_level_sub_dir_path = os.path.join(sub_root, sub_dir_name)

        # 创建ImageSets文件夹
        imagesets_path = os.path.join(second_level_sub_dir_path, 'ImageSets')
        if not os.path.exists(imagesets_path):
            os.makedirs(imagesets_path)

        # 创建Segmentation文件夹
        segmentation_path = os.path.join(imagesets_path, 'Segmentation')
        if not os.path.exists(segmentation_path):
            os.makedirs(segmentation_path)

        # 执行脚本voc_data_process.py
        command = [
            'python', os.path.join(current_dir, 'voc_data_process.py'),
            '--segfilepath', second_level_sub_dir_path,
            '--saveBasePath', segmentation_path
        ]
        subprocess.run(command)

        # 更新内部进度条
        inner_pbar.update(1)

    # 关闭内部进度条
    inner_pbar.close()

    # 更新外部进度条
    outer_pbar.update(1)

# 关闭外部进度条
outer_pbar.close()
