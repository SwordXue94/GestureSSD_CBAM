import cv2 as cv
import numpy as np
import os
import cv2


def blur_demo(image):  # 均值模糊  去随机噪声有很好的去燥效果
    dst = cv.blur(image, (1, 15))  # （1, 15）是垂直方向模糊，（15， 1）还水平方向模糊


def median_blur_demo(image):  # 中值模糊  对椒盐噪声有很好的去燥效果
    dst = cv.medianBlur(image, 5)


def custom_blur_demo(image):  # 用户自定义模糊
    kernel = np.ones([5, 5], np.float32) / 25  # 除以25是防止数值溢出
    dst = cv.filter2D(image, -1, kernel)


src = '/ssd2/xsh/T0001_P008_06'
src2 = '/ssd2/xsh/T0001_P008_06_out'
if not os.path.exists(src2):
    os.mkdir(src2)

dirs = os.listdir(src)
for dir in dirs:  # common
    # sub_dirs = os.listdir(os.path.join(path1, dir))
    # # print(sub_dirs)
    # for sub_dir in sub_dirs:  # P001
    image = cv2.imread(os.path.join(src, dir))
    image = cv.blur(image, (1, 15))
    cv2.imwrite(os.path.join(src2, dir), image)
