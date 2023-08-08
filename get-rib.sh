
#!/bin/bash

# Base URL for RouteViews archive
BASE_URL="http://archive.routeviews.org/bgpdata"

# Current working directory
RIB_DIR=$(pwd)

# Get yesterday's date in the format YYYY.MM and YYYYMMDD
YEAR_MONTH=$(date -d "yesterday" "+%Y.%m")
DAY=$(date -d "yesterday" "+%Y%m%d")

# Construct the URL for the previous day at 10:00
RIB_URL="$BASE_URL/$YEAR_MONTH/RIBS/rib.$DAY.1000.bz2"

# Hardcoded fallback URL
HARDCODED_URL="http://archive.routeviews.org/bgpdata/2023.08/RIBS/rib.20230807.1000.bz2"

# Filename to save the downloaded RIB
DOWNLOAD_PATH="$RIB_DIR/rib.$DAY.1000.bz2"

# Extracted RIB filename
EXTRACTED_RIB_FILE="$RIB_DIR/rib.$DAY.1000"

# Processed RIB filename
PROCESSED_RIB="$RIB_DIR/processed_rib.txt"

# Download the RIB file
echo "Downloading RIB data from $RIB_URL..."
curl -o $DOWNLOAD_PATH $RIB_URL

# Check if download was successful
if [ $? -ne 0 ]; then
    echo "Failed to download RIB data from the generated URL."
    echo "Falling back to hardcoded URL: $HARDCODED_URL..."
    curl -o $DOWNLOAD_PATH $HARDCODED_URL
    if [ $? -ne 0 ]; then
        echo "Failed to download RIB data from hardcoded URL as well."
        exit 1
    fi
fi

echo "Extracting RIB data from $DOWNLOAD_PATH..."
# Decompress the RIB data
bunzip2 $DOWNLOAD_PATH

# Check if decompression was successful
if [ $? -ne 0 ]; then
    echo "Failed to extract RIB data."
    exit 1
fi

# Process the RIB data
echo "Processing RIB data with bgpdump..."
bgpdump $EXTRACTED_RIB_FILE > $PROCESSED_RIB

# Check if processing was successful
if [ $? -ne 0 ]; then
    echo "Failed to process RIB data with bgpdump."
    exit 1
fi

rm rib*

echo "RIB data processed and saved to $PROCESSED_RIB"


exit 0