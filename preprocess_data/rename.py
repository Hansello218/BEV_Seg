import os
import shutil
import argparse

def process_folders(root_folder, destination_folder):
    # 遍历根文件夹下的每个子文件夹
    for subdir in os.listdir(root_folder):
        subdir_path = os.path.join(root_folder, subdir)
        if os.path.isdir(subdir_path):
            print(f"Processing folder: {subdir}")
            # 创建目标文件夹路径，只使用子文件夹的名称
            destination_subdir = os.path.join(destination_folder, subdir)
            os.makedirs(destination_subdir, exist_ok=True)

            # 创建 geojson 和 mask_output 文件夹
            geojson_folder = os.path.join(destination_subdir, "geojson")
            os.makedirs(geojson_folder, exist_ok=True)
            mask_output_folder = os.path.join(destination_subdir, "mask_output")
            os.makedirs(mask_output_folder, exist_ok=True)

            # 复制 bev_output 中的 JSON 文件到 geojson 文件夹
            bev_output_json = os.path.join(subdir_path, "bev_output", "segment_coord.json")
            if os.path.exists(bev_output_json):
                shutil.copy(bev_output_json, os.path.join(geojson_folder, "segment_coord.json"))

            # 复制标注件文件夹中的指定文件到 geojson 文件夹
            annotation_folder = os.path.join(subdir_path, "标注件")
            if os.path.exists(annotation_folder):
                # 遍历标注件文件夹下的所有文件
                for root, dirs, files in os.walk(annotation_folder):
                    for filename in files:
                        if filename.endswith(".geojson"):
                            source_file = os.path.join(root, filename)
                            destination_file = os.path.join(geojson_folder, filename)
                            shutil.copy(source_file, destination_file)

                            # 根据文件名重命名
                            if filename == "标线标注.geojson":
                                os.rename(destination_file, os.path.join(geojson_folder, "biaoxian.geojson"))
                            elif filename == "箭头标注.geojson":
                                os.rename(destination_file, os.path.join(geojson_folder, "jiantou.geojson"))
                            elif filename == "路沿标注.geojson":
                                os.rename(destination_file, os.path.join(geojson_folder, "luyan.geojson"))

    print("操作完成。")

def main():
    parser = argparse.ArgumentParser(description="Process folders.")
    parser.add_argument("-r", "--root_folder", type=str, required=True, help="Root folder path.")
    parser.add_argument("-d", "--destination_folder", type=str, required=True, help="Destination folder path.")
    args = parser.parse_args()

    process_folders(args.root_folder, args.destination_folder)

if __name__ == "__main__":
    main()
