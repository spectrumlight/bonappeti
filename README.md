# Bonappeti
## HTTP 401 Unauthorized Mass Brute Force
This Python script runs the shef command for many ports, creates a directory for each and tries different passwords to gain access. 
It runs `150` brute force tasks at once using threads and adds delays for 5 seconds after executing `shef` 3 times to avoid anti-DOS blocks.
Number of tasks can be modified in `max_concurrent_ports`.
Education purposes only.

## Usage
1. Install Shef: https://github.com/1hehaq/shef
2. Use `filter.py` to filter the ports if needed. It will create `ports.txt`
3. Create `ports.txt` in the directory, if you did not use `filter.py`
4. Edit `bruteforce.py` script to fit your Shodan seach needs (`shef_command =....`)
5. Run `bruteforce.py`: `nohup python3 bruteforce.py > bruteforce.log 2>&1 &`

Successful attempts will be output in `success.txt`

### `filter.py`
Filters out number of ports when directly copied from Shodan. 
Example: 
`9944
1
9997
1
10909
1` to `9944
9997
10909`
