import socket

# we aquire the urls in the local file 
zone_file = open('zone.txt', 'r').read()
# we create the server's socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# we bind it with a port
s.bind(('', 12345))

# the server loop
while True:
    # receive a req
    url, addr = s.recvfrom(1024)
    # decode the req url
    url = url.decode('utf-8')
    # we check if we have a match
    test = zone_file.find(url)
    # if the file contains the req url we shall return it
    if test != -1:
        # we extract the url from the file
        start = zone_file.rfind('\n', 0, test) + 1
        end = zone_file.find('\n', test)
        # the req line
        line = zone_file[start:end]
        # send back to the sender
        s.sendto(line.encode('utf-8'), addr)
        continue
    
    # an var that indicates if we found a substring of the req url in the file 'zone'
    was_found = False
    # we go over each line in the file
    for line in zone_file.split('\n'):
        # if we have not found yet
        if not was_found:
            # we check for substring
            if line and line.split(',')[0] in url:
                # we send the whole line that fit
                s.sendto(line.strip().encode('utf-8'), addr)
                # update the var accordingly
                was_found = True

    # if we didn't find any substring we return "non-existent response" 
    if not was_found:
        res = "non-existent response"
        s.sendto(res.encode('utf-8'), addr) 