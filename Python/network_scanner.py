#!/usr/bin/env python

import optparse, scapy.all as scapy

def get_arguments():
    parse = optparse.OptionParser()
    parse.add_option('-r', '--range', dest='range', help='Enter the range to find networks')
    (options, arguments) = parse.parse_args()
    if not options.range:
        parse.error('Please specify a range to discover networks or use --help for more information')
    return options

def scan(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    clients_list = []
    for element in answered_list:
        client_dict = {'ip': element[1].psrc, 'mac': element[1].hwsrc}
        clients_list.append(client_dict)
    return clients_list

def print_result(results_list):
    print('---------------------------------\nIP\t\tMAC address\n---------------------------------')
    for client in results_list:
        print(client['ip'], '\t', client['mac'])

options = get_arguments()
scan_result = scan(options.range)
print_result(scan_result)