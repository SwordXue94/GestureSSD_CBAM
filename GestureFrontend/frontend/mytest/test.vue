<template>
<div>
    <div class="camera_outer">
        <video id="videoCamera" :width="videoWidth" :height="videoHeight" autoplay></video>
        <canvas style="display:none;" id="canvasCamera" :width="videoWidth" :height="videoHeight"></canvas>
        <!-- <div v-if="imgSrc" class="img_bg_camera"> -->
          <!-- <p>效果预览</p> -->
          <!-- <img :src="imgSrc" alt class="tx_img" /> -->
        <!-- </div> -->
    </div>
    <div class="button" style="margin-top:30px">
      <el-button @click="startCamera()" name='openCamera'>打开摄像头</el-button>
      <el-button @click="stopNavigator()">关闭摄像头</el-button>
      <el-button @click="startSetImage()">开始</el-button>
      <el-button @click="stopImage()">停止</el-button>
    </div>
    <div class="result">
      <p id="gestureType"></p>
    </div>
</div>
</template>


<script>

const cv = require('opencv')
async function startCamera() {
    let video = document.getElementById("videoCamera");
    let stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: {
                    exact: videoWidth
                },
                height: {
                    exact: videoHeight
                }
            },
            audio: false
        })
    video.srcObject = stream;
    video.play();
}

// 创建VideoCapture
let cap = new cv.VideoCapture(video);
// 创建存放图像的Mat
let src = new cv.Mat(videoHeight, videoWidth, cv.CV_8UC4);
// 读一帧图像
cap.read(src);




</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
