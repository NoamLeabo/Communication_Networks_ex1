import time
cache = [("tett,1.3.2.4,A", time.time()-0.1)]
zone_file = open('zone.txt', 'r').read()
url = "tett.co.il,1.3.2.4:984,NS"
for line in zone_file.split('\n'):
    if line and line.split(',')[0] in url:
        print(f"Found substring: {line.split(',')[0]}")
        print(f"Returning whole line: {line.strip()}")