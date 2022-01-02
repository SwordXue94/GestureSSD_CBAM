import cv2
import numpy as np
import os


# 椭圆模型
def ellipse_detect(image):
    img = cv2.imread(image, cv2.IMREAD_COLOR)
    skinCrCbHist = np.zeros((256, 256), dtype=np.uint8)
    # 画椭圆 中心点 长轴短轴 旋转角度 起始角度 终止角度 边界线颜色 边界线粗细-1:以边界线颜色填充
    # cv2.ellipse(skinCrCbHist, (113, 155), (23, 15), 43, 0, 360, (255, 255, 255), -1)
    cv2.ellipse(skinCrCbHist, (113, 155), (55, 45), 43, 0, 360, (255, 255, 255), -1)

    # 转换到YCRCB空间
    YCRCB = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)
    (y, cr, cb) = cv2.split(YCRCB)
    skin = np.zeros(cr.shape, dtype=np.uint8)
    (x, y) = cr.shape
    for i in range(0, x):
        for j in range(0, y):
            CR = YCRCB[i, j, 1]
            CB = YCRCB[i, j, 2]
            if skinCrCbHist[CR, CB] > 0:
                skin[i, j] = 255
    # cv2.namedWindow(image, cv2.WINDOW_NORMAL)
    # cv2.imshow(image, img)
    dst = cv2.bitwise_and(img, img, mask=skin)
    # cv2.namedWindow("cutout", cv2.WINDOW_NORMAL)
    # cv2.imshow("cutout", dst)
    # cv2.waitKey()
    return dst


# YCrCb颜色空间的Cr分量+Otsu阈值分割
def cr_otsu(image):
    img = cv2.imread(image, cv2.IMREAD_COLOR)
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)

    (y, cr, cb) = cv2.split(ycrcb)
    cr1 = cv2.GaussianBlur(cr, (5, 5), 0)
    _, skin = cv2.threshold(cr1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    cv2.namedWindow("image raw", cv2.WINDOW_NORMAL)
    cv2.imshow("image raw", img)
    cv2.namedWindow("image CR", cv2.WINDOW_NORMAL)
    cv2.imshow("image CR", cr1)
    cv2.namedWindow("Skin Cr+OTSU", cv2.WINDOW_NORMAL)
    cv2.imshow("Skin Cr+OTSU", skin)

    dst = cv2.bitwise_and(img, img, mask=skin)
    cv2.namedWindow("seperate", cv2.WINDOW_NORMAL)
    cv2.imshow("seperate", dst)
    cv2.waitKey()


src = '/ssd1/dataset/egohands_data/_LABELLED_SAMPLES'
src2 = '/ssd1/dataset/egohands_data/mask'

if not os.path.exists(src2):
    os.mkdir(src2)

# ellipse_detect('00018.jpg')
# cr_otsu('00018.jpg')

dirs = os.listdir(src)
for dir in dirs:
    sub_dirs = os.listdir(os.path.join(src, dir))
    if not os.path.exists(os.path.join(src2, dir)):
        os.makedirs(os.path.join(src2, dir))
    for sub_dir in sub_dirs:
        filet = os.path.join(src2, dir, sub_dir).split('.')
        if filet[1] == 'jpg':
            output = ellipse_detect(os.path.join(src, dir, sub_dir))
            cv2.imwrite(os.path.join(src2, dir, sub_dir), output)
        print(os.path.join(src2, dir, sub_dir))
