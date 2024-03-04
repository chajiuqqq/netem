import subprocess
import os
import logging
from mininet.util import pmonitor

log = logging.getLogger(__name__)

FILE_DIR = os.path.dirname(os.path.abspath(__file__))

class BandwidthCollector:
    def __init__(self, net,iface_list, shared_stats,stats_dict):
        self.iface_list = iface_list
        self.name = "StatsCollector"
        self.stats = shared_stats
        self.stats_dict = stats_dict
        self.net = net
    def _get_bandwidths(self, iface_list):
        popens = {}
        for iface in iface_list:
            host = self.net.get(iface.split('_')[0]) # h1-eth0
            popens[ host ] = host.popen( " ifstat -i %s -b -q 0.5 1 | awk \'{if (NR==3) print $0}\' | \
                   awk \'{$1=$1}1\' OFS=\", \"" % (iface))
           
        # Monitor them and print output
        for host, line in pmonitor( popens ):
            if host:
                bw = line.split(', ')
                if bw[0] != 'n/a' and bw[1] != ' n/a\n':
                    bps_rx = float(bw[0]) * 1000.0 / float(self.max_bps)
                    bps_tx = float(bw[1]) * 1000.0 / float(self.max_bps)
                    self.stats[self.stats_dict["bw_rx"]] = bps_rx
                    self.stats[self.stats_dict["bw_tx"]] = bps_tx


    def collect(self):
        self._get_bandwidths(self.iface_list)
