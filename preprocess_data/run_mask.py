import os
import subprocess

# 当前路径下的所有文件夹
current_path = os.getcwd()
subfolders = [f.path for f in os.scandir(current_path) if f.is_dir()]

# 遍历每个文件夹
for folder in subfolders:
    # 获取子文件夹列表
    sub_subfolders = [f.path for f in os.scandir(folder) if f.is_dir()]

    # 遍历子文件夹
    for sub_folder in sub_subfolders:
        print("处理文件夹:", sub_folder)

        # 获取geojson文件夹和mask_output文件夹的路径
        geojson_folder = os.path.join(sub_folder, 'geojson')
        mask_output_folder = os.path.join(sub_folder, 'mask_output')

        # 获取segment_coord.json文件路径
        segment_coord_json = os.path.join(geojson_folder, 'segment_coord.json')

        # 检查路径是否存在
        if os.path.exists(geojson_folder) and os.path.exists(mask_output_folder) and os.path.exists(segment_coord_json):
            # 构建命令行参数
            cmd = ["python", "geojson2mask.py", "--geojson", geojson_folder, "-sp", mask_output_folder, "-mp", segment_coord_json]

            # 运行命令
            subprocess.run(cmd)

print("处理完成")
