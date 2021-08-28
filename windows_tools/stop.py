import os
import sys
import subprocess
import netifaces
import winreg
import socket

REG_CONTROL_NETWORK = r'SYSTEM\CurrentControlSet\Control\Network\{4d36e972-e325-11ce-bfc1-08002be10318}'

def get_iface_name(iface):
    iface_name = None
    reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    reg_key = winreg.OpenKey(reg, REG_CONTROL_NETWORK)
    try:
        reg_subkey = winreg.OpenKey(reg_key, iface + r'\Connection')
        iface_name = winreg.QueryValueEx(reg_subkey, 'Name')[0]
    except FileNotFoundError:
        pass
    return iface_name

def get_default_iface():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(('8.8.8.8', 80))
    addr = sock.getsockname()[0]

    iface = None
    for item in netifaces.interfaces():
        ifaddr = netifaces.ifaddresses(item)
        if netifaces.AF_INET not in ifaddr:
            continue
        cur_addr = netifaces.ifaddresses(item)[netifaces.AF_INET][0]['addr']
        if cur_addr == addr:
            iface = item
            break
    return iface

def execute(cmd):
    CREATE_NO_WINDOW = 0x08000000
    ret = subprocess.call(cmd, creationflags=CREATE_NO_WINDOW)

eth_name = get_iface_name(get_default_iface())
execute('netsh interface ipv4 set address name="%s" source=dhcp' % (eth_name,))
execute('netsh interface ipv4 set dnsservers name="%s" source=dhcp' % (eth_name,))
execute('netsh interface ipv4 set subinterface "%s" mtu=1500' % (eth_name,))
