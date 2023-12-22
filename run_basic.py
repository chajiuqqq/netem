from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink
from chart import plot

duration = 60   
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
    result_dir = "result"
    stream_num = 1
    h1 = net.get('h1')
    h4 = net.get('h4')

    # Set congestion control algorithm
    # h1.cmd('sysctl -w net.ipv4.tcp_congestion_control={}'.format(congestion_algorithm))

    # Perform TCP test
    h4.cmd(f'iperf3 -s -p 5000 -i 1 &> {result_dir}/{test_prefix}_tcp_h4.txt &')
    pid = h1.cmd(f'iperf3 -c {h4.IP()} -p 5000 -t {duration} -i 1 --json -R -P {stream_num} &> {result_dir}/{test_prefix}_tcp_h1.txt &')
    print(pid)

    # net.iperf((h1,h4),port=8080)
def run_quic_test(net,test_prefix):
    result_dir = "result"
    h1 = net.get('h1')
    h4 = net.get('h4')

    h4.cmd(f'./bin/qperf server --port=8080 &> {result_dir}/{test_prefix}_quic_h4.txt &')
    pid = h1.cmd(f'./bin/qperf client --addr="{h4.IP()}:8080" --t={duration} &> {result_dir}/{test_prefix}_quic_h1.txt &')
    print(pid)

def run_fairness_test(net):
    print('run_fairness_test...')
    print('start tcp test...')
    run_tcp_test(net,'fairness')
    
    print('start quic test...')
    run_quic_test(net,'fairness')
    print(net.get('h1').cmd('wait'))

topos = {'dumbbellTopo':DumbbellTopo}
def main():
    setLogLevel('info')
    
    topo = DumbbellTopo()
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    # Run TCP tests with different congestion control algorithms
    # run_tcp_test(net, "cubic")
    # run_tcp_test(net, "reno")

    # run_fairness_test(net)
    run_tcp_test(net,'fairness')
    print(net.get('h1').cmd('wait'))
    plot('fairness')

    # CLI(net)
    net.stop()

if __name__ == '__main__':
    main()
