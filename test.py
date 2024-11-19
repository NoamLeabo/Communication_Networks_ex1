import socket

# we aquire the urls in the local file 
zone_file = open('zone.txt', 'r').read()
# we create the server's socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# we bind it with a port
s.bind(('', 777))

# the server loop
while True:
    # receive a req
    url, addr = s.recvfrom(1024)
    to_send = "w.co.il,127.0.0.1:888,NS"
    s.sendto(to_send.encode('utf-8'), addr)