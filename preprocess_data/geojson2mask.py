
import numpy as np
import cv2
from dataloader import dataload
import json
import os
from tqdm import tqdm
from argparse import ArgumentParser
import argparse
# from shapely.geometry import Point, Polygon
from skimage.draw import polygon
from skimage.draw import polygon
from multiprocessing import Pool, cpu_count



def generate_polygon_mask(segs, x_threshold, y_threshold):

    M = np.zeros((2000, 2000),dtype=np.uint8)


    x = []
    y = []
    for one in segs:
        x.append(int((one[0] - x_threshold[0]) * 2000 / (x_threshold[1] - x_threshold[0])) - 1)
        y.append(int(2000 - (one[1] - y_threshold[0]) * 2000 / (y_threshold[1] - y_threshold[0])) - 1)
    rr, cc = polygon(x,y)
    # rr = np.clip(rr, 0, 1999)
    # cc = np.clip(cc, 0, 1999)
    rrmask = np.logical_and(rr >= 0, rr <= 1999)
    ccmask = np.logical_and(cc >= 0, cc <= 1999)
    combinemask = np.logical_and(rrmask, ccmask)
    M[rr[combinemask], cc[combinemask]] = 1
    coord = list(zip(rr[combinemask], cc[combinemask]))


    return coord



# def generate_grid_points_in_polygon(points_list, grid_spacing=0.1):
#     """
#     生成多边形内的所有网格点坐标。
#
#     参数:
#     - points_list: 包含多边形顶点坐标的二维列表，如 [[x11, y11], [x12, y12], ...].
#     - grid_spacing: 网格点的间距，默认为0.025.
#
#     返回值:
#     - grid_points: 多边形内所有网格点坐标的列表，如 [(x1, y1), (x2, y2), ...].
#     """
#     # 创建多边形对象
#     polygon = Polygon(points_list)
#
#     # 确定边界框
#     min_x, min_y, max_x, max_y = polygon.bounds
#
#     # 生成网格点坐标
#     grid_points = []
#     # 以网格间距为步长，在边界框内生成可能的点
#     for x in np.arange(min_x, max_x, grid_spacing):
#         for y in np.arange(min_y, max_y, grid_spacing):
#             point = Point(x, y)
#             # 判断点是否在多边形内部
#             if polygon.contains(point):
#                 grid_points.append((x, y))
#
#     return grid_points

def check_points_within_threshold(points, x_threshold, y_threshold):
    """
    在世界坐标系下搜索geojson文件中标注点是否落在了mask图片中！
    Args：
        points：要检查的点集，形如 [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
        x_threshold：x坐标的阈值范围，(min_x, max_x)   --->   2k图片左上角的坐标x=min_x 右下角坐标x=max_x  max_x = min_x + 2000*0.025
        y_threshold：y坐标的阈值范围，(min_y, max_y)   --->   2k图片左上角的坐标y=max_x 右下角坐标y=min_x  max_y = min_y + 2000*0.025
    Returns：

        如果一组标注线的所有点都在范围内，返回 True；否则返回 False。
    """
    for x, y in points:
        if not (x_threshold[0] <= x <= x_threshold[1] and y_threshold[0] <= y <= y_threshold[1]):
            return False
    return True

#
# def process_three_dimensional_array(three_dimensional_lst, x_threshold, y_threshold):
#     """
#     处理三维数组，并返回满足条件的点集！
#     Args：
#         three_dimensional_array：三维列表 ---> [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]]]
#         x_threshold
#         y_threshold
#     Returns：
#         返回一个包含满足条件的四边形的列表 ---> [[[x11, y11], [x12, y12], [x13, y13], [x14, y14]], ...] ---> 确保一组标注的所有点储存在一个list中， 避免在连线阶段出现错连的现象
#     """
#     # 存储满足条件的n边形列表
#     all_quads = []
#
#     for two_dimensional_lst in three_dimensional_lst:
#
#
#         for one_dimensional_lst in two_dimensional_lst: # 检测点是否落在了每张图片框里
#             x, y = one_dimensional_lst
#             # 检查点是否在阈值范围内
#             if x_threshold[0] <= x <= x_threshold[1] and y_threshold[0] <= y <= y_threshold[1]:
#                 two_dimensional_lst_clip = generate_polygon_mask(two_dimensional_lst, x_threshold, y_threshold)  # 获得的是世界坐标系下多边形中所有点的坐标
#         # 如果二维数组中的所有一维数组都在范围内，且有element个点，则记录这些点
#         # if len(quad_within_threshold) == elements and check_points_within_threshold(quad_within_threshold, x_threshold, y_threshold):
#
#             # all_quads.append(tuple(quad_within_threshold))
#         all_quads.append(two_dimensional_lst_clip)
#
#
#     return all_quads

