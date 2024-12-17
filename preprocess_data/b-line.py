import numpy as np
import cv2
from scipy.interpolate import splprep, splev
import matplotlib.pyplot as plt

# 读取图像并转换为灰度图
image = cv2.imread(r'D:\python_projects\workplace\bytetree\SegFormer\tools\preprocess_data\image1', cv2.IMREAD_GRAYSCALE)

# 找到白色曲线的轮廓
contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 提取第一个轮廓
if contours:
    points = contours[0][:, 0, :]  # 获取轮廓点
else:
    raise ValueError("没有找到轮廓")

# 使用 B 样条拟合
tck, u = splprep(points.T, s=1.0)  # s 为平滑因子
unew = np.linspace(0, 1, num=100)  # 生成 100 个均匀的参数
out = splev(unew, tck)  # 计算 B 样条拟合的点

# 可视化
plt.figure(figsize=(8, 6))
plt.plot(points[:, 0], points[:, 1], 'ro', label='原始点')
plt.plot(out[0], out[1], 'b-', label='B样条拟合曲线')
plt.title('B样条曲线拟合')
plt.xlabel('X轴')
plt.ylabel('Y轴')
plt.legend()
plt.grid()
plt.axis('equal')
plt.show()
