#!/bin/bash
input_file=$1
output_file=$2

# get file line number
line_num=$(wc -l $input_file | awk '{print $1}')

# get ip from domain
cnt=0
while read line
do
    # extract only IPv4 address
    ips=$(nslookup $line | grep -A 1 "Name:" | grep "Address" | awk '{print $2}' | grep -v ":")

    # save domain and ips to file in one line, splited by space
    for ip in $ips
    do
        echo "$line $ip" >> $output_file
    done

    # print current processed line number
    cnt=$((cnt + 1))
    echo -ne "\n[$input_file: $cnt/$line_num] $line"
done < $input_file