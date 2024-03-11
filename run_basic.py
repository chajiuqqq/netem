from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink
# from chart import *

import argparse
import utils
import os

LOG_DIR = "logs"
RESULT_DIR = "result"
conf = None
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
        self.addLink(leftSwitch, rightSwitch,
                     bw=conf['mn']['bw'],
                     loss=conf['mn']['loss'],
                     delay=conf['mn']['delay'])

class TestManager:

    def __init__(self,net,client,server) -> None:
        self.net = net
        self.c = client
        self.s = server
        pass
        
    def run_10mb_test(self):
        dir = LOG_DIR+'/init'
        create_directory(dir)
        self.s.cmd(f'./bin/qperf-go server --port=8888 --http3 --www www &> {dir}/quic_server.txt &')
        self.c.cmd(f'./bin/qperf-go client --http3 --quiet=True https://{self.s.IP()}:8888/www/10MB.jpg &> {dir}/quic_client.txt &')
        self.c.cmd('wait')
    # 基础测试，记录吞吐量、rtt、丢包率
    def run_basic(self):
        dir = LOG_DIR+'/basic'
        create_directory(dir)
        params = conf['tests']['basic']['params']

        # tcp
        self.s.cmd(f'iperf3 -s -p 5000 -i {params["report_interval"]} -V -J --logfile {dir}/tcp_server.json &')
        self.c.cmd(f'iperf3 -c {self.s.IP()} -C cubic -p 5000 -t {params["duration"]} -i 1 -J -R -P {params["n_tcp_streams"]} -V --logfile {dir}/tcp_client.json &')
        self.c.cmd('wait')

        # quic
        self.s.cmd(f'./bin/qperf-go server --port=8080 &> {dir}/quic_server.txt &')
        self.c.cmd(f'./bin/qperf-go client --log-prefix=quic --addr="{self.s.IP()}:8080" --t={params["duration"]} &> {dir}/quic_client.txt &')
        self.c.cmd('wait')

    # 公平性测试
    def run_fairness(self):
        dir = LOG_DIR+'/fairness'
        create_directory(dir)
        params = conf['tests']['fairness']['params']
        print('params:',params['duration'])

        # tcp
        self.s.cmd(f'iperf3 -s -p 5000 -i 1 -V -J --logfile {dir}/tcp_server.json &')
        self.c.cmd(f'iperf3 -c {self.s.IP()} -p 5000 -t {params["duration"]} -i 1 -J -R -P {params["n_tcp_streams"]} -V --logfile {dir}/tcp_client.json &')

        # quic
        self.s.cmd(f'./bin/qperf-go server --port=8080 &> {dir}/quic_server.txt &')
        self.c.cmd(f'./bin/qperf-go client --log-prefix=quic --addr="{self.s.IP()}:8080" --t={params["duration"]} &> {dir}/quic_client.txt &')
        self.c.cmd('wait')

    # plt测试
    def run_plt(self):
        dir = LOG_DIR+'/fairness'
        create_directory(dir)

        # 改造plt-tester，支持多个url
        # 改造qperf和http2的server，支持5kb-10mb的网页大小，支持1mb-5kb但数量不同的img测试
        # plt的画图

        filenames = [
            '5kb',
            '10kb',
            '100kb',
            '200kb',
            '1mb',
            '10mb',
        ]
        http2urls=[ f"https://{self.s.IP()}:8080/html/{x}.jpeg" for x in filenames]
        quicUrls= [ f"https://{self.s.IP()}:8888/www/{x}.jpeg" for x in filenames]

        # http2
        print('doing http2 plt testing...')
        self.s.cmd(f'''./bin/http2 --cert server.crt --key server.key &> {dir}/http2_server.txt &''')
        # for i,url in enumerate(http2urls):
        #     fname=filenames[i]
        #     print(f'doing http2 plt testing for {fname} ...')
        #     h1.cmd(f'python3 submod/pageloading-tester/src/main.py bin/chromedriver {url} plt_http2_{fname}_result.json &> {LOG_DIR}/{test_prefix}_http2_h1.txt')
        self.c.cmd(f'python3 submod/pageloading-tester/src/main.py bin/chromedriver plt_http2_result.json --urls {" ".join(http2urls)} &> {dir}/http2_client.txt')
        
        # quic
        print('doing quic plt testing...')
        self.s.cmd(f'''./bin/qperf-go server --port=8888  --http3 --www www &> {dir}/quic_server.txt &''')
        self.c.cmd(f'''./bin/qperf-go client --http3 --quiet=True {" ".join(quicUrls)} &> {dir}/quic_client.txt''')

    # dash视频流测试
    def run_dash(self):
        dir = LOG_DIR+'/dash'
        create_directory(dir)

        params = conf['tests']['dash']['params']
        maxSegNum = int(params['duration'] / params['eachSegDuration'] + 1)

        print('start h2 stream test')
        # tcp
        h2_mpd = f'https://{h4.IP()}:8080{params["mpd"]}'
        self.s.cmd(f'''./bin/http2 --cert server.crt --key server.key &> {LOG_DIR}/{params['name']}_http2_h4.txt &''')
        self.c.cmd(f'''./bin/dashquic -p {params['play_strategy']} -m {h2_mpd} -r 1 -v -n {maxSegNum} -f {dir} -h2 &> {dir}/{params['name']}_{params['play_strategy']}_http2_client.txt &''')
        self.c.cmd('wait')

        print('end h2 stream test')

        # quic
        print('start quic stream test')
        quic_mpd = f'https://{h4.IP()}:8888{params["mpd"]}'
        self.s.cmd(f'''./bin/qperf-go server --port=8888 --http3 --www www &> {LOG_DIR}/{params['name']}_quic_h4.txt &''')
        self.c.cmd(f'''./bin/dashquic -p {params['play_strategy']} -m {quic_mpd} -r 1 -v -n {maxSegNum} -f {dir} -quic &> {dir}/{params['name']}_{params['play_strategy']}_quic_client.txt &''')
        self.c.cmd('wait')
        print('end quic stream test')


