from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink
from chart import *

import argparse

log_dir = "logs"
result_dir = "result"
class DumbbellTopo(Topo):
    "Dumbbell Topology"
    def build(self): 
        leftSwitch = self.addSwitch('s1')
        rightSwitch = self.addSwitch('s2')

        leftHost1 = self.addHost('h1')
        leftHost2 = self.addHost('h2')
        rightHost1 = self.addHost('h3')
        rightHost2 = self.addHost('h4')

        self.addLink(leftHost1, leftSwitch)
        self.addLink(leftHost2, leftSwitch)
        self.addLink(rightHost1, rightSwitch)
        self.addLink(rightHost2, rightSwitch)
        self.addLink(leftSwitch, rightSwitch,bw=10)

def run_tcp_test(net,test_prefix):
    stream_num = 1
    h1 = net.get('h1')
    h4 = net.get('h4')

    # Set congestion control algorithm
    # h1.cmd('sysctl -w net.ipv4.tcp_congestion_control={}'.format(congestion_algorithm))

    # Perform TCP test
    h4.cmd(f'iperf3 -s -p 5000 -i 1 &> {log_dir}/{test_prefix}_tcp_h4.txt &')
    pid = h1.cmd(f'iperf3 -c {h4.IP()} -p 5000 -t {args.duration} -i 1 --json -R -P {stream_num} &> {result_dir}/{test_prefix}_tcp_h1.json &')
    print(pid)
    return pid

    # net.iperf((h1,h4),port=8080)
def run_quic_test(net,test_prefix):
    h1 = net.get('h1')
    h4 = net.get('h4')

    h4.cmd(f'./bin/qperf-go server --port=8080 &> {log_dir}/{test_prefix}_quic_h4.txt &')
    pid = h1.cmd(f'./bin/qperf-go client --log-prefix {test_prefix} --addr="{h4.IP()}:8080" --t={args.duration} &> {log_dir}/{test_prefix}_quic_h1.txt &')
    print(pid)
    return pid

def run_fairness_test(net):
    print('run_fairness_test...')
    print('start tcp test...')
    run_tcp_test(net,'fairness')
    
    print('start quic test...')
    run_quic_test(net,'fairness')
    print(net.get('h1').cmd('wait'))

def run_throughput_test(net):
    print('run_throughput...')
    print('start tcp test...')
    run_tcp_test(net,'throughput')
    print(net.get('h1').cmd('wait'))

    print('start quic test...')
    run_quic_test(net,'throughput')
    print(net.get('h1').cmd('wait'))

def run_10mb_test(net):
    test_prefix = "10mb"
    h1 = net.get('h1')
    h4 = net.get('h4')
    h4.cmd(f'./bin/qperf-go server --port=8888 --http3 --www www &> {log_dir}/{test_prefix}_quic_h4.txt &')
    pid = h1.cmd(f'./bin/qperf-go client --http3 --quiet=True https://{h4.IP()}:8888/10MB.jpg &> {log_dir}/{test_prefix}_quic_h1.txt &')
    print(pid)
    h1.cmd('wait')
    return pid
def run_plt_test(net):
    test_prefix = "plt"
    h1 = net.get('h1')
    h4 = net.get('h4')
    h4.cmd(f'./bin/http2 --cert server.crt --key server.key &> {log_dir}/{test_prefix}_http2_h4.txt &')
    pid = h1.cmd(f'python3 submod/pageloading-tester/src/main.py bin/chromedriver https://{h4.IP()}:8080/welcome plt_http2_result.json &> {log_dir}/{test_prefix}_http2_h1.txt &')
    print(pid)
    h1.cmd('wait')
    return pid
topos = {'dumbbellTopo':DumbbellTopo}
 # 创建 ArgumentParser 对象
parser = argparse.ArgumentParser(description='示例程序 - 一个简单的命令行工具')

# 添加位置参数（Positional Arguments）
parser.add_argument('-t','--test', help='测试名称 fairness, quic, tcp, quic-std')

# 添加位置参数（Positional Arguments）
parser.add_argument('-d','--duration',default=60, help='测试时间 s 默认60')
# 添加可选参数（Optional Arguments）
# parser.add_argument('-o', '--output', help='输出文件的路径')

# # 添加标志参数（Flag Arguments）
# parser.add_argument('-v', '--verbose', action='store_true', help='启用详细输出模式')

# 解析命令行参数
args = parser.parse_args()
def main():
    setLogLevel('info')
    
    topo = DumbbellTopo()
    net = Mininet(topo=topo, link=TCLink)
    net.start()
    if args.test == 'plt':
        run_plt_test(net)
    if args.test == 'throughput':
        run_throughput_test(net)
        plot('throughput')
    if args.test == 'quic-std':
        run_10mb_test(net)
    if args.test == 'fairness':
        run_fairness_test(net)
        plot('fairness')

    # CLI(net)
    net.stop()

if __name__ == '__main__':
    main()
