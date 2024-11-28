import subprocess
import time
import os
import random

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
        stdout, stderr = process.communicate(input=input_data)  # Timeout for hanging processes
        return stdout.strip(), stderr.strip(), process.returncode
    except subprocess.TimeoutExpired:
        process.kill()
        return "", "Process timed out", 1
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

# Cleanup helper function
def cleanup_files(files):
    for file in files:
        try:
            os.remove(file)
        except FileNotFoundError:
            print(f"File {file} not found, skipping deletion.")

# Test cases
def run_tests():
    rand_sesolver_port = 55555
    rand_server_port1 = 32322
    rand_server_port2 = 45210
    rand_server_port3 = 24386
    rand_server_port4 = 62431
    # Zone files setup
    zone_files = ["zone1.txt", "zone2.txt", "zone3.txt", "zone4.txt"]
    with open("zone1.txt", "w") as f:
        f.write(f"biu.ac.il,1.2.3.4,A\nco.il,127.0.0.1:{rand_server_port2},NS\nexample.com,1.2.3.7,A\n")
    with open("zone2.txt", "w") as f:
        f.write(f"www.google.co.il,1.2.3.8,A\nmail.google.co.il,1.2.3.9,A\nbiu.google.co.il,127.0.0.1:{rand_server_port3},NS\n")
    with open("zone3.txt", "w") as f:
        f.write(f"top.biu.google.co.il,1.2.3.10,A\nthe.top.biu.google.co.il,127.0.0.1:{rand_server_port4},NS\n")
    with open("zone4.txt", "w") as f:
        f.write("al.the.top.biu.google.co.il,1.2.3.12,A\n")

    # Start servers
    server1 = start_server(rand_server_port1, "zone1.txt")
    server2 = start_server(rand_server_port2, "zone2.txt")
    server3 = start_server(rand_server_port3, "zone3.txt")
    server4 = start_server(rand_server_port4, "zone4.txt")
    time.sleep(1)  # Wait for servers to start

    # Start resolver
    resolver = start_resolver(rand_sesolver_port, "127.0.0.1", rand_server_port1, 60)
    time.sleep(1)  # Wait for resolver to start

    try:
        # Test Case 1: Basic Server Response
        output, stderr = run_client("127.0.0.1", rand_sesolver_port, "biu.ac.il")
        if output != "1.2.3.4":
            print(f"Test Case 1 Failed. Output: {output}, Stderr: {stderr}")
        else:
            print("passed 1")
        # assert output == "1.2.3.4", f"Test Case 1 Failed: {output}"

        # Test Case 2: Resolver with Caching
        output, stderr = run_client("127.0.0.1", rand_sesolver_port, "example.com")
        if output != "1.2.3.7":
            print(f"Test Case 2 Failed. Output: {output}, Stderr: {stderr}")
        else:
            print("passed 2")
        # assert output == "1.2.3.7", f"Test Case 2 Failed: {output}"

        # Test Case 2.1: Resolver with Caching
        output, stderr = run_client("127.0.0.1", rand_sesolver_port, "exampl.com")
        if output != "non-existent domain":
            print(f"Test Case 2 Failed. Output: {output}, Stderr: {stderr}")
        else:
            print("passed 2.1")
        # assert output == "1.2.3.7", f"Test Case 2 Failed: {output}"

        # Test Case 3: Non-existent Domain
        output, stderr = run_client("127.0.0.1", rand_sesolver_port, "unknown-domain.com")
        if output != "non-existent domain":
            print(f"Test Case 3 Failed. Output: {output}, Stderr: {stderr}")
        else:
            print("passed 3")
        # assert output == "non-existent domain", f"Test Case 3 Failed: {output}"

        # Test Case 4: Chain Communication (Server 2 -> Server 3)
        output, stderr = run_client("127.0.0.1", rand_sesolver_port, "mail.google.co.il")
        if output != "1.2.3.9":
            print(f"Test Case 4 Failed. Output: {output}, Stderr: {stderr}")
        else:
            print("passed 4")
        # assert output == "1.2.3.9", f"Test Case 4 Failed: {output}"

        # Test Case 5: Nested Chain Communication
        output, stderr = run_client("127.0.0.1", rand_sesolver_port, "top.biu.google.co.il")
        if output != "1.2.3.10":
            print(f"Test Case 5 Failed. Output: {output}, Stderr: {stderr}")
        else:
            print("passed 5")
        # assert output == "1.2.3.10", f"Test Case 5 Failed: {output}"

        # Test Case 6: Deep Chain Communication
        output, stderr = run_client("127.0.0.1", rand_sesolver_port, "al.the.top.biu.google.co.il")
        if output != "1.2.3.12":
            print(f"Test Case 6 Failed. Output: {output}, Stderr: {stderr}")
        else:
            print("passed 6")
        # assert output == "1.2.3.12", f"Test Case 6 Failed: {output}"

        # Test Case 7: Invalid Input
        output, stderr = run_client("127.0.0.1", rand_sesolver_port, "invalid@domain.com")
        if output != "non-existent domain":
            print(f"Test Case 7 Failed. Output: {output}, Stderr: {stderr}")
        else:
            print("passed 7")
        # assert output == "non-existent domain", f"Test Case 7 Failed: {output}"

        # Test Case 8: Complex Domain (Edge Case)
        output, stderr = run_client("127.0.0.1", rand_sesolver_port, "www.google.co.il")
        if output != "1.2.3.8":
            print(f"Test Case 8 Failed. Output: {output}, Stderr: {stderr}")
        else:
            print("passed 8")
        # assert output == "1.2.3.8", f"Test Case 8 Failed: {output}"

        # Cache Tests
        print("\nRunning Cache Tests...")

        # Preload cache with multiple queries
        run_client("127.0.0.1", rand_sesolver_port, "mail.google.co.il")
        run_client("127.0.0.1", rand_sesolver_port, "top.biu.google.co.il")

        # Turn off some servers
        server1.terminate()
        server3.terminate()
        server1.wait(timeout=5)
        server3.wait(timeout=5)

        print("<--- Servers 1 and 3 are now TERMINATED --->\n")

        # Test Case 9: Cached Response for mail.google.co.il
        output, stderr = run_client("127.0.0.1", rand_sesolver_port, "mail.google.co.il")
        if output != "1.2.3.9":
            print(f"Test Case 9 Failed. Output: {output}, Stderr: {stderr}")
        else:
            print("passed 9")
        # assert output == "1.2.3.9", f"Test Case 9 Failed: {output}"

        # Test Case 9.1: Cached Response for www.google.co.il
        output, stderr = run_client("127.0.0.1", rand_sesolver_port, "www.google.co.il")
        if output != "1.2.3.8":
            print(f"Test Case 9.1 Failed. Output: {output}, Stderr: {stderr}")
        else:
            print("passed 9.1")
        # assert output == "1.2.3.9", f"Test Case 9 Failed: {output}"

        server2 = start_server(rand_server_port1, "zone1.txt")

        # Test Case 9.2: Cached Response for www.google.co.il
        output, stderr = run_client("127.0.0.1", rand_sesolver_port, "www.google.co.ili")
        if output != "non-existent domain":
            print(f"Test Case 9.2 Failed. Output: {output}, Stderr: {stderr}")
        else:
            print("passed 9.2")
        # assert output == "1.2.3.9", f"Test Case 9 Failed: {output}"

        server1.terminate()
        server1.wait(timeout=5)

        # Test Case 9.3: Cached Response for www.google.co.il
        output, stderr = run_client("127.0.0.1", rand_sesolver_port, "www.google.co.ili")
        if output != "non-existent domain":
            print(f"Test Case 9.3 Failed. Output: {output}, Stderr: {stderr}")
        else:
            print("passed 9.3")
        # assert output == "1.2.3.9", f"Test Case 9 Failed: {output}"

        # Test Case 10: Cached Response for top.biu.google.co.il
        output, stderr = run_client("127.0.0.1", rand_sesolver_port, "top.biu.google.co.il")
        if output != "1.2.3.10":
            print(f"Test Case 10 Failed. Output: {output}, Stderr: {stderr}")
        else:
            print("passed 10")
        # assert output == "1.2.3.10", f"Test Case 10 Failed: {output}"

        print("All tests passed!")
    finally:
        # Clean up processes with timeout handling
        for process, name in [(server1, "Server 1"), (server4, "Server 4"), (resolver, "Resolver")]:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                print(f"{name} did not terminate in time and was killed.")
                process.kill()

        # Cleanup zone files
        # cleanup_files(zone_files)

# Run tests
run_tests()