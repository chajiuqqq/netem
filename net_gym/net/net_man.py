from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
class NetworkManager():
    def __init__(self, topo):
        self.topo = topo
        self.net = Mininet(topo=topo, link=TCLink)

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