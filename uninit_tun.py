from tuntap_utils import uninit_tun

lan_ips = [
    '172.16.0.201',
    '172.16.0.202',
    '172.16.0.203',
    '172.16.0.204',
    '172.16.0.205',
]

uninit_tun('tun0', lan_ips)
