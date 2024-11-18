import socket
import time
import sys

# the server's port
myPort = int(sys.argv[1])
# the father server's ip 
parentIP = sys.argv[2]
# the father server's port
parentPort = int(sys.argv[3])
# the nums of seconds that url are saved in the cache
x = sys.argv[4]
# better notation
time_last_in_cache = float(x)

# we create a socket for the resolver server
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# we bind it with its port
s.bind(('', myPort))
# we initiate the cache
cache = []

# the server loop
while True:
    # wait for a msg (req url, addr of the sender)
    url, addr = s.recvfrom(1024)
    # before handeling the msg we clean the cache
    curr_time = time.time()
    for tuple in cache:
        old_to_check = float(tuple[1])
        if (curr_time - old_to_check > time_last_in_cache):
            cache.remove(tuple)

    # we decode the req url
    url = url.decode('utf-8')
    # check if it's in the cache
    test = any(url in item[0] for item in cache)

    # if url is in cache we send it back and we're done
    if test == True:
        # the url's index in cache
        index = next((i for i, item in enumerate(cache) if url in item[0]),
                     None)
        # the tuple with line and the time it wad inserted to the cache
        line = cache[index]
        # we extract the addres
        addres, old_time = line
        # set the data
        data = addres
        # we send back the encoded data to the addr of the sender
        s.sendto(data.encode('utf-8'), addr)


    # if url is not in cache we ask our father server for the req line
    else:
        # we create a socket to contact with the father 
        f_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # we send the father the req url
        f_socket.sendto(url.encode('utf-8'), (parentIP, parentPort))
        # we wait for an answer 
        f_data, f_addr = f_socket.recvfrom(1024)
        # decode the answered line
        f_data = f_data.decode('utf-8')
        # if the line ends with 'A' it means we can send it back to the sender and we're done

        if f_data[-1] == 'A':
            # we add the new data for the cache with the curr time
            cache.append((f_data, time.time()))
            # we send the info back
            s.sendto(f_data.encode('utf-8'), addr)
            continue

        # if the line does not end with 'A' we play "Havila O've'ret" until we get the final result
        while f_data[-1] == 'S':
            # split the f_data to extract the next IP and port
            parts = f_data.split(',')
            next_ip = parts[1].split(':')[0]
            next_port = int(parts[1].split(':')[1])
            # send the next request to the next server
            f_socket.sendto(url.encode('utf-8'), (next_ip, next_port))
            # wait for the next answer
            next_data, next_addr = f_socket.recvfrom(1024)
            # decode the next answered line
            f_data = next_data.decode('utf-8')

        # we add the new data for the cache with the curr time
        cache.append((f_data, time.time()))
        # we send the info back
        s.sendto(f_data.encode('utf-8'), addr)
