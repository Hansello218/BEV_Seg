from skimage.draw import polygon
import numpy as np
img = np.zeros((10, 10), dtype=np.uint8)
r = np.array([-1, 2, 8])
c = np.array([1, 7, 4])
rr, cc = polygon(r, c)
img[rr, cc] = 1
print(img)
print(rr)
print(cc)