def process_three_dimensional_array(three_dimensional_lst, x_threshold, y_threshold):
    """
    处理三维数组，并返回满足条件的点集！
    Args：
        three_dimensional_lst：三维列表 ---> [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]]]
        x_threshold
        y_threshold
    Returns：
        返回一个包含满足条件的四边形的列表 ---> [[[x11, y11], [x12, y12], [x13, y13], [x14, y14]], ...]
    """
    # 存储满足条件的四边形列表
    all_quads = []

    for two_dimensional_lst in three_dimensional_lst:
        quad_within_threshold = None

        for one_dimensional_lst in two_dimensional_lst:
            x, y = one_dimensional_lst
            # 如果点在阈值范围内，则生成多边形坐标并跳出循环
            if x_threshold[0] <= x <= x_threshold[1] and y_threshold[0] <= y <= y_threshold[1]:
                quad_within_threshold = generate_polygon_mask(two_dimensional_lst, x_threshold, y_threshold)
                break

        # 如果找到符合条件的多边形，则添加到列表中
        if quad_within_threshold is not None:
            all_quads.append(quad_within_threshold)

    return all_quads



def linear_interpolation(point1, point2, num_steps):
    """
    线性插值函数，根据给定的两个点和步数，返回插值后的点列表
    """
    interpolated_points = []
    for i in range(num_steps):
        # 计算每一步的插值点
        x = point1[0] + (point2[0] - point1[0]) * (i + 1) / (num_steps + 1)
        y = point1[1] + (point2[1] - point1[1]) * (i + 1) / (num_steps + 1)
        interpolated_points.append([x, y])
    return interpolated_points

def interpolate_2d_list(input_list, num_steps):
    """
    在二维列表中进行线性插值
    """
    interpolated_list = []
    for i in range(len(input_list) - 1):
        # 对每对相邻的一维列表进行插值
        point1 = input_list[i]
        point2 = input_list[i + 1]
        interpolated_points = linear_interpolation(point1, point2, num_steps)
        interpolated_list.extend(interpolated_points)
    return interpolated_list


def process_three_dimensional_array_line(three_dimensional_lst, x_threshold, y_threshold):
    """
    从线条中提取点集，无需判断是否一个实例的所有点均在其中
    """
    # 存储满足条件的线条
    all_quads = []

    for two_dimensional_lst in three_dimensional_lst:

        two_dimensional_lst = interpolate_2d_list(two_dimensional_lst, 10)
        # elements = len(two_dimensional_lst)
        quad_within_threshold = []

        for one_dimensional_lst in two_dimensional_lst:
            x, y = one_dimensional_lst
            # 检查点是否在阈值范围内
            if x_threshold[0] <= x <= x_threshold[1] and y_threshold[0] <= y <= y_threshold[1]:
                quad_within_threshold.append([x, y])
            # print(quad_within_threshold)
        # 线条无需判断是否列表中的所有点都在其中
        # if len(quad_within_threshold) == elements and check_points_within_threshold(quad_within_threshold, x_threshold, y_threshold):
            # all_quads.append(tuple(quad_within_threshold))
        all_quads.append(quad_within_threshold)
    # print("all_quads: ")
    # print(all_quads)

    return all_quads
