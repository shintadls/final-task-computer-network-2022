#!/usr/bin/python
 
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call
import time

def MyTopo():
	net = Mininet(topo=None, host=CPULimitedHost, link=TCLink)
	
	info('CLO 1\n')
	info('*** Add hosts\n' )
	
	hA = net.addHost('hA', ip = '130.67.0.1')
	hB = net.addHost('hB', ip = '130.67.6.1')
		
	info( '*** Add routers\n' )
	r1 = net.addHost('r1', ip = '130.67.0.2')
	r2 = net.addHost('r2', ip = '130.67.3.1')
	r3 = net.addHost('r3', ip = '130.67.6.2')
	r4 = net.addHost('r4', ip = '130.67.3.2')
	
	curr_buff_size = 100
		
	bw1000 = {"bw": 1, "max_queue_size" : curr_buff_size, "use_htb" : True}
	bw500 = {"bw": 0.5, "max_queue_size" : curr_buff_size, "use_htb" : True}
		
	net.addLink(hA, r1, intfName1 = 'hA-eth0', intfName2 = 'r1-eth0', cls = TCLink, **bw1000)
	net.addLink(hA, r2, intfName1 = 'hA-eth1', intfName2 = 'r2-eth1', cls = TCLink, **bw1000)
	net.addLink(hB, r3, intfName1 = 'hB-eth0', intfName2 = 'r3-eth0', cls = TCLink, **bw1000)
	net.addLink(hB, r4, intfName1 = 'hB-eth1', intfName2 = 'r4-eth1', cls = TCLink, **bw1000)
		
	net.addLink(r1, r3, intfName1 = 'r1-eth1', intfName2 = 'r3-eth1', cls = TCLink, **bw500)
	net.addLink(r1, r4, intfName1 = 'r1-eth2', intfName2 = 'r4-eth2', cls = TCLink, **bw1000)
		
	net.addLink(r2, r4, intfName1 = 'r2-eth0', intfName2 = 'r4-eth0', cls = TCLink, **bw500)
	net.addLink(r2, r3, intfName1 = 'r2-eth2', intfName2 = 'r3-eth2', cls = TCLink, **bw1000)
	
	info( '\n*** Starting network\n' )
	net.start()

	info( '*** Starting controllers\n' )
	for controller in net.controllers:
		controller.start()	
	
	net['hA'].cmd("ifconfig hA-eth0 0")
	net['hA'].cmd("ifconfig hA-eth1 0")
	net['hA'].cmd("ifconfig hA-eth0 130.67.0.1 netmask 255.255.255.0")
	net['hA'].cmd("ifconfig hA-eth1 130.67.1.1 netmask 255.255.255.0")
	
	net['hB'].cmd("ifconfig hB-eth0 0")
	net['hB'].cmd("ifconfig hB-eth1 0")
	net['hB'].cmd("ifconfig hB-eth0 130.67.6.1 netmask 255.255.255.0")
	net['hB'].cmd("ifconfig hB-eth1 130.67.7.1 netmask 255.255.255.0")
	
	net['r1'].cmd("ifconfig r1-eth0 0")
	net['r1'].cmd("ifconfig r1-eth1 0")
	net['r1'].cmd("ifconfig r1-eth2 0")
	net['r1'].cmd("ifconfig r1-eth0 130.67.0.2 netmask 255.255.255.0")
	net['r1'].cmd("ifconfig r1-eth1 130.67.2.1 netmask 255.255.255.0")
	net['r1'].cmd("ifconfig r1-eth2 130.67.5.1 netmask 255.255.255.0")
	
	net['r2'].cmd("ifconfig r2-eth0 0")
	net['r2'].cmd("ifconfig r2-eth1 0")
	net['r2'].cmd("ifconfig r2-eth2 0")
	net['r2'].cmd("ifconfig r2-eth0 130.67.3.1 netmask 255.255.255.0")
	net['r2'].cmd("ifconfig r2-eth1 130.67.1.2 netmask 255.255.255.0")
	net['r2'].cmd("ifconfig r2-eth2 130.67.4.1 netmask 255.255.255.0")
	
	net['r3'].cmd("ifconfig r3-eth0 0")
	net['r3'].cmd("ifconfig r3-eth1 0")
	net['r3'].cmd("ifconfig r3-eth2 0")
	net['r3'].cmd("ifconfig r3-eth0 130.67.6.2 netmask 255.255.255.0")
	net['r3'].cmd("ifconfig r3-eth1 130.67.2.2 netmask 255.255.255.0")
	net['r3'].cmd("ifconfig r3-eth2 130.67.4.2 netmask 255.255.255.0")
	
	net['r4'].cmd("ifconfig r4-eth0 0")
	net['r4'].cmd("ifconfig r4-eth1 0")
	net['r4'].cmd("ifconfig r4-eth2 0")
	net['r4'].cmd("ifconfig r4-eth0 130.67.3.2 netmask 255.255.255.0")
	net['r4'].cmd("ifconfig r4-eth1 130.67.7.2 netmask 255.255.255.0")
	net['r4'].cmd("ifconfig r4-eth2 130.67.5.2 netmask 255.255.255.0")
	
	#config router into 1
	net['r1'].cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")
	net['r2'].cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")
	net['r3'].cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")
	net['r4'].cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")
	
	#static routing host
	net['hA'].cmd("ip rule add from 192.168.0.1 table 1")
	net['hA'].cmd("ip rule add from 192.168.1.1 table 2")
	net['hA'].cmd("ip route add 130.67.0.0/24 dev hA-eth0 scope link table 1")
	net['hA'].cmd("ip route add default via 130.67.0.2 dev hA-eth0 table 1")
	net['hA'].cmd("ip route add 130.67.1.0/24 dev hA-eth1 scope link table 2")
	net['hA'].cmd("ip route add default via 130.67.1.2 dev hA-eth1 table 2")
	net['hA'].cmd("ip route add default scope global nexthop via 130.67.0.2 dev hA-eth0")
	
	net['hB'].cmd("ip rule add from 130.67.6.1 table 1")
	net['hB'].cmd("ip rule add from 130.67.7.1 table 2")
	net['hB'].cmd("ip route add 130.67.6.0/24 dev hB-eth0 scope link table 1")
	net['hB'].cmd("ip route add default via 130.67.6.2 dev hB-eth0 table 1")
	net['hB'].cmd("ip route add 130.67.7.0/24 dev hB-eth1 scope link table 2")
	net['hB'].cmd("ip route add default via 130.67.7.2 dev hB-eth1 table 2")
	net['hB'].cmd("ip route add default scope global nexthop via 130.67.6.2 dev hB-eth0")
	
	#static routing router
	net['r1'].cmd("route add -net 130.67.3.0/24 gw 130.67.5.2")
	net['r1'].cmd("route add -net 130.67.1.0/24 gw 130.67.5.2")
	net['r1'].cmd("route add -net 130.67.4.0/24 gw 130.67.2.2")
	net['r1'].cmd("route add -net 130.67.6.0/24 gw 130.67.2.2")
	net['r1'].cmd("route add -net 130.67.7.0/24 gw 130.67.5.2")
	
	net['r2'].cmd("route add -net 130.67.0.0/24 gw 130.67.3.2")
	net['r2'].cmd("route add -net 130.67.6.0/24 gw 130.67.4.2")
	net['r2'].cmd("route add -net 130.67.7.0/24 gw 130.67.3.2")
	net['r2'].cmd("route add -net 130.67.2.0/24 gw 130.67.4.2")
	net['r2'].cmd("route add -net 130.67.5.0/24 gw 130.67.3.2")
	
	net['r3'].cmd("route add -net 130.67.7.0/24 gw 130.67.4.1")
	net['r3'].cmd("route add -net 130.67.5.0/24 gw 130.67.2.1")
	net['r3'].cmd("route add -net 130.67.0.0/24 gw 130.67.2.1")
	net['r3'].cmd("route add -net 130.67.1.0/24 gw 130.67.4.1")
	net['r3'].cmd("route add -net 130.67.3.0/24 gw 130.67.4.1")
	
	net['r4'].cmd("route add -net 130.67.2.0/24 gw 130.67.5.1")
	net['r4'].cmd("route add -net 130.67.0.0/24 gw 130.67.5.1")
	net['r4'].cmd("route add -net 130.67.1.0/24 gw 130.67.3.1")
	net['r4'].cmd("route add -net 130.67.6.0/24 gw 130.67.5.1")
	net['r4'].cmd("route add -net 130.67.4.0/24 gw 130.67.3.1")
	
	info('CLO 2\n')
	net.pingAll()
	
	info("CLO 3\n")
	info("*** measuring network performance")
	net['hA'].cmd("iperf -s &") # to claim hA as a server
	net['hB'].cmd("tcpdump -w result.pcap -c 100 &") 
	net['hB'].cmd("iperf -c 130.67.0.1 &") 
	time.sleep(15)
	
	net['hA'].cmdPrint("fg") # to 
	net['hB'].cmdPrint("fg") 
	
	info("CLO 4\n")
	net['hA'].cmd("iperf -s &") #as a server
	net['hB'].cmd("iperf -c 130.67.0.1 &") #as a client
	time.sleep(15)
	
	net['hB'].cmdPrint("fg")
	
	CLI(net)
	net.stop()
	
if __name__=='__main__':
	setLogLevel('info')
	MyTopo()
