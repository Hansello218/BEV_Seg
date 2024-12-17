import numpy as np
import json
import re
import os

def filename_matcher(file_name):
    match = re.match(r'.*_(BEV_\d+)_(sub_\d+)\.jpg', file_name)
    if match:
        bev_num = match.group(1)
        sub_num = match.group(2)
        return bev_num, sub_num
    return None, None

def get_coord_mean_height(height_map, center, window_size):
    rows, cols = height_map.shape
    row_center, col_center = center
    row_center = int(row_center)
    col_center = int(col_center)
    half_window = window_size // 2

    row_start = max(row_center - half_window, 0)
    row_end = min(row_center + half_window + 1, rows)
    col_start = max(col_center - half_window, 0)
    col_end = min(col_center + half_window + 1, cols)

    sub_map = height_map[row_start:row_end, col_start:col_end]
    # 筛掉0后计算均值
    sub_map = sub_map[sub_map != 0]
    if sub_map.size > 0:
        mean_height = np.mean(sub_map)
    else:
        mean_height = 0
    return float(mean_height)


def get_point_world_coord(point, absolute_coord_info, height_map=None, height_range=1):
    x, y = point
    x_left_w, y_top_w = absolute_coord_info[:2]
    pixel_size = absolute_coord_info[2]
    x_world = x_left_w + x * pixel_size
    y_world = y_top_w - y * pixel_size
    if height_map is not None:
        window_size = int(height_range // pixel_size)
        z_world = get_coord_mean_height(height_map, (y, x), window_size)
        return [x_world, y_world, z_world]
    return [x_world, y_world]


root_path = '/Users/baijiquan/Desktop/platform_test/demo'  # 根目录，可自己替换一下
segment_file = 'bev_output/segment_coord.json'  # 分割文件，一般在每包数据的 bev_output 文件夹下
image_name = '1950117_BEV_17_sub_74.jpg'  # 要处理的图片名

with open(os.path.join(root_path, segment_file)) as f:
    segment_coord = json.load(f)
crop_2k_sub_img_coord_info = segment_coord['crop_2k_sub_img_coord_info']

# 这里是根据图片名提取BEV和sub部分的内容，用于定位下面的absolute_coord_info和height文件
# 如果你的结果图片名不符合这个规则，可以自己修改一下正则表达式，反正能提取到BEV和sub部分就行
bev_part, sub_part = filename_matcher(image_name)  # 结果为('BEV_17', 'sub_74')
assert bev_part and sub_part, f'filename {image_name} does not match the pattern'

absolute_coord_info = crop_2k_sub_img_coord_info[f'{bev_part}.jpg'][f'{sub_part}.jpg']['absolute_coord_info']
roi = crop_2k_sub_img_coord_info[f'{bev_part}.jpg'][f'{sub_part}.jpg']['roi']

# 读取深度图以及提取roi部分
depth_data = np.load(os.path.join(root_path, f'bev_output/{bev_part}.depth.npz'))['depth']
depth_roi = depth_data[roi[1]:roi[3] + 1, roi[0]:roi[2] + 1]

# 调用示例
# point就是你的结果的像素坐标,是一个二维数组, [[x1, y1], [x2, y2], ...]
# height_range是计算高度的窗口大小，单位是米，即取周围多大范围的高度均值
point_w = get_point_world_coord(point, absolute_coord_info, depth_roi, height_range=1)