def extract_points_from_4d_list(labels, x_threshold, y_threshold):


    all_points = []

    for list in labels:
        # array = np.array(list)
        points = process_three_dimensional_array(list, x_threshold, y_threshold)

        # 检查 points 是否为空
        if points and any(points):  # 检查 points 是否不为空
            all_points.append(points)  # 如果不为空，则将 points 添加到 all_points 中
            # print("process_not_none")
        else:
            # print("process_none")
            continue  # 如果为空，则跳过当前循环，继续下一次循环
        # if not points:
        #     continue  # 如果为空，则跳过当前循环，继续下一次循环
        #
        #
        # all_points.append(points)  # 将 points_array 添加到列表中

    return all_points


def extract_points_from_3d_list(labels, x_threshold, y_threshold):
    all_points = []
    # array = np.array(labels)
    points = process_three_dimensional_array(labels, x_threshold, y_threshold)
    points_array = points
    all_points.append(points_array)
    return all_points

def extract_points_from_3d_list_line(labels, x_threshold, y_threshold):
    """
    从线条中提取点集，无需判断是否一个实例的所有点均在其中
    """
    all_points = []
    # array = np.array(labels)
    points = process_three_dimensional_array_line(labels, x_threshold, y_threshold)
    points_array = points
    all_points.append(points_array)
    return all_points


def product_biaoxian_masks(arrays, x_threshold, y_threshold, args, mask):

    for type in arrays:   # arrays 4d type 3d
        for quad in type:  # quad 2d
            mask_biaoxian = []
            for points in quad:
                if not points:
                    continue
                x, y = points
            #     # 将坐标映射到画布上
            #     mapped_x = int((x - x_threshold[0]) * args.canvas_size[0] / (x_threshold[1] - x_threshold[0]))
            #     mapped_y = int(args.canvas_size[0] - (y - y_threshold[0]) * args.canvas_size[1] / (y_threshold[1] - y_threshold[0]))
            #     mask_biaoxian.append((mapped_x, mapped_y))
            # quad_points = np.array([mask_biaoxian], dtype=np.int32)
            # # cv2.fillPoly(mask, quad_points, args.biaoxian_color)   # (0,0,255)
                cv2.circle(mask, (x, y), 1,args.biaoxian_color, -1)
    return mask

def product_jiantou_masks(arrays, x_threshold, y_threshold, args, mask):

    for type in arrays:  # arrays 4d type 3d
        for quad in type:  # quad 2d

            for points in quad:
                if not points:
                    continue
                x, y = points
                #     # 将坐标映射到画布上
                #     mapped_x = int((x - x_threshold[0]) * args.canvas_size[0] / (x_threshold[1] - x_threshold[0]))
                #     mapped_y = int(args.canvas_size[0] - (y - y_threshold[0]) * args.canvas_size[1] / (y_threshold[1] - y_threshold[0]))
                #     mask_biaoxian.append((mapped_x, mapped_y))
                # quad_points = np.array([mask_biaoxian], dtype=np.int32)
                # # cv2.fillPoly(mask, quad_points, args.biaoxian_color)   # (0,0,255)
                cv2.circle(mask, (x, y), 1, args.jiantou_color, -1)

    return mask

def product_luyan_masks(arrays, x_threshold, y_threshold, args, mask):

    for type in arrays:  # arrays 4d type 3d
        for quad in type:  # quad 2d
            mask_luyan = []
            for points in quad:
                x, y = points
                # 将坐标映射到画布上
                mapped_x = int((x - x_threshold[0]) * args.canvas_size[0] / (x_threshold[1] - x_threshold[0]))
                mapped_y = int(args.canvas_size[0] - (y - y_threshold[0]) * args.canvas_size[1] / (
                            y_threshold[1] - y_threshold[0]))
                mask_luyan.append((mapped_x, mapped_y))
            quad_points = np.array([mask_luyan], dtype=np.int32)
            for list in quad_points:
                for i in range(len(list) - 1):
                    cv2.line(mask, tuple(list[i]), tuple(list[i + 1]), args.luyan_color, 11)
            # cv2.polylines(mask, quad_points, isClosed=False, color=args.luyan_color, thickness=50)  # (0,0,255)
    return mask


