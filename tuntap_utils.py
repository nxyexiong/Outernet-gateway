import os


def init_tun(eth_name, tun_name, lan_ips, tun_ip, dst_ip):
    os.system("ip tuntap add dev %s mode tun" % (tun_name,))
    os.system("ifconfig %s %s dstaddr %s up" % (tun_name, tun_ip, dst_ip))
    
    os.system("echo 100 outernet >> /etc/iproute2/rt_tables")
    os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")
    
    for ip in lan_ips:
        os.system("ip rule add from %s/32 table outernet" % (ip,))
        
    os.system("ip route add default via %s dev %s table outernet" % (dst_ip, tun_name))
    os.system("ip route flush cache")
    
    os.system("iptables -t nat -A POSTROUTING -o %s -j MASQUERADE" % (tun_name,))
    os.system("iptables -A FORWARD -i %s -o %s -j ACCEPT" % (eth_name, tun_name))
    os.system("iptables -A FORWARD -i %s -o %s -m state --state RELATED,ESTABLISHED -j ACCEPT" % (tun_name, eth_name))


def uninit_tun(tun_name, lan_ips):
    os.system("ip link delete %s" % (tun_name,))
    
    os.system("sed -i '/outernet/d' /etc/iproute2/rt_tables")
    os.system("echo 0 > /proc/sys/net/ipv4/ip_forward")
    
    for ip in lan_ips:
        os.system("ip route del table outernet %s/32" % (ip,))
    
    os.system("ip route del table outernet default")
    os.system("ip route flush cache")
    
    os.system("iptables -P INPUT ACCEPT")
    os.system("iptables -P FORWARD ACCEPT")
    os.system("iptables -P OUTPUT ACCEPT")
    os.system("iptables -t nat -F")
    os.system("iptables -t mangle -F")
    os.system("iptables -F")
    os.system("iptables -X")
