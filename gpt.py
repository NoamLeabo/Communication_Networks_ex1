import subprocess
import time
import os

# Helper function to run a command and capture its output
def run_command(command, input_data=None):
    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=input_data)
        return stdout.strip(), stderr.strip(), process.returncode
    except Exception as e:
        return "", str(e), 1

# Test setup
def start_server(port, zone_file):
    return subprocess.Popen(
        ["python", "server.py", str(port), zone_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

def start_resolver(port, parent_ip, parent_port, cache_duration):
    return subprocess.Popen(
        ["python", "resolver.py", str(port), parent_ip, str(parent_port), str(cache_duration)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

def run_client(server_ip, server_port, query):
    stdout, stderr, _ = run_command(
        ["python", "client.py", server_ip, str(server_port)],
        input_data=query
    )
    return stdout, stderr

# Test cases
def run_tests():
    # Zone files setup
    with open("zone.txt", "w") as f:
        f.write("biu.ac.il,1.2.3.4,A\nco.il,127.0.0.1:777,NS\nexample.com,1.2.3.7,A\n")
    with open("zone2.txt", "w") as f:
        f.write("www.google.co.il,1.2.3.8,A\nmail.google.co.il,1.2.3.9,A\n")
    
    # Start servers
    server1 = start_server(55555, "zone.txt")
    server2 = start_server(777, "zone2.txt")
    time.sleep(1)  # Wait for servers to start

    # Start resolver
    resolver = start_resolver(12345, "127.0.0.1", 55555, 60)
    time.sleep(1)  # Wait for resolver to start

    try:
        # Test Case 1: Basic Server Response
        output, _ = run_client("127.0.0.1", 55555, "biu.ac.il")
        assert output == "1.2.3.4", f"Test Case 1 Failed: {output}"

        # Test Case 2: Resolver with Caching
        output, _ = run_client("127.0.0.1", 12345, "example.com")
        assert output == "1.2.3.7", f"Test Case 2 Failed: {output}"

        # Test Case 3: Non-existent Domain
        output, _ = run_client("127.0.0.1", 12345, "unknown-domain.com")
        assert output == "non-existent domain", f"Test Case 3 Failed: {output}"

        # Test Case 4: Chain Communication
        output, _ = run_client("127.0.0.1", 12345, "mail.google.co.il")
        assert output == "1.2.3.9", f"Test Case 4 Failed: {output}"

        # Test Case 5: Cache Expiry
        time.sleep(10)  # Wait for cache to expire
        output, _ = run_client("127.0.0.1", 12345, "example.com")
        assert output == "1.2.3.7", f"Test Case 5 Failed: {output}"

        # Test Case 6: Invalid Input
        output, _ = run_client("127.0.0.1", 12345, "example@@@.com")
        assert output == "non-existent domain", f"Test Case 6 Failed: {output}"

        print("All tests passed!")
    finally:
        # Clean up processes
        server1.terminate()
        server2.terminate()
        resolver.terminate()
        server1.wait()
        server2.wait()
        resolver.wait()

# Run tests
run_tests()
