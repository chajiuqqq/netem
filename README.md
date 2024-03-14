# A net emulation platform for QUIC testing

RL part repo: https://github.com/chajiuqqq/netem_rl
# Install
**1. 初始化子模块**
```
git submodule update --init --recursive
```
**更新子模块**
```
git submodule update --remote
```
**2. install mininet**

本地安装或直接用虚拟机

A. install mininet;should installed in /root
```
cd /root && git clone https://github.com/mininet/mininet.git
./mininet/util/install.sh -a
```
B. using mininet vm

https://mininet.org/vm-setup-notes/

**3. install go**
```
rm -rf /usr/local/go && wget https://go.dev/dl/go1.21.8.linux-amd64.tar.gz && tar -C /usr/local -xzf go1.21.8.linux-amd64.tar.gz && rm go1.21.8.linux-amd64.tar.gz
```
**4. install qperf-go**
```
export GOPROXY=https://goproxy.io,direct
go install golang.org/dl/go1.21@latest && go1.21 download && go1.21 build -o ../../bin/qperf
export PATH=$PATH:$PWD/bin
```

**5. install chrome**
```
sudo apt install wget
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb
ln /usr/bin/google-chrome-stable /usr/bin/google-chrome
```
**6. install python env**
```
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**7. install iperf3**
```
apt update && apt install iperf3
```

# Usage

## H2+TCP

**web server**

使用./www作为静态文件目录。端口8080

```
./bin/http2 --cert server.crt --key server.key 
```
**basic**
```
# server
iperf3 -s -p 5000 -i 0.5 -V -J --logfile logs/tcp_server.json &
# client
iperf3 -c 127.0.0.1 -C cubic -p 5000 -t 0.5 -i 1 -J -R -P 1 -V --logfile logs/tcp_client.json &
   ```     

**run page loading time tester**
```
python3 submod/pageloading-tester/src/main.py bin/chromedriver https://www.xxx.com/ performance.json
```

## QUIC

**basic**

```
./bin/qperf-go server --port=8080 
./bin/qperf-go client --log-prefix basic --addr="127.0.0.1:8080" --t={duration} 
```

**http3 plt test**

启动http3:
```
./bin/qperf-go server --port=8888 --http3 --www www 
```

加载客户端请求：
```
./bin/qperf-go client --http3 --quiet=True  https://xxx.xxx/xx https://xxx.xxx/xx
```

## 视频流

**bento4 tool**
```
wget https://www.bok.net/Bento4/binaries/Bento4-SDK-1-6-0-641.x86_64-unknown-linux.zip
unzip Bento4-SDK-1-6-0-641.x86_64-unknown-linux.zip
```

### DASH测试文件准备

**1. 分段mp4**

只是在mp4文件中添加分割标记。必须是分割后的视频才能制作为dash。
```
./mp4fragment 源文件 生成的文件
./mp4fragment /root/poj/netem/www/video/dance_360.mp4 /root/poj/netem/www/video/dance_360f.mp4 
```

**2. 制作dash分片视频和mpd文件**
```
./mp4dash -o 输出目录 输入的文件1 输入的文件2
./mp4dash -o /root/poj/netem/www/video/dance /root/poj/netem/www/video/dance_720f.mp4 /root/poj/netem/www/video/dance_360f.mp4
```
### DASH请求
准备mpd文件http url的路径

**QUIC**

```
# server
./bin/qperf-go server --port=8888 --http3 --www www &> {dir}quic_server.txt &
# client
./bin/dashquic -p {play_strategy} -m {quic_mpd} -r 1 -v -n {maxSegNum} -f {dir} -quic &> {dir}{play_strategy}_quic_client.txt &
```

**tcp**
```
# server
./bin/qperf-go server --port=8888 --http3 --www www &> {dir}quic_server.txt &
# client
./bin/dashquic -p {play_strategy} -m {quic_mpd} -r 1 -v -n {maxSegNum} -f {dir} -h2 &> {dir}{play_strategy}_quic_client.txt &
```

