# Bonappeti
## HTTP 401 Unauthorized
This Python script runs the shef command for many ports, creates a directory for each and tries different passwords to gain access. 
It does multiple tasks at once using threads and adds delays for 5 seconds after executing `shef` 3 times to avoid anti-DOS blocks.

## Usage
1. Install Shef (https://github.com/1hehaq/shef)
2. Edit `bruteforce.py` to 
3. Edit `bruteforce.py` script to fit your Shodan seach needs (look for `shef_command = f"shef -q \"country:test '401' port:{port}\" > {output_file}"`)
4. Run `bruteforce.py` 
