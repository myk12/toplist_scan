import os
import argparse
import json

class MergeScanResult:
    def __init__(self):
        self.domain_IPs_dict = {}
        self.domain_TCP_scan_dict = {}
        self.domain_MPTCP_scan_dict = {}
        self.IP_domain_mapping_dict = {}

    
    def read_domain_ip_file(self, domain_ip_file):
        with open(domain_ip_file, 'r') as f:
            for line in f:
                domain, ip = line.strip().split(' ')
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
    
    def merge_tcp_scan_result(self, tcp_scan_file):
        with open(tcp_scan_file, 'r') as f:
            for line in f:
                res_json = json.loads(line.strip())
                ip = res_json['saddr']
                if ip not in self.IP_domain_mapping_dict:
                    error_msg = 'IP {} not in domain IP mapping'.format(ip)
                    raise Exception(error_msg)
                
                domain = self.IP_domain_mapping_dict[ip]
                self.domain_TCP_scan_dict[domain] = 1

    def merge_mptcp_scan_result(self, mptcp_scan_file):
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

    def write_output(self, output_file):
        with open("./analysis.dat", 'w') as f:
            for domain in self.domain_IPs_dict:
                ips = list(self.domain_IPs_dict[domain])
                tcp = self.domain_TCP_scan_dict[domain]
                mptcp = self.domain_MPTCP_scan_dict[domain]
                f.write('{} {} {} {}\n'.format(domain, tcp, mptcp, ' '.join(ips)))
                

def main():
    parser = argparse.ArgumentParser(description='Merge scan result')
    parser.add_argument('--domain_ip_file', required=True, help='Domain and ip file')
    parser.add_argument('--tcp_scan_file', required=True, help='TCP scan result file')
    parser.add_argument('--mptcp_scan_file', required=True, help='MPTCP scan result file')
    parser.add_argument('--output_file', required=True, help='Output file')
    args = parser.parse_args()

    domain_ip_file = args.domain_ip_file
    tcp_scan_file = args.tcp_scan_file
    mptcp_scan_file = args.mptcp_scan_file
    output_file = args

    merge_scan_result = MergeScanResult()
    merge_scan_result.read_domain_ip_file(domain_ip_file)
    merge_scan_result.merge_tcp_scan_result(tcp_scan_file)
    merge_scan_result.merge_mptcp_scan_result(mptcp_scan_file)
    merge_scan_result.write_output(output_file)

if __name__ == '__main__':
    main()