def parse_args():
    parser = argparse.ArgumentParser(description="info")
    parser.add_argument(
        '--scale',
        help="一张照片的长宽所对应的真实世界米数",
        type=int,
        default=50,
    )

    parser.add_argument(
        '--biaoxian',
        help="需要生成mask的标注类型文件名",
        type=str,
        default='biaoxian.geojson',
    )

    parser.add_argument(
        '--jiantou',
        help="需要生成mask的标注类型文件名",
        type=str,
        default='jiantou.geojson',
    )
    parser.add_argument(
        '--luyan',
        help="需要生成mask的标注类型文件名",
        type=str,
        default='luyan.geojson',
    )

    parser.add_argument(
        '--geojson_folder',
        help="设置geojson文件夹路径",
        type=str,
        default= r'D:\python_projects\workplace\bytetree\SegFormer\tools\20230901_1.96km_LTZJ260\geojson',
    )
    parser.add_argument(
        '-mp',
        '--mask_coord_json',
        help="设置mask_json文件路径",
        type=str,
        default=r'D:\python_projects\workplace\bytetree\SegFormer\tools\20230901_1.96km_LTZJ260\geojson\segment_coord.json',
    )

    parser.add_argument(
        '-sp',
        '--save_path',
        help="设置mask掩码保存路径",
        type=str,
        default=r'D:\python_projects\workplace\bytetree\SegFormer\tools\20230901_1.96km_LTZJ260\maskout_revise2',
    )

    parser.add_argument(
        '--biaoxian_color',
        help="设置标线颜色",
        type=tuple,
        default=(255, 0, 0),

    )
    parser.add_argument(
        '--jiantou_color',
        help="设置箭头颜色",
        type=tuple,
        default=(0, 255, 0),
    )

    parser.add_argument(
        '--luyan_color',
        help="设置箭头颜色",
        type=tuple,
        default=(0, 0, 255),
    )

    parser.add_argument(
        '--canvas_size',
        help="设置画布大小",
        type=tuple,
        default=(2000, 2000),
    )
    return parser.parse_args()


#测试：

