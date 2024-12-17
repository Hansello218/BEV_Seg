import os
import re
import argparse

def rename_images(folder_path):
    # 获取文件夹下所有文件名
    files = os.listdir(folder_path)

    # 匹配文件名中的数字部分的正则表达式
    pattern = r'(\d+)_BEV_(\d+)_sub_(\d+)\.jpg'

    # 存储匹配结果的列表
    file_infos = []

    # 提取和排序文件名中的数字部分
    for filename in files:
        match = re.search(pattern, filename)
        if match:
            bev_number = int(match.group(2))  # BEV后面的数字
            sub_number = int(match.group(3))  # sub后面的数字
            file_infos.append((filename, bev_number, sub_number))

    # 根据BEV后面的数字和sub后面的数字排序文件信息
    file_infos.sort(key=lambda x: (x[1], x[2]))

    # 重命名文件并保存
    for idx, (filename, _, _) in enumerate(file_infos):
        new_filename = f'mask_{idx}.jpg'
        os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_filename))
        print(f'Renamed {filename} to {new_filename}')

    print('All files renamed successfully.')

def main():
    parser = argparse.ArgumentParser(description='Rename images in a folder based on specified pattern.')
    parser.add_argument('folder_path', type=str, help='Path to the folder containing images.')
    args = parser.parse_args()

    rename_images(args.folder_path)

if __name__ == '__main__':
    main()
