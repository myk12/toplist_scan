#!/bin/bash
input_file=$1
output_file=$2

#1. split domain file into different files
split -l 100000 $input_file /tmp/domain_ -d -a 3 --additional-suffix=.txt

#2. convert domain to ip
for file in /tmp/domain_*.txt
do
    echo "convert $file"
    ./nslookup.sh $file $file.ip &
done

wait

#3. merge ip files
cat /tmp/domain_*.txt.ip > $output_file

#4. remove tmp files
rm /tmp/domain_*.txt
rm /tmp/domain_*.txt.ip
