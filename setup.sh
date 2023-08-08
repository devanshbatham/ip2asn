#!/bin/bash

# Rename the ip2asn.py file to ip2asn
mv ip2asn.py ip2asn

# Move the ip2asn file to /usr/local/bin
sudo mv ip2asn /usr/local/bin/

# Make the ip2asn file executable
sudo chmod +x /usr/local/bin/ip2asn

echo "ip2asn has been installed successfully! Usage 'cat ips.txt | ip2asn'"

mkdir $HOME/.ip2asn
mv rib-trie/trie_data.json.gz $HOME/.ip2asn/trie_data.json.gz