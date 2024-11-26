# Bonappeti
## HTTP 401 Unauthorized Mass Brute Force
This Python script runs the shef command for many ports, creates a directory for each and tries different passwords to gain access. 
It does multiple tasks at once using threads and adds delays for 5 seconds after executing `shef` 3 times to avoid anti-DOS blocks.

## Usage
1. Install Shef (https://github.com/1hehaq/shef)
2. Use `filter.py` to filter the ports if needed*
3. Edit `bruteforce.py` script to fit your Shodan seach needs (`shef_command =....`)
4. Run `bruteforce.py`

Successful attempts will be output in `success.txt`

# *`filter.py`
Filters out number of ports when directly copied from Shodan
Example: 
`9944
1
9997
1
10909
1`
