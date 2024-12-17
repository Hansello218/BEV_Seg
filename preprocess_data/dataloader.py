import json
import io
import os
import argparse
from argparse import ArgumentParser

def exact_left_coord_for_mask(coord_json_file):
    """
    获得每张mask的左上角世界坐标值！

    Args:
        coord_json: BEV_out_put文件将其裁剪为2k图片的json文件，其储存了每张2k图片左上角像素的绝对世界坐标
                    Example : coord_json = json.load(open("D:\python_projects\keypoint_detection\data\Bev_output\segment_coord_full.json"))
    Returns:
        coord_list: 返回一个列表，其储存了所有2k图片左上角坐标的元组

    """
    coord_json = json.load(open(coord_json_file))
    crop_2k_sub_img_coord_info = coord_json["crop_2k_sub_img_coord_info"]
    coord_list = []
    for key, value in crop_2k_sub_img_coord_info.items():
        for sub_key, sub_value in value.items():
            coord = tuple(sub_value["absolute_coord_info"])
            coord_list.append(coord)
    return coord_list

def remove_height(lst):
    """
    最高只能处理三维列表
    :param lst: 不确定维度的多维列表，三维或者四维
    :return: 返回剔除高度的多维列表
    """
    if isinstance(lst, list):
        if len(lst) > 0 and isinstance(lst[0], list):
            for i in range(len(lst)):
                lst[i] = remove_height(lst[i])
        else:
            lst = lst[:2]
    return lst


def process_dict(dictionary):
    """
    用于处理嵌套字典
    """
    for key, value in dictionary.items():
        if isinstance(value, dict):                #如果还是字典继续搜寻
            process_dict(value)
        elif isinstance(value, list):              #如果是列表，则开始剔除高度
            dictionary[key] = remove_height(value)
    return dictionary



def extract_3d_coordinates_strategy_biaoxian(file_path):
    """
    标线文件的读取策略：针对文件名为 'Biaoxian.geojson'

    Args:
        file_path: geojson 文件路径

    Returns:
        all_4d_coordinates: 将所有三维数组都全部堆叠，以四维列表输出
    """
    with open(file_path, "r", encoding='utf-8') as f:
        data = json.load(f)

        type = {
            "dotted": [],
            "straight": [],
            "diverted": [],
            "stop": [],
            "man": [],
            "jiansu":[]
        }

        for feature in data["features"]:
            geometry = feature["geometry"]
            coordinates = geometry["coordinates"]
            name = feature["properties"]["FCode"]

            if name == "401111" or name == "401116" or name == "401115" or name == "401112" or name == "401114" or name == "401119" or name == "401511" or name == "401136" or name == "401133" or name =="401117" or name == "401134" or name == "401118":
                type["dotted"].append(coordinates)     # 虚线

            elif name == "401121" or name == "401122" or name =="401141" or name == "401521" or name == "401142":
                type["straight"].append(coordinates)   # 实线

            elif name == "402038" or name == "402018" or name == "402028" or name == "401113":  # 停止线
                type["stop"].append(coordinates)

            elif name == "401124" or name == "401123" or name == "401418":  # 导向线
                type["diverted"].append(coordinates)

            elif name == "401211":  # 人行横道
                type["man"].append(coordinates)

            elif name == "401432" or name == "401433":  # 纵向减速标线
                type["jiansu"].append(coordinates)

            else:
                print(f"未识别标线FCode： {name}")

        # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # print(len(type["dotted"]) + len(type["straight"]) + len(type["stop"]) + len(type["diverted"]) + len(type["man"]) + len(type["jiansu"]))
    return type

def extract_3d_coordinates_strategy_arrow(file_path):
    """
    箭头文件读取策略：针对文件名为 'Arrow.geojson'

    Args:
        file_path: geojson 文件路径

    Returns:
        tupe: 字典中的每个列表将所有2维数组都全部堆叠，以3维列表输出
    """

    with open(file_path, "r", encoding='utf-8') as f:
        data = json.load(f)

        type = {
            "straight": [],
            "left": [],
            "straight_right": [],
            "straight_left":[],
            "right": [],
            "jinzhidiaotou": [],
            "xiangzuoheliu": [],
            "diaotou": []




        }

        for feature in data["features"]:
            geometry = feature["geometry"]
            coordinates = geometry["coordinates"]
            name = feature["properties"]["FCode"]

            if name == "401322":
                type["straight_right"].append(coordinates)  # 直行右转

            elif name == '401321':
                type["straight_left"].append(coordinates)   # 直行左转

            elif name == "401312" or name == "401338" or name == "401325":
                type["left"].append(coordinates)   # 左转

            elif name == "401313" or name == "401339" or name == "401436":
                type["right"].append(coordinates)   # 右转

            elif name == "401311":
                type["straight"].append(coordinates)   # 直行
            elif name == "401341" or name == "401342":
                type["jinzhidiaotou"].append(coordinates)   # 禁止掉头
            elif name == "401331" or name == "401332":
                type["xiangzuoheliu"].append(coordinates)   # 向左合流 向右合流
            elif name == "401314" :
                type["diaotou"].append(coordinates)   # 向左合流 向右合流


            else:
                print(f"未识别箭头： {name}")

    return type

