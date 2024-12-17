import os


def check_images_folders():
    # 获取当前目录
    current_dir = os.getcwd()

    # 获取所有一级子文件夹
    first_level_folders = [os.path.join(current_dir, name) for name in os.listdir(current_dir) if
                           os.path.isdir(os.path.join(current_dir, name))]

    # 检查每个一级子文件夹中的二级子文件夹是否包含images文件夹
    for first_level_folder in first_level_folders:
        second_level_folders = [os.path.join(first_level_folder, name) for name in os.listdir(first_level_folder) if
                                os.path.isdir(os.path.join(first_level_folder, name))]
        for second_level_folder in second_level_folders:
            images_folder = os.path.join(second_level_folder, 'images')
            if not os.path.exists(images_folder):
                print(second_level_folder)


# 执行检查函数
check_images_folders()
