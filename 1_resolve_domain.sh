#!/bin/bash
toplist_name=$1
out_GFW=$2
domain_file='./data/'$toplist_name'/domain.csv'
echo "======= ======= Start Scaning Toplist : "$toplist_name" ======= ======="

#0. create and cleanup working dir
working_dir=/tmp/$toplist_name
mkdir -p /tmp/$toplist_name
rm $working_dir/*

#1. split domain file into different files
sed -i 's/\r$//' $domain_file
cut -d ',' $domain_file -f 2 > $working_dir/domain_file.dat
split -l 10000 $working_dir/domain_file.dat $working_dir/domain_ -d -a 3 --additional-suffix=.txt

#2. convert domain to ip
for file in $working_dir/domain_*.txt
do
    echo "convert $file"
    ./utils/nslookup.sh $file $file.ip &
done

wait

#3. merge ip files
cat $working_dir/domain_*.txt.ip > $working_dir/domain_IPs.dat
rm $working_dir/domain_*.txt
rm $working_dir/domain_*.txt.ip

#4. launch zmap scan
cut -d ' ' -f 2 $working_dir/domain_IPs.dat > $working_dir/IP_to_scan.dat

#5. TCP syn scan
sudo zmap -I $working_dir/IP_to_scan.dat -p 80 -M tcp_synscan -O json -f saddr -o $working_dir/tcp_scan.dat

#6. MPTCP syn scan
sudo zmap -I $working_dir/IP_to_scan.dat -p 80 -M tcp_mpsynscan -O json -f saddr,mptcp -o $working_dir/mptcp_scan.dat

#7. Analysis result
python3 ./utils/merge_scan_result.py --domain_file $working_dir/domain_file.dat \
                                     --domain_ip_file $working_dir/domain_IPs.dat \
                                     --tcp_scan_file $working_dir/tcp_scan.dat \
                                     --mptcp_scan_file $working_dir/mptcp_scan.dat  \
                                     --output_file $working_dir/analysis.dat

#8. save result
cp $working_dir/analysis.dat ./data/$toplist_name/scan_result_$2.dat

