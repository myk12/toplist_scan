#!/bin/bash

# input: domain ip file
# do: launch zmap scan port 80
# output: csv file [domain ip tcp mptcp] scan result
input_file=$1
output_file=$2

# 1. extract IPs
cut -d ' ' -f 2 $input_file > /tmp/$input_file.ip

# 2. tcp scan
sudo zmap -I /tmp/$input_file.ip -p 80 -o /tmp/$input_file.tcp -M tcp_synscan -O json -f saddr

# 3. mptcp scan
sudo zmap -I /tmp/$input_file.ip -p 80 -o /tmp/$input_file.mptcp -M tcp_mpsynscan -O json -f saddr,mptcp

# 4. merge scan result
python3 ./utils/merge_scan_result.py --domain_ip_file $input_file --tcp_scan_file /tmp/$input_file.tcp --mptcp_scan_file /tmp/$input_file.mptcp --output_file $output_file
