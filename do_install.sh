git submodule update --init --recursive

# install mininet
PWD=$(pwd)
cd submod/mininet/util 
sh ./install.sh
# install go
rm -rf /usr/local/go && wget https://go.dev/dl/go1.20.12.linux-amd64.tar.gz && tar -C /usr/local -xzf go1.20.12.linux-amd64.tar.gz && rm go1.20.12.linux-amd64.tar.gz



# install qperf
export GOPROXY=https://goproxy.io,direct
go install golang.org/dl/go1.19@latest && go1.19 download && go1.19 build -o ../../bin/qperf
export PATH=$PATH:$PWD/bin