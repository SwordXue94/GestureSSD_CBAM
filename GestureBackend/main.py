import base64
import os
import cv2
import PIL.Image as Image
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from mytest import SSD
import time
'''
    for pytorch1.4
'''


def create_app(test_config=None):
    # create and configure the app
    # os.environ['CUDA_VISIBLE_DEVICES'] = '3'
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    ssd = SSD()

    # 处理网页端
    @app.route('/hello', methods=['post'])
    def hello():
        t0 = time.time()
        # 把POST请求中的数据取出来
        a = request.files.get('image')
        filestr = a.read()

        # 从网络传输中解码图像
        img = cv2.imdecode(np.frombuffer(filestr, np.uint8), cv2.IMREAD_COLOR)

        t1 = time.time()
        print('time to get and decode image: {}'.format(t1 - t0))

        # 对图片进行手势识别
        result = ssd.detect(img)

        print('result: {}'.format(result))
        print('\n')
        t2 = time.time()
        print('time for gesture recognition: {}'.format(t2 - t1))
        # 结果返回给前端
        return jsonify(result)
    return app

    # android端 base64字符串
    # @app.route('/hello', methods=['post'])
    # def hello():
    #     t0 = time.time()
    #     # 把POST请求中的数据取出来
    #     a = request.get_data()
    #     # 解码
    #     img = base64.b64decode(a)
    #     img = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_COLOR)
    #
    #     t1 = time.time()
    #     print('time to get and decode image: {}'.format(t1 - t0))
    #     # 对图片进行手势识别
    #     result = ssd.detect(img)
    #     left, top, right, bottom = result['box']
    #
    #     result = {'left': left, 'top': top,
    #               'right': right, 'bottom': bottom,
    #               'result': result['result']}
    #
    #     print('result: {}'.format(result))
    #     print('\n')
    #     # 结果返回给前端
    #     return jsonify(result)
    # return app


app = create_app()
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8088,
        debug=True
    )
