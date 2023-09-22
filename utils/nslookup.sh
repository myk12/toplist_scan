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
    #echo $line
    #nslookup $line
    ips=$(nslookup $line | grep -A 1 "Name:" | grep "Address" | awk '{print $2}' | grep -v ":")
    #echo $ips
    for ip in $ips
    do
        echo "$line $ip" >> $output_file
    done
    if ! [[ $line == www.* ]];then
	    ips_www=$(nslookup www.$line | grep -A 1 "Name:" | grep "Address" | awk '{print $2}' | grep -v ":")
	#echo $ips_www
    	for ip in $ips_www
    	do
	    	echo "$line $ip" >> $output_file
    	done
    fi

    # print current processed line number
    cnt=$((cnt + 1))
    echo -ne "\n[$input_file: $cnt/$line_num] $line"
    echo -ne "\n[$input_file: $cnt/$line_num] www.$line"
done < $input_file