def create_directory(d):
    if not os.path.exists(d):
        os.makedirs(d,mode=777) 

def run_tcp_test(net,test_prefix,duration,n_tcp_streams=1):
    h1 = net.get('h1')
    h4 = net.get('h4')

    # Set congestion control algorithm
    # h1.cmd('sysctl -w net.ipv4.tcp_congestion_control={}'.format(congestion_algorithm))

    # Perform TCP test
    h4.cmd(f'iperf3 -s -p 5000 -i 1 &> {LOG_DIR}/{test_prefix}_tcp_h4.txt &')
    pid = h1.cmd(f'iperf3 -c {h4.IP()} -p 5000 -t {duration} -i 1 --json -R -P {n_tcp_streams} &> {RESULT_DIR}/{test_prefix}_tcp_h1.json &')
    print(pid)
    return pid

    # net.iperf((h1,h4),port=8080)
def run_quic_test(net,test_prefix,duration,bom=False):
    h1 = net.get('h1')
    h4 = net.get('h4')

    if bom:
        test_prefix = f'{test_prefix}_bom'

    h4.cmd(f'./bin/qperf-go server --port=8080 &> {LOG_DIR}/{test_prefix}_quic_h4.txt &')
    pid = h1.cmd(f'./bin/qperf-go client --log-prefix {test_prefix} --addr="{h4.IP()}:8080" --t={duration} &> {LOG_DIR}/{test_prefix}_quic_h1.txt &')
    print(pid)
    return pid

def run_fairness_test(net):
    params = conf['tests']['fairness']['params']
    testname = f'fairness_{params.n_tcp_streams}_tcpStreams'

    print(f'run {testname}...')
    print('start tcp test...')
    run_tcp_test(net,testname,duration=params.duration,n_tcp_streams=params.n_tcp_streams)
    
    print('start quic test...')
    run_quic_test(net,testname,duration=params.duration)

    # print('start quic-bom test...')
    # run_quic_test(net,testname,True)
    print(net.get('h1').cmd('wait'))

def run_throughput_test(net):
    print('run_throughput...')
    # print('start tcp test...')

    # params = params = conf['tests']['throughput']['params']
    # run_tcp_test(net,'throughput',duration=params.duration)
    # print(net.get('h1').cmd('wait'))

    # print('start quic test...')
    # run_quic_test(net,'throughput',duration=params.duration)
    # print(net.get('h1').cmd('wait'))
    h1 = net.get('h1')
    h4 = net.get('h4')
    test_prefix='throughput_rl'
    h4.cmd(f'./bin/qperf-go server --port=8080 --redis 192.168.71.109:6379 --cc rl &> {LOG_DIR}/{test_prefix}_quic_h4.txt &')
    pid = h1.cmd(f'./bin/qperf-go client --log-prefix {test_prefix} --addr="{h4.IP()}:8080" --t=10 &> {LOG_DIR}/{test_prefix}_quic_h1.txt &')
    
def run_10mb_test(net):
    test_prefix = "10mb"
    h1 = net.get('h1')
    h4 = net.get('h4')
    h4.cmd(f'./bin/qperf-go server --port=8888 --http3 --www www &> {LOG_DIR}/{test_prefix}_quic_h4.txt &')
    pid = h1.cmd(f'./bin/qperf-go client --http3 --quiet=True https://{h4.IP()}:8888/www/10MB.jpg &> {LOG_DIR}/{test_prefix}_quic_h1.txt &')
    print(pid)
    h1.cmd('wait')
    return pid
