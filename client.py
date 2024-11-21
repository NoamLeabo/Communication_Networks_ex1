from socket import socket, AF_INET, SOCK_DGRAM
import sys

# the server's IP
serverIP = sys.argv[1]

# the server's Port
serverPort = int(sys.argv[2])

# we set up the client's socket
s = socket(AF_INET, SOCK_DGRAM)

# the client loop
while True:
    # the checked addres
    req = input()
    # send a url req to the server
    s.sendto(f"{req}".encode('utf-8'), (serverIP, serverPort))

    # receive the res from the server
    data, addr = s.recvfrom(1024)
    data = data.decode("utf-8")
    # if we receive a valid res
    if data[-1] =='A':
        # we print only the IP
        print(data.split(',')[1])
    else:
        # print the res
        print(data)

# close the socket
s.close()