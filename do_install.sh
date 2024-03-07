git submodule update --init --recursive

# install mininet;should installed in /root
cd /root && git clone https://github.com/mininet/mininet.git
./mininet/util/install.sh -a

# install go
rm -rf /usr/local/go && wget https://go.dev/dl/go1.20.12.linux-amd64.tar.gz && tar -C /usr/local -xzf go1.20.12.linux-amd64.tar.gz && rm go1.20.12.linux-amd64.tar.gz

# install qperf
export GOPROXY=https://goproxy.io,direct
go install golang.org/dl/go1.19@latest && go1.19 download && go1.19 build -o ../../bin/qperf
export PATH=$PATH:$PWD/bin

# install chrome
sudo apt install wget
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb
ln /usr/bin/google-chrome-stable /usr/bin/google-chrome

# run page loading time tester
# python3 submod/pageloading-tester/src/main.py bin/chromedriver https://www.baidu.com/ performance.json