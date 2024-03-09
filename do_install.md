**初始化子模块**
git submodule update --init --recursive

**更新子模块**
git submodule update --remote

### install mininet

**A. install mininet;should installed in /root**
cd /root && git clone https://github.com/mininet/mininet.git
./mininet/util/install.sh -a

**B. using mininet vm**
https://mininet.org/vm-setup-notes/

**install go**
rm -rf /usr/local/go && wget https://go.dev/dl/go1.21.8.linux-amd64.tar.gz && tar -C /usr/local -xzf go1.21.8.linux-amd64.tar.gz && rm go1.21.8.linux-amd64.tar.gz

**install qperf-go**
export GOPROXY=https://goproxy.io,direct
go install golang.org/dl/go1.21@latest && go1.21 download && go1.21 build -o ../../bin/qperf
export PATH=$PATH:$PWD/bin

**install chrome**
sudo apt install wget
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb
ln /usr/bin/google-chrome-stable /usr/bin/google-chrome

**run page loading time tester**
python3 submod/pageloading-tester/src/main.py bin/chromedriver https://www.baidu.com/ performance.json