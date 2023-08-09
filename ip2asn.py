#!/usr/bin/env python3

import pytricia
import sys
import json
import gzip
from tqdm import tqdm
import os
from termcolor import colored
import argparse
from collections import defaultdict
import logging
import ipaddress
from pathlib import Path



# Constants
HOME_DIR = str(Path.home())
TRIE_DIR = os.path.join(HOME_DIR, ".ip2asn")
os.makedirs(TRIE_DIR, exist_ok=True)
TRIE_SAVE_PATH = os.path.join(TRIE_DIR, "trie_data.json.gz")

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()








def is_private_ip(ip):
    """
    Check if the given IP is a private IP.

    Args:
    - ip (str): IP address to check.

    Returns:
    - bool: True if the IP is private, False otherwise.
    """
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        # Handle the error (you can raise another exception, print an error message, etc.)
        pass
        return False


    

def build_trie_from_rib(rib_file_path):
    """
    Build a Trie structure from the given RIB (Routing Information Base) file.

    Args:
    - rib_file_path (str): Path to the RIB file.

    Returns:
    - pytricia.PyTricia: Trie structure mapping IP prefixes to AS numbers.
    """
    trie = pytricia.PyTricia()
    
    try:
        with open(rib_file_path, "r") as f:
            total_lines = sum(1 for _ in f)
            f.seek(0)
            current_prefix = None
            for line in tqdm(f, total=total_lines, desc="Building Trie"):
                if line.startswith("PREFIX:"):
                    current_prefix = line.split()[-1]
                elif line.startswith("ASPATH:") and current_prefix:
                    asn = line.split()[-1]
                    trie[current_prefix] = asn
                    current_prefix = None
    except FileNotFoundError:
        logger.error(f"RIB file '{rib_file_path}' not found. Please ensure the path is correct or run get_rib.sh to generate the file.")
        sys.exit(1)

    with gzip.open(TRIE_SAVE_PATH, "wt") as f:
        json.dump({key: trie[key] for key in trie}, f)

    return trie


def load_trie_from_file(file_path):
    """
    Load a Trie from a saved file.

    Args:
    - file_path (str): Path to the saved Trie file.

    Returns:
    - pytricia.PyTricia: Loaded Trie structure.
    """
    with gzip.open(file_path, "rt") as f:
        data = json.load(f)
    trie = pytricia.PyTricia()
    for key, value in data.items():
        trie[key] = value
    return trie

def find_asn_for_ips(ips, trie):
    """
    Find AS numbers for given IPs using the Trie structure.

    Args:
    - ips (list of str): List of IP addresses to search for.
    - trie (pytricia.PyTricia): Trie structure to use for lookup.

    Returns:
    - dict: Mapping of IP addresses to their corresponding AS numbers.
    """
    asn_map = {}
    for ip in ips:
        try:
            asn_map[ip] = trie.get(ip)
        except ValueError:
            pass
    return asn_map

parser = argparse.ArgumentParser(description="Find ASN for given IPs.")
parser.add_argument("-j", "--json", action='store_true', help='Output results in JSON format.')
parser.add_argument("-rp", "--rib-path", default="processed_rib.txt", help="Path to the RIB file. Defaults to 'processed_rib.txt'.")
args = parser.parse_args()


# Main execution starts here


if os.path.exists(TRIE_SAVE_PATH):
    trie = load_trie_from_file(TRIE_SAVE_PATH)
else:
    logger.info("Serialized trie not found. Building trie from RIB dump...")
    logger.info("This may take some time..")
    trie = build_trie_from_rib(args.rib_path)

ips_to_search = [line.strip() for line in sys.stdin]
filtered_ips_to_search = [ip for ip in ips_to_search if not is_private_ip(ip)]
asns = find_asn_for_ips(filtered_ips_to_search, trie)

if args.json:
    asn_to_ips = defaultdict(list)
    for ip, asn in asns.items():
        if asn:
            asn_to_ips[f"AS{asn}"].append(ip)
        else:
            asn_to_ips["NOT_FOUND"].append(ip)
    print(json.dumps(asn_to_ips, indent=4))
else:
    for ip, asn in asns.items():
        if asn:
            print(f"{colored(ip, 'yellow')} {colored(f'[AS{asn}]', 'green')}")
        else:
            print(f"{colored(ip, 'yellow')} {colored('NOT_FOUND', 'red')}")
