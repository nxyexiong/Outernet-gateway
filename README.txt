- change configs in main.py and uninit_tun.py
- tun_name should be your tun interface name, use anything you like, tun0 is recommended
- eth_name should be your ethernet interface name, which can be found using ifconfig. it usually is eth0
- lan_ips should be your client device's lan ip, could be something like 192.168.0.xx

if you are setting up a VPN-ed router:
- put router's lan ip in lan_ips. for example, if this code is running in a subnet 192.168.0.0/24, the router's lan ip is 192.168.0.150, then lan_ips += '192.168.0.150'. also dont forget to edit lan_ips inside uninit_tun.py
- the router should set its mtu to less than 1400

if you are setting up a raw side gateway:
- you need to manually setup client device's network by setting ip to the one you put into lan_ip, setting gateway ip to the ip where this code is running and setting dns to 1.1.1.1 or 8.8.8.8