import fcntl
import struct
import os
import socket
import hashlib
import threading
import time

from Crypto import Random
from Crypto.Cipher import ChaCha20
from Crypto.Util import Padding
from tuntap_utils import init_tun, uninit_tun


################ config starts ################
tun_name = 'tun0'
eth_name = 'ens33'
lan_ips = [
    '172.16.0.201',
    '172.16.0.202',
    '172.16.0.203',
    '172.16.0.204',
    '172.16.0.205',
]
server_addr = ('1.2.3.4', 6666)
identification = 'username'
secret = 'secret'
################# config ends #################

# handle configuration
identification = identification.encode('utf-8')
identification = hashlib.sha256(identification).digest()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

key = secret.encode('utf-8')
key = hashlib.sha256(key).digest()

def encrypt(key, raw):
    nonce = Random.new().read(8)
    cipher = ChaCha20.new(key=key, nonce=nonce)
    return nonce + cipher.encrypt(raw)

def decrypt(key, enc):
    nonce = enc[:8]
    cipher = ChaCha20.new(key=key, nonce=nonce)
    return cipher.decrypt(enc[8:])

# handshake
data = b'\x01' + identification
sock.sendto(encrypt(key, data), server_addr)
data, _ = sock.recvfrom(2048)
data = decrypt(key, data)
tun_ip_raw = data[1:5]
dst_ip_raw = data[5:9]
tun_ip = str(dst_ip_raw[0]) + '.' + str(dst_ip_raw[1]) + '.' + str(dst_ip_raw[2]) + '.' + str(dst_ip_raw[3])
dst_ip = str(tun_ip_raw[0]) + '.' + str(tun_ip_raw[1]) + '.' + str(tun_ip_raw[2]) + '.' + str(tun_ip_raw[3])
print("handshake successful, tun_ip: %s, dst_ip: %s" % (tun_ip, dst_ip))

# setup tuntap
init_tun(eth_name, tun_name, lan_ips, tun_ip, dst_ip)

TUNSETIFF = 0x400454ca
TUNSETOWNER = TUNSETIFF + 2
IFF_TUN = 0x0001
IFF_TAP = 0x0002
IFF_NO_PI = 0x1000

tun = os.open('/dev/net/tun', os.O_RDWR)
ifr = struct.pack('16sH', tun_name.encode('utf-8'), IFF_TUN | IFF_NO_PI)
fcntl.ioctl(tun, TUNSETIFF, ifr)
fcntl.ioctl(tun, TUNSETOWNER, 1000)

# setup threads
def handle_read():
    while True:
        data = os.read(tun, 2048)
        data = b'\x03' + identification + data
        sock.sendto(encrypt(key, data), server_addr)

def handle_recv():
    while True:
        data, _ = sock.recvfrom(2048)
        data = decrypt(key, data)[1:]
        os.write(tun, data)

read_thread = threading.Thread(target=handle_read)
read_thread.start()
recv_thread = threading.Thread(target=handle_recv)
recv_thread.start()

while True:
    time.sleep(1)
