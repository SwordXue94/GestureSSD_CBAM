import torch
import torch.nn as nn
import torch.backends.cudnn as cudnn
from torch.autograd import Variable
from data import VOC_ROOT, VOCAnnotationTransform, VOCDetection, BaseTransform
from data import VOC_CLASSES as labelmap
import torch.utils.data as data
from ssd_x2 import build_ssd
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
        num_classes = len(labelmap) + 1                      # +1 for background
        self.net = build_ssd('test', 300, num_classes)            # initialize SSD
        # self.net.load_state_dict(torch.load('/ssd2/xsh/SSD_Models/VOC.pth'))
        self.net.load_state_dict(torch.load('models/ssd_x2.pth'))
        # self.net.load_state_dict(torch.load('/ssd2/xsh/over/ssd_x2.pth'))
        self.net.eval()
        if torch.cuda.is_available():
            self.net = self.net.cuda()
            cudnn.benchmark = True
            print('net.cuda()')
        self.transform = BaseTransform(self.net.size, (104, 117, 123))
        print('Finished loading model!')

    def detect(self, img):  # 目前只取一个检测
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


# if __name__ == '__main__':
#     ssd = SSD()
#     image = cv2.imread('/ssd2/xsh/gesture_dataset/VOC_gesture/JPEGImages/3_1_00001.jpg')
#     ssd.detect(image)