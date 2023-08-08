Based on the format provided for `revwhoix`, here is the README for `ip2asn`:

<h1 align="center">
    ip2asn
  <br>
</h1>

<h4 align="center">A utility to quickly map IP addresses to their respective ASN</h4>

<p align="center">
  <a href="#installation">🏗️ Installation</a>  
  <a href="#updating-rib-data">🔄 Updating RIB Data</a>  
  <a href="#usage">⛏️ Usage</a>
  <a href="#how-it-works">📖 How It Works</a>
  <br>
</p>


# Installation

```sh
git clone https://github.com/devanshbatham/ip2asn
cd ip2asn
./setup.sh
```



*Note:* The utility comes pre-packed with trie data, so if you don't wish to update the RIB data, it should work well right off the bat.

# Usage


```sh
cat ips.txt | ip2asn


```

- With `--json` for JSON output: 

```sh
cat ips.txt | ip2asn --json
```


- To use a different RIB file to build the trie (read the section below):

```sh
echo "8.8.8.8" | ip2asn --rib-path /path/to/rib.txt
```

# Updating RIB Data

If you wish to build the trie yourself or want to update the trie data:

1. Delete the `~/.ip2asn` folder.
2. Run the `get-rib.sh` script.
3. Build the trie using the `--rib-path` or `--rp` option with the updated RIB data.


# How It Works

The `ip2asn` utility employs a trie data structure to map IP address prefixes to their corresponding Autonomous System Numbers (ASN). Each key in the trie represents an IP address prefix, while the corresponding value denotes the AS number that announces these prefixes. The utility checks this trie to find the longest matching prefix for each IP and retrieves its associated ASN.