def extract_3d_coordinates_strategy_luyan(file_path):
    """
      箭头文件读取策略：针对文件名为 'Luyan.geojson'

      Args:
          file_path: geojson 文件路径

      Returns:
          type: 字典中的列表将所有二维维数组都全部堆叠，以三维列表输出
      """
    with open(file_path, "r", encoding='utf-8') as f:
        data = json.load(f)

        type = {
            "hulan": [],
            "gaoducha": [],
            "caizhicha": []
        }

        for feature in data["features"]:
            geometry = feature["geometry"]
            coordinates = geometry["coordinates"]
            name = feature["properties"]["name"]

            if "护栏" in name:
                type["hulan"].append(coordinates)

            elif "高度差" in name:
                type["gaoducha"].append(coordinates)

            elif "材质差" in name:
                type["caizhicha"].append(coordinates)

            else:
                print(f"未识别路沿： {name}")
        # print(len(type["hulan"]))
        # print(len(type["gaoducha"]))

    return type






def extract_all_from_geojson_folder(folder_path, args):
    """
    提取文件夹中所有的 GeoJSON 文件中的世界坐标值！
    Args:
        folder_path: 包含 GeoJSON 文件的文件夹路径

    Returns:
       geojson_zoo: 将所有类型的geojson文件提中不同类型的标注以字典的形式打包
    """
    geojson_zoo = {}
    for filename in os.listdir(folder_path):
        if filename.endswith('.geojson'):
            file_path = os.path.join(folder_path, filename)
            if filename == args.biaoxian:
                geojson_zoo["biaoxian"] = extract_3d_coordinates_strategy_biaoxian(file_path)         #得到标线字典 --> 1.虚线 2.实线 3 人行横道 4 导流区 5 停止区 6. 纵向减速标线
            elif filename == args.jiantou:
                geojson_zoo["jiantou"] = extract_3d_coordinates_strategy_arrow(file_path)               #得到箭头字典 --> 1.直行右转箭头 2.左弯箭头 3.直行箭头 4右转箭头 5 直行左转箭头
            elif filename == args.luyan:                                                                                # 6.禁止掉头箭头 401341 7.向左合流 401331 右合流401332 7.掉头
                geojson_zoo["luyan"] = extract_3d_coordinates_strategy_luyan(file_path)                #得到路沿字典 --> 1.护栏式 2.高度差式 3. 材质差
            else:
                print(f"未识别标注类型: {filename}")
    return geojson_zoo



def dataload(args):
    """
    Args:
        geojson_file:  geojson文件路径
        mask_coord_file: 2k分割小图json文件路径

    Returns:
        modify_4d_coordinates_list： 一个四维列表，其保存了每个剔除高度信息的标注实例（每个标注实例是一个三维列表）
        mask_left_coord_list ： 一个保存了所有图片左上角世界坐标的列表，每个世界坐标( x, y )由元组保存
    """
    zoo = extract_all_from_geojson_folder(args.geojson_folder, args)
    no_height_zoo = process_dict(zoo)
    mask_left_coord_list = exact_left_coord_for_mask(args.mask_coord_json)

    return no_height_zoo, mask_left_coord_list

def parse_args():
    parser = argparse.ArgumentParser(description="info")
    parser.add_argument(
        '--biaoxian',
        help="需要生成mask的标注类型文件名",
        type=str,
        default='Biaoxian.geojson',
    )

    parser.add_argument(
        '--jiantou',
        help="需要生成mask的标注类型文件名",
        type=str,
        default='Arrow.geojson',
    )
    parser.add_argument(
        '--luyan',
        help="需要生成mask的标注类型文件名",
        type=str,
        default='Luyan.geojson',
    )
    parser.add_argument(
        '--geojson_folder',
        help="设置geojson文件路径",
        type=str,
        default='geojson',
    )
    parser.add_argument(
        '-mp',
        '--mask_coord_json',
        help="设置mask_json文件路径",
        type=str,
        default='D:\python_projects\keypoint_detection\data\Bev_output\segment_coord_full.json',
    )
    return parser.parse_args()

#测试

if __name__ == "__main__":
    args = parse_args()
    zoo, mask_left_crood_list = dataload(args)
    print(zoo)
    print(mask_left_crood_list)
