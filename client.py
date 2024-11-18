from socket import socket, AF_INET, SOCK_DGRAM

# we set up the client's socket
s = socket(AF_INET, SOCK_DGRAM)
# send a url req to the server
s.sendto(b'example.com', ('127.0.0.1', 8888))

# receive the res from the server
data, addr = s.recvfrom(1024)
# print the res
print(data.decode('utf-8'))

# close the socket
s.close()