#!/usr/bin/env python3

# https://chaos-data.projectdiscovery.io/index.json

import requests
import zipfile
import io
import json
from pathlib import Path
import sys
import argparse

# Get the cwd
script_path = Path.cwd()

def is_up_to_date(target_path, last):
    last_update = target_path / 'last_updated'
    
    # check if last_updated.txt exists
    # if true, open and compare strings
    if last_update.exists() != False:
        with last_update.open('r') as f:
            last_updated_file = f.read()
            # return true if strings match
            if last == last_updated_file:
                return True
            return False 
    else:
        # create last_updated.txt file with current value
        with last_update.open('w') as f:
            f.write(last)

    return False

# Download program zip file and extract it to the target directory
def download_zip(target_path, url):
    r = requests.get(url, stream=True)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(target_path)

def print_files(target_path):
    
    subdomains = ""

    # create a list of .txt files extracted from zip
    for i in list(target_path.glob('*.txt')):
        temp = target_path / i
        
        # open txt file, read and store contents
        with temp.open('r') as f:
            subdomains += f.read()

    # print subdomains in txt files
    print(subdomains)


def urlparser(target):
    # Get the index.json file which contains the download urls and parse it
    index_parsed = requests.get(url='https://chaos-data.projectdiscovery.io/index.json').json()

    # loop through parsed index.json
    for i in index_parsed:
        # replace spaces with underscores
        target_name = i['name'].lower().replace(" ", "_")
       
        # check if you get a match for target name
        if target.lower() in target_name:
           
            # change directories and check if directory exists
            target_path = script_path / target_name
           
            if target_path.is_dir() != True:
                target_path.mkdir()

            # check if file is already up-to-date
            if is_up_to_date(target_path, i['last_updated']):
                return
                    
            # Download zip if not up-to-date
            download_zip(target_path, i['URL'])

            print_files(target_path)

    return


def main():
    parser = argparse.ArgumentParser(description='Search public subdomain informaiton on chaos.projectdiscovery.com')
    parser.add_argument('program', type=str)
    args = parser.parse_args()

    urlparser(args.program)

if __name__ == "__main__":
    main()
