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
    print(url)
    line = "www.co.il,1.2.3.4,A"
    s.sendto(line.encode('utf-8'), addr)