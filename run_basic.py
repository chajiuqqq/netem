from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink

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

def run_tcp_test(net, congestion_algorithm):
    result_dir = "result"
    # net.pingAll()
    
    h1 = net.get('h1')
    h4 = net.get('h4')

    # Set congestion control algorithm
    h1.cmd('sysctl -w net.ipv4.tcp_congestion_control={}'.format(congestion_algorithm))

    # Perform TCP test
    h4.cmd('iperf -s &> {}/h4_{}_result.txt &'.format(result_dir, congestion_algorithm))
    result = h1.cmd('iperf -c {} &> {}/h1_{}_result.txt'.format(h4.IP(), result_dir, congestion_algorithm))
    print(result)

    # net.iperf((h1,h4),port=8080)

topos = {'dumbbellTopo':DumbbellTopo}
def main():
    setLogLevel('info')
    
    topo = DumbbellTopo()
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    # Run TCP tests with different congestion control algorithms
    run_tcp_test(net, "cubic")
    run_tcp_test(net, "reno")

    # CLI(net)
    net.stop()

if __name__ == '__main__':
    main()
