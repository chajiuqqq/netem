# h2+tcp

使用./www作为静态文件目录。端口8080

```
./bin/http2 --cert server.crt --key server.key 
```

# QUIC

启动http3:
```
./bin/qperf-go server --port=8888 --http3 --www www 
```

加载客户端请求：
```
./bin/qperf-go client --http3 --quiet=True  https://xxx.xxx/xx https://xxx.xxx/xx
```

# 视频流

## 分段mp4

只是在mp4文件中添加分割标记。必须是分割后的视频才能制作为dash。
```
./mp4fragment 源文件 生成的文件
./mp4fragment /root/poj/netem/www/video/dance_360.mp4 /root/poj/netem/www/video/dance_360f.mp4 
```

## 制作dash分片视频和mpd文件
```
./mp4dash -o 输出目录 输入的文件1 输入的文件2
./mp4dash -o /root/poj/netem/www/video/dance /root/poj/netem/www/video/dance_720f.mp4 /root/poj/netem/www/video/dance_360f.mp4
```