import os
import pandas as pd
import argparse
import json
from tqdm import tqdm

###################################################################
#
#        DataFrame Format
#         __________ _____________ ____________ ______________
#        |  domain  |  resolved   |  tcp_scan  |  mptcp_scan  |
#        |``````````|`````````````|````````````|``````````````| 
#        |__________|_____________|____________|______________|
#
#
####################################################################

class MergeScanResult:
    def __init__(self):
        #self.scan_result_df = pd.DataFrame(columns=['domain', 'resolved', 'tcp_scan', 'mptcp_scan'])
        self.data_column_names = ['resolved', 'tcp_scan', 'mptcp_scan']
        self.none_resolved_domain_count = 0
        self.domain_IPs_dict = {}
        self.domain_TCP_scan_dict = {}
        self.domain_MPTCP_scan_dict = {}
        self.IP_domain_mapping_dict = {}
    
    def read_domain_file(self, domain_file):
        print("Loading domain file...")
        self.scan_result_df = pd.read_csv(domain_file, header=None, names=['domain'])

        self.scan_result_df['resolved'] = 0
        self.scan_result_df['tcp_scan'] = 0
        self.scan_result_df['mptcp_scan'] = 0
        print(self.scan_result_df)
    
    def read_domain_ip_file(self, domain_ip_file):
        print("Parsing domain IP file...")
        total_lines = sum(1 for line in open(domain_ip_file))
        with tqdm(total=total_lines) as pbar:
            with open(domain_ip_file, 'r') as f:
                for line in f:
                    domain, ip = line.strip().split(' ')

                    #self.scan_result_df.loc[self.scan_result_df['domain'] == domain, 'resolved'] = 1
                    
                    if domain not in self.domain_IPs_dict:
                        self.domain_IPs_dict[domain] = set()
                    self.domain_IPs_dict[domain].add(ip)

                    # add IP domain mapping
                    self.IP_domain_mapping_dict[ip] = domain

                    # init domain scan result dict
                    if domain not in self.domain_TCP_scan_dict:
                        self.domain_TCP_scan_dict[domain] = 0
                    if domain not in self.domain_MPTCP_scan_dict:
                        self.domain_MPTCP_scan_dict[domain] = 0
                    pbar.update(1)
        
        resolved_domain = self.domain_IPs_dict.keys()
        #print(type(resolved_domain))
        self.scan_result_df['resolved'] = self.scan_result_df['domain'].isin(resolved_domain).astype(int)
        print(self.scan_result_df)
    
    def merge_tcp_scan_result(self, tcp_scan_file):
        print("Loading tcp scan result...")
        with open(tcp_scan_file, 'r') as f:
            for line in f:
                res_json = json.loads(line.strip())
                ip = res_json['saddr']
                if ip not in self.IP_domain_mapping_dict:
                    error_msg = 'IP {} not in domain IP mapping'.format(ip)
                    raise Exception(error_msg)
                
                domain = self.IP_domain_mapping_dict[ip]
                self.domain_TCP_scan_dict[domain] = 1
        
        tcp_domain = self.domain_TCP_scan_dict.keys()
        self.scan_result_df['tcp_scan'] = self.scan_result_df['domain'].isin(tcp_domain).astype(int)

    def merge_mptcp_scan_result(self, mptcp_scan_file):
        print("Loading mptcp scan result...")
        with open(mptcp_scan_file, 'r') as f:
            for line in f:
                res_json = json.loads(line.strip())
                ip = res_json['saddr']
                mptcp = res_json['mptcp']

                if ip not in self.IP_domain_mapping_dict:
                    error_msg = 'IP {} not in domain IP mapping'.format(ip)
                    raise Exception(error_msg)
                
                domain = self.IP_domain_mapping_dict[ip]
                if self.domain_MPTCP_scan_dict[domain] < mptcp:
                    self.domain_MPTCP_scan_dict[domain] = mptcp
        
        mapping_series = pd.Series(self.domain_MPTCP_scan_dict).astype(int)
        self.scan_result_df['mptcp_scan'] = self.scan_result_df['domain'].map(mapping_series)

    def write_output(self, output_file):
        print("Writing datafram to output file {}".format(output_file))
        print(self.scan_result_df)
        self.scan_result_df.to_csv(output_file)

def main():
    parser = argparse.ArgumentParser(description='Merge scan result')
    parser.add_argument('--domain_file', required=True, help="Toplist domain file")
    parser.add_argument('--domain_ip_file', required=True, help='Domain and ip file')
    parser.add_argument('--tcp_scan_file', required=True, help='TCP scan result file')
    parser.add_argument('--mptcp_scan_file', required=True, help='MPTCP scan result file')
    parser.add_argument('--output_file', required=True, help='Output file')
    args = parser.parse_args()

    domain_file = args.domain_file
    domain_ip_file = args.domain_ip_file
    tcp_scan_file = args.tcp_scan_file
    mptcp_scan_file = args.mptcp_scan_file
    output_file = args.output_file

    merge_scan_result = MergeScanResult()
    merge_scan_result.read_domain_file(domain_file)
    merge_scan_result.read_domain_ip_file(domain_ip_file)
    merge_scan_result.merge_tcp_scan_result(tcp_scan_file)
    merge_scan_result.merge_mptcp_scan_result(mptcp_scan_file)
    merge_scan_result.write_output(output_file)

if __name__ == '__main__':
    main()