if __name__ == '__main__':
    args = parse_args()

    # 提取所有标注，将所有标线实例区分，以便后续需要实例分割
    zoo, mask_left_coord_list = dataload(args)

    # # 标线标注（四维列表）
    # straight_line = zoo['biaoxian']['straight']
    # dotted_line = zoo['biaoxian']['dotted']
    # stop_area = zoo['biaoxian']['stop']
    # diverted_area = zoo['biaoxian']['diverted']
    # man_area = zoo['biaoxian']['man']
    # jiansu_area = zoo['biaoxian']['jiansu']
    #
    #
    # # 箭头标注（三维列表）
    # left_arrow = zoo['jiantou']['left']
    # right_arrow = zoo['jiantou']['right']
    # straight_right_arrow = zoo['jiantou']['straight_right']
    # straight_left_arrow = zoo['jiantou']['straight_left']
    # jinzhidiaotou_arrow = zoo['jiantou']['jinzhidiaotou']
    # xiangzuoheliu_arrow = zoo['jiantou']['xiangzuoheliu']
    # diaotou_arrow = zoo['jiantou']['diaotou']
    #
    # straight_arrow = zoo['jiantou']['straight']

    # luyan标注（三维列表）
    hulan_luyan = zoo['luyan']['hulan']
    gaoducha_luyan = zoo['luyan']['gaoducha']
    caizhicha_luyan = zoo['luyan']['caizhicha']


    num_processes = 72

    with Pool(processes=num_processes) as pool:

        # start!
        for idx, coord in enumerate(tqdm(mask_left_coord_list, desc='Custom Description')):
            # 根据每张2k图片左上角坐标设定bbox范围
            x_threshold = (coord[0], coord[0] + args.scale)
            y_threshold = (coord[1] - args.scale, coord[1])

            # biaoxian = []
            # straight_line_points = extract_points_from_4d_list(straight_line, x_threshold, y_threshold)
            # dotted_line_points = extract_points_from_4d_list(dotted_line, x_threshold, y_threshold)
            # stop_line_points = extract_points_from_4d_list(stop_area, x_threshold, y_threshold)
            # diverted_line_points = extract_points_from_4d_list(diverted_area, x_threshold, y_threshold)
            # man_area_points = extract_points_from_4d_list(man_area, x_threshold, y_threshold)
            # jiansu_area_points = extract_points_from_4d_list(jiansu_area, x_threshold, y_threshold)
            #
            # biaoxian.append(straight_line_points)
            # biaoxian.append(dotted_line_points)
            # biaoxian.append(stop_line_points)
            # biaoxian.append(diverted_line_points)
            # biaoxian.append(man_area_points)
            # biaoxian.append(jiansu_area_points)
            # # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            # # print(len(biaoxian))
            #
            #
            # jiantou = []
            # straight_arrow_points = extract_points_from_3d_list(straight_arrow, x_threshold, y_threshold)
            # left_arrow_points = extract_points_from_3d_list(left_arrow, x_threshold, y_threshold)
            # right_arrow_points = extract_points_from_3d_list(right_arrow, x_threshold, y_threshold)
            # straight_right_arrow_points = extract_points_from_3d_list(straight_right_arrow, x_threshold, y_threshold)
            # straight_left_arrow_points = extract_points_from_3d_list(straight_left_arrow, x_threshold, y_threshold)
            # jinzhidiaotou_arrow_points = extract_points_from_3d_list(jinzhidiaotou_arrow, x_threshold, y_threshold)
            # xiangzuoheliu_arrow_points = extract_points_from_3d_list(xiangzuoheliu_arrow, x_threshold, y_threshold)
            # diaotou_arrow_points = extract_points_from_3d_list(diaotou_arrow, x_threshold, y_threshold)
            # jiantou.append(straight_arrow_points)
            # jiantou.append(left_arrow_points)
            # jiantou.append(straight_right_arrow_points)
            # jiantou.append(right_arrow_points)
            # jiantou.append(straight_left_arrow_points)
            # jiantou.append(jinzhidiaotou_arrow_points)
            # jiantou.append(xiangzuoheliu_arrow_points)
            # jiantou.append(diaotou_arrow_points)



            luyan = []
            hulan_luyan_points = extract_points_from_3d_list_line(hulan_luyan, x_threshold, y_threshold)
            gaoducha_luyan_points = extract_points_from_3d_list_line(gaoducha_luyan, x_threshold, y_threshold)
            caizhicha_luyan_points = extract_points_from_3d_list_line(caizhicha_luyan, x_threshold, y_threshold)
            luyan.append(hulan_luyan_points)
            luyan.append(gaoducha_luyan_points)
            luyan.append(caizhicha_luyan_points)


            # # 有效标注点集
            # all_labels = {
            #     'biaoxian': biaoxian,
            #     'jiantou': jiantou,
            #     'luyan': luyan
            # }
            # 有效标注点集
            all_labels = {
                'luyan': luyan
            }

            # 建立mask画布并将点映射到mask上
            mask = np.zeros((args.canvas_size[1], args.canvas_size[0], 3), dtype=np.uint8)

            # # 生成标线
            # for arrays_bx in all_labels['biaoxian']:
            #     mask = product_biaoxian_masks(arrays_bx, x_threshold, y_threshold, args, mask)
            #
            #
            #
            # # 生成箭头
            # for arrays_jt in all_labels['jiantou']:
            #     mask = product_jiantou_masks(arrays_jt, x_threshold, y_threshold, args, mask)

            # 生成路沿
            for arrays_ly in all_labels['luyan']:
                mask = product_luyan_masks(arrays_ly, x_threshold, y_threshold, args, mask)
                # pts = product_luyan_masks(arrays_ly, x_threshold, y_threshold, args)
                # print(pts)


            # 图片保存
            mask_name = f"mask_{idx}.png"
            file_path = os.path.join(args.save_path, mask_name)
            cv2.imwrite(file_path, cv2.cvtColor(mask, cv2.COLOR_BGR2RGB))

    print("succeed!")
    print("masks save in {}".format(args.save_path))





