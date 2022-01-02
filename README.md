# GestureSSD_CBAM
A gesture recognition web system based on SSD and CBAM, using pytorch, flask and node.js

SSD implementation is based on https://github.com/amdegroot/ssd.pytorch

![demo gif](https://github.com/SwordXue94/GestureSSD_CBAM/blob/main/demo.gif?raw=true)

======================================================

environment：

  python3.6 
  
  frontend：
  
    node.js v10.16.3 + vue.js
    
  backend：
  
    pytorch1.4 
    
    flask 1.1.2
    
    (you can copy my environment by pytorch1_4.yaml)
    
======================================================

pay attention:

1.change your own url at GestureFrontend/frontend/config/index.js line 17 & 27

2.link for trained models: https://pan.baidu.com/s/160gPWagDYmNngFXB4HCVuQ pwd:imhj , please download the pths to ./GestureBackend/models

  ssd.pth: original SSD
  
  ssd_x.pth: SSD + CBAM
  
  ssd_x2.pth(default): SSD + CBAM + feature fusion
  
======================================================

run:

backend: python main.py

frontend: npm run dev (in dir 'frontend')

frontend default url: http://localhost:8080
