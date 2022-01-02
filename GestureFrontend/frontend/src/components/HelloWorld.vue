<template>
<div>
    <div class="camera_outer">
        <video id="gestureCamera" style="z-index:-1; position:absolute; left:0px; top:0px" :width="videoWidth" :height="videoHeight" autoplay></video>
        <canvas id="canvasCamera" style="display: None" :width="videoWidth" :height="videoHeight"></canvas>
        <canvas id="mycanvas" style="position:absolute; left:0px; top:0px" :width="videoWidth" :height="videoHeight"></canvas>
    </div>

    <div class="button" style="position: absolute; left:1340px; top: 150px">
      <el-button @click="openCamera()" name='openCamera'>打开摄像头</el-button>
    </div>

    <div class="button" style="position: absolute; left:1340px; top: 230px">
      <el-button @click="stopCamera()">关闭摄像头</el-button>
    </div>
    
    <div class="button" style="position: absolute; left:1350px; top: 310px">
      <el-button @click="startUpload()">开始检测</el-button>
    </div>

    <div class="button" style="position: absolute; left:1350px; top: 390px">
      <el-button @click="stopUpload()">停止检测</el-button>
    </div>

    <div class="result" style="position: absolute; left: 1350px; top: 470px">
      <p id="realTime" style=""></p>
    </div>

    <div class="result" style="position: absolute; left: 1340px; top: 470px">
      <p id="gestureType" style=""></p>
    </div>   
</div>

</template>
<script>
// import axios from 'axios'

var stopFlag = false;

export default {
  name:'HelloWorld',
  data() {
    return {
      videoWidth: 1280,
      videoHeight: 720,
      imgSrc: "",
      thisCanvas: null,
      thisContext: null,
      thisVideo: null,
      openVideo:false
    };
  },
  mounted(){
    //this.openCamera()//进入页面就调用摄像头
  },
  methods: {
    // 开启摄像头
    openCamera() {
      var _this = this;
      _this.thisCanvas = document.getElementById("canvasCamera");
      _this.thisContext = this.thisCanvas.getContext("2d");
      _this.thisVideo = document.getElementById("gestureCamera");
      _this.thisVideo.style.display = 'block';
      if (navigator.mediaDevices === undefined) {
        navigator.mediaDevices = {};
      }
      if (navigator.mediaDevices.getUserMedia === undefined) {
        navigator.mediaDevices.getUserMedia = function(constraints) {
          var getUserMedia =
            navigator.webkitGetUserMedia ||
            navigator.mozGetUserMedia ||
            navigator.getUserMedia;
          if (!getUserMedia) {//不存在则报错
            return Promise.reject(
              new Error("getUserMedia is not implemented in this browser")
            );
          }
          return new Promise(function(resolve, reject) {
            getUserMedia.call(navigator, constraints, resolve, reject);
          });
        };
      }
      var constraints = {
        audio: false,
        video: {
          width: this.videoWidth,
          height: this.videoHeight,
          transform: "scaleX(-1)"
        }
      };
      navigator.mediaDevices
        .getUserMedia(constraints)
        .then(function(stream) {
          if ("srcObject" in _this.thisVideo) {
            _this.thisVideo.srcObject = stream;
          } else { 
            _this.thisVideo.src = window.URL.createObjectURL(stream);
          }
          _this.thisVideo.onloadedmetadata = function(e) { // onloadedmetadata 事件为video加载后触发的事件
            _this.thisVideo.play();
          };
        })
        .catch(err => {
          console.log(err);
        });
    },
    // 上传二进制文件
    async uploadFile(blob) {
      const formData = new FormData();
      formData.append("image", blob);
      
      const res = await this.$axios({
        method: "post",
        url: "/apis/hello",
        data: formData,
        headers: {
          "Content-Type": "multipart/form-data",
          "charset":"UTF-8"
        }
      });
      var result = res.data;
      if(result.result=='6'){
        result.result = 'y'
      }
      else if(result.result=='8'){
        result.result = 'l'
      }
      else if(result.result=='q'){
        result.result = '相握'
      }
      else if(result.result=='5'){
        result.result = '双5'
      }
      else if(result.result=='7'){
        result.result = '双7'
      }
      else if(result.result=='9'){
        result.result = '双9'
      }
      return result;
    },
    // 结果展示（画预测框+类别）
    displayResult(result, time){
      let ltx = result.box[0], lty = result.box[1], rdx = result.box[2], rdy = result.box[3];
      document.getElementById('realTime').innerText = time;
      document.getElementById('gestureType').innerText = result.result;
      // 在canvas上画手框
      let mycanvas = document.getElementById('mycanvas');
      mycanvas.height = mycanvas.height //重设长宽可以清屏
      let context = mycanvas.getContext('2d');
      // 边框颜色和宽窄
      context.lineWidth = 8;
      context.strokeStyle = "red"; 
      // 画边框
      context.strokeRect(ltx, lty, rdx - ltx, rdy - lty)
    },
    // 拍照（获取数据）
    getImage(){
      var _this = this;
      // 获取图片
      _this.thisContext.drawImage(
        _this.thisVideo,
        0,
        0,
        _this.videoWidth,
        _this.videoHeight
      );
      // 转base64
      var image = this.thisCanvas.toDataURL("image/png");
      return image
    },
    // 整个流程：拍照并上传，接收结果（类别，框）并显示
	  async uploadImage() {
      var _this = this;
      // 获取当前时间
      var now = new Date();
      var hour = now.getHours();
      var minu = now.getMinutes();
      var sec = now.getSeconds();
　    var MS = now.getMilliseconds();
      if (hour < 10) hour = "0" + hour;
      if (minu < 10) minu = "0" + minu;
      if (sec < 10) sec = "0" + sec;
      if (MS < 100) MS = "0" + MS;
      var time = hour + ':' + minu + ':' + sec + ':' + MS;
      // 获取图片
      let image = _this.getImage()
      // 发送、接收结果
      let blob = _this.dataURLtoBlob(image);
      let result = await _this.uploadFile(blob);
      // 展示结果
      this.displayResult(result, time)
    },
    // 定义sleep方法
    sleep(time) {
      return new Promise((resolve) => setTimeout(resolve, time));
    },
    // 定时调用uploadImage()
    async startUpload(){
      stopFlag = false;
      var _this = this;
      while(stopFlag == false){
        await _this.sleep(100);
        await _this.uploadImage();
      }
    },
    // 停止uploadImage() 利用flag
    stopUpload(){
      stopFlag = true
    },
    // 关闭摄像头
    stopCamera() {
      this.thisVideo.srcObject.getTracks()[0].stop();
    },
    // base64转文件
    dataURLtoBlob: function(dataurl) {
      var arr = dataurl.split(",");
      var mime = arr[0].match(/:(.*?);/)[1];
      var bstr = atob(arr[1]);
      var n = bstr.length;
      var u8arr = new Uint8Array(n);
      while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
      }
      let imgFile = new Blob([u8arr], {
        type: mime
      });
      return imgFile;    
    },
  }
};
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
#gestureType {
  font-size: 80px;
  font-weight: bold;
}
</style>
