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
import shutil


# Constants
HOME_DIR = str(Path.home())
TRIE_DIR = os.path.join(HOME_DIR, ".ip2asn")
os.makedirs(TRIE_DIR, exist_ok=True)
TRIE_SAVE_PATH = os.path.join(TRIE_DIR, "trie_data.json.gz")

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()


def setup_trie_data():
    """
    Set up trie data by copying the `trie_data.json.gz` file from the 
    current directory to the `~/.ip2asn/` directory.
    
    The function performs the following steps:
    1. Determines the home directory of the user.
    2. Creates (if it doesn't exist) a directory named `.ip2asn` in the user's home directory.
    3. Checks if the `trie_data.json.gz` exists in the current directory.
    4. If the file exists, copies it to the `~/.ip2asn/` directory.
    
    """
    # Get home directory
    home_dir = Path.home()

    # Create the directory ~/.ip2asn
    target_dir = home_dir / ".ip2asn"
    target_dir.mkdir(exist_ok=True)

    # Copy trie_data.json.gz from the current directory to ~/.ip2asn
    current_dir = Path.cwd()
    trie_data_path = current_dir / "trie_data.json.gz"
    
    if trie_data_path.exists():
        shutil.copy(trie_data_path, target_dir)
    else:
        pass




def is_private_ip(ip):
    """
    Check if the given IP is a private IP.

    Args:
    - ip (str): IP address to check.

    Returns:
    - bool: True if the IP is private, False otherwise.
    """
    return ipaddress.ip_address(ip).is_private

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
        asn_map[ip] = trie.get(ip)
    return asn_map

parser = argparse.ArgumentParser(description="Find ASN for given IPs.")
parser.add_argument("-j", "--json", action='store_true', help='Output results in JSON format.')
parser.add_argument("-rp", "--rib-path", default="processed_rib.txt", help="Path to the RIB file. Defaults to 'processed_rib.txt'.")
args = parser.parse_args()


# Main execution starts here

setup_trie_data()

if os.path.exists(TRIE_SAVE_PATH):
    logger.info("Loading trie from saved file...")
    trie = load_trie_from_file(TRIE_SAVE_PATH)
else:
    logger.info("Serialized trie not found. Building trie from RIB dump...")
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
