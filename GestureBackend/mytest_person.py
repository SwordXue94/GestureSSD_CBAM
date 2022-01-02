import glob

import torch
import torch.nn as nn
import torch.backends.cudnn as cudnn
from torch.autograd import Variable
from data import VOC_ROOT, VOCAnnotationTransform, VOCDetection, BaseTransform
from data import VOC_CLASSES as labelmap
import torch.utils.data as data
from ssd import build_ssd
import sys
import os
import time
import argparse
import numpy as np
import pickle
import cv2

if torch.cuda.is_available():
    torch.set_default_tensor_type('torch.cuda.FloatTensor')
else:
    torch.set_default_tensor_type('torch.FloatTensor')


class SSD:
    # 初始化检测模型和分类模型
    def __init__(self):
        # load net
        num_classes = len(labelmap) + 1  # +1 for background
        self.net = build_ssd('test', 300, num_classes)  # initialize SSD
        self.net.load_state_dict(torch.load('/ssd2/xsh/SSD_person/ssd300_VOC_10000.pth'))
        self.net.eval()
        if torch.cuda.is_available():
            self.net = self.net.cuda()
            cudnn.benchmark = True
            print('net.cuda()')
        self.transform = BaseTransform(self.net.size, (104, 117, 123))
        print('Finished loading model!')

    def detect(self, img):  # 由test.py而来，是否显示多个检测？ 目前只取一个检测
        x = torch.from_numpy(self.transform(img)[0]).permute(2, 0, 1)
        x = Variable(x.unsqueeze(0))

        if torch.cuda.is_available():
            x = x.cuda()
            print('x.cuda()')
        detections = self.net(x).data  # forward pass
        # scale each detection back up to the image
        scale = torch.Tensor([img.shape[1], img.shape[0], img.shape[1], img.shape[0]])

        pred_num = 0
        for i in range(detections.size(1)):
            j = 0
            while detections[0, i, j, 0] >= 0.6:
                score = detections[0, i, j, 0].item()
                label_name = labelmap[i - 1]
                pt = (detections[0, i, j, 1:] * scale).cpu().numpy()
                coords = (str(pt[0]), str(pt[1]), str(pt[2]), str(pt[3]))
                pred_num += 1
                j += 1
                print('coords: {}'.format(coords))
                return {'box': coords, 'result': label_name, 'score': score}

        return {'box': (0, 0, 0, 0), 'result': 'no hand'}

    # def detect_multi_results(self, img):
    #     x = torch.from_numpy(self.transform(img)[0]).permute(2, 0, 1)
    #     x = Variable(x.unsqueeze(0))
    #
    #     if torch.cuda.is_available():
    #         x = x.cuda()
    #         print('x.cuda()')
    #     detections = self.net(x).data  # forward pass
    #     # detections = y.data
    #     # scale each detection back up to the image
    #     scale = torch.Tensor([img.shape[1], img.shape[0],
    #                           img.shape[1], img.shape[0]])
    #
    #     filename = 'test1.txt'
    #     pred_num = 0
    #     for i in range(detections.size(1)):
    #         j = 0
    #         while detections[0, i, j, 0] >= 0.6:
    #             if pred_num == 0:
    #                 with open(filename, mode='a') as f:
    #                     f.write('PREDICTIONS: ' + '\n')
    #             score = detections[0, i, j, 0]
    #             label_name = labelmap[i - 1]
    #             pt = (detections[0, i, j, 1:] * scale).cpu().numpy()
    #             coords = (pt[0], pt[1], pt[2], pt[3])
    #             pred_num += 1
    #             with open(filename, mode='a') as f:
    #                 f.write(str(pred_num) + ' label: ' + label_name + ' score: ' +
    #                         str(score) + ' ' + ' || '.join(str(c) for c in coords) + '\n')
    #             j += 1


if __name__ == '__main__':
    ssd = SSD()

    def fsf(input_path, output_path):
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        files = sorted(glob.glob("%s/*.jpg" % input_path))
        for file in files:
            print(file)
            filename = file.split('.')[0].split(os.sep)[-1]
            if not os.path.exists(os.path.join(output_path, "{}.jpg".format(filename))):
                t0 = time.time()
                image = cv2.imread(file)
                t1 = time.time()
                print('time to read image: {}'.format(t1 - t0))
                result = ssd.detect(image)
                t2 = time.time()
                print('time to detect image: {}'.format(t2 - t1))
                left, top, right, bottom = result['box']
                image = image[int(float(top)): int(float(bottom)), int(float(left) - 50): int(float(right) + 50)]

                if image.size:  # 用于双手相握
                    # 保存原图
                    cv2.imwrite(os.path.join(output_path, "{}.jpg".format(filename)), image)
                    t3 = time.time()
                    print('time to write image: {}'.format(t3 - t2))


    path1 = '/ssd2/xsh/9192'
    path2 = '/ssd2/xsh/91922'

    dirs = os.listdir(path1)
    # print(dirs)
    for dir in dirs:  # common
        # sub_dirs = os.listdir(os.path.join(path1, dir))
        # # print(sub_dirs)
        # for sub_dir in sub_dirs:  # P001
        fsf(os.path.join(path1, dir), os.path.join(path2, dir))
            # sub_sub_dirs = os.listdir(os.path.join(path1, dir, sub_dir))
            # for sub_sub_dir in sub_sub_dirs:  # 最后一级
            #     print(os.path.join(path1, dir, sub_dir, sub_sub_dir))
            #     print(os.path.join(path2, dir, sub_dir, sub_sub_dir))
            #     fsf(os.path.join(path1, dir, sub_dir, sub_sub_dir), os.path.join(path2, dir, sub_dir, sub_sub_dir))

    # image_names = os.listdir('/ssd2/dataset/CSL-TJU_third_person_image')
    # for image_name in image_names:
    #     t0 = time.time()
    #     image = cv2.imread(os.path.join('/app/xsh/qwe/T0002_P006_03/T0002_P006_03', image_name))
    #     t1 = time.time()
    #     print('time to read image: {}'.format(t1 - t0))
    #     result = ssd.detect(image)
    #     t2 = time.time()
    #     print('time to detect image: {}'.format(t2 - t1))
    #     left, top, right, bottom = result['box']
    #     image = image[int(float(top)): int(float(bottom)), int(float(left) - 50): int(float(right) + 50)]
    #
    #     if image.size:
    #         cv2.imwrite(os.path.join('/app/xsh/qwe/out', "{}".format(image_name)), image)
    #     t3 = time.time()
    #     print('time to write image: {}'.format(t3 - t2))