def run_plt_test(net):
    # 改造plt-tester，支持多个url
    # 改造qperf和http2的server，支持5kb-10mb的网页大小，支持1mb-5kb但数量不同的img测试
    # plt的画图

    test_prefix = "plt"
    h1 = net.get('h1')
    h4 = net.get('h4')

    filenames = [
        '5kb',
        '10kb',
        '100kb',
        '200kb',
        '1mb',
        '10mb',
    ]
    http2urls=[ f"https://{h4.IP()}:8080/html/{x}.jpeg" for x in filenames]
    quicUrls= [ f"https://{h4.IP()}:8888/www/{x}.jpeg" for x in filenames]

    # http2
    print('doing http2 plt testing...')
    h4.cmd(f'''./bin/http2 
           --cert server.crt 
           --key server.key 
           &> {LOG_DIR}/{test_prefix}_http2_h4.txt &
           ''')
    # for i,url in enumerate(http2urls):
    #     fname=filenames[i]
    #     print(f'doing http2 plt testing for {fname} ...')
    #     h1.cmd(f'python3 submod/pageloading-tester/src/main.py bin/chromedriver {url} plt_http2_{fname}_result.json &> {LOG_DIR}/{test_prefix}_http2_h1.txt')
    h1.cmd(f'python3 submod/pageloading-tester/src/main.py bin/chromedriver plt_http2_result.json --urls {" ".join(http2urls)} &> {LOG_DIR}/{test_prefix}_http2_h1.txt')
    
    # quic
    print('doing quic plt testing...')
    h4.cmd(f'''./bin/qperf-go server 
           --port=8888  
           --http3 
           --www www &> {LOG_DIR}/{test_prefix}_quic_h4.txt &
           ''')
    h1.cmd(f'''./bin/qperf-go client
           --http3 
           --quiet=True {" ".join(quicUrls)} &> {LOG_DIR}/{test_prefix}_quic_h1.txt
           ''')

# 视频流测试
def run_stream_test(net):
    params = conf['tests']['video_stream']['params']
    h1 = net.get('h1')
    h4 = net.get('h4')

    maxSegNum = int(params['duration'] / params['eachSegDuration'] + 1)

    print('start h2 stream test')
    # tcp
    h2_mpd = f'https://{h4.IP()}:8080{params["mpd"]}'
    h4.cmd(f'''./bin/http2 --cert server.crt --key server.key &> {LOG_DIR}/{params['name']}_http2_h4.txt &''')
    h1.cmd(f'''./bin/dashquic -p {params['play_strategy']} -m {h2_mpd} -r 1 -v -n {maxSegNum} -f {LOG_DIR}/STREAM/h2/ -h2 &> {LOG_DIR}/{params['name']}_{params['play_strategy']}_http2_h1.txt &''')
    h1.cmd('wait')

    print('end h2 stream test')

    # quic
    print('start quic stream test')
    quic_mpd = f'https://{h4.IP()}:8888{params["mpd"]}'
    h4.cmd(f'''./bin/qperf-go server --port=8888 --http3 --www www &> {LOG_DIR}/{params['name']}_quic_h4.txt &''')
    h1.cmd(f'''./bin/dashquic -p {params['play_strategy']} -m {quic_mpd} -r 1 -v -n {maxSegNum} -f {LOG_DIR}/STREAM/quic/ -quic &> {LOG_DIR}/{params['name']}_{params['play_strategy']}_quic_h1.txt &''')
    h1.cmd('wait')
    print('end quic stream test')


topos = {'dumbbellTopo':DumbbellTopo}
 # 创建 ArgumentParser 对象
parser = argparse.ArgumentParser(description='示例程序 - 一个简单的命令行工具')

# 添加位置参数（Positional Arguments）
parser.add_argument('-t','--test', help='测试名称 fairness,basic,plt, quic-std,video')
parser.add_argument('-c','--config', help='配置文件路径',default='./conf/default.yaml')

# 添加可选参数（Optional Arguments）
# parser.add_argument('-o', '--output', help='输出文件的路径')

# # 添加标志参数（Flag Arguments）
# parser.add_argument('-v', '--verbose', action='store_true', help='启用详细输出模式')

# 解析命令行参数
args = parser.parse_args()
def init_args(args):
    print('初始化参数...')
    # 打印参数和值
    for arg in vars(args):
        print(arg,' = ', getattr(args, arg))
    if args.test == '':
        print('未指定测试名称')
        # exit 
        exit(0)
def main():
    setLogLevel('info')
    init_args(args)
    global conf
    conf = utils.read_config(args.config)
    topo = DumbbellTopo()

    net = Mininet(topo=topo, link=TCLink)
    net.start()
    
    h1,h4=net.get('h1'),net.get('h4')
    tm = TestManager(net,h1,h4)
    
    # if args.test == 'plt':
    #     run_plt_test(net)
    if args.test == 'basic':
        tm.run_basic()
        # run_throughput_test(net)
        # plot(conf['tests'][args.test]['params']['name'])
    # if args.test == 'quic_std':
    #     run_10mb_test(net)
    # if args.test == 'fairness':
    #     run_fairness_test(net)
    #     plot(conf['tests'][args.test]['params']['name'])
    # if args.test == 'video':
    #     run_stream_test(net)
    #     plot_video_stream(conf['tests']['video_stream']['params'])

    # CLI(net)
    net.stop()

if __name__ == '__main__':
    main()
