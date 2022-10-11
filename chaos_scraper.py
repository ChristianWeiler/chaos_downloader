#!/usr/bin/env python3

import requests
import zipfile
import io
import json
from pathlib import Path
import sys
import argparse

# json file containing public program information
CHAOS_URL = "https://chaos-data.projectdiscovery.io/index.json"

# returns a list of publically avaialbe programs to scrape
def get_programs():
    return requests.get(url=CHAOS_URL).json()

# downloads program zip file to program directory and extracts it
def download_zip(program, url, download_dir):                    
    r = requests.get(url, stream=True)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(download_dir)

# check if .last_updated exists if program directory
# returns true if up-to-date or false if not
def is_up_to_date(last_updated, chaos_last_updated):    
    if last_updated.exists() == True:
        with last_updated.open('r') as f:
            last_updated_file = f.read()
            return (chaos_last_updated == last_updated_file)

    return False

# takes a file path and prints out the subdomain
# Ex: input: /tmp/.downloads/program/mysubdomain.com.txt output: mysubdomain.com
def print_subdomain_from_path(subdomains):
    for i in subdomains:
        i = str(i).split('/')[-1]
        i = i.split('.txt')[0]
        print(i)
    
def main():

    example_usage_text = """
    Example:
    python3 chaos_downloader.py --list-programs
        4chan
        84codes
        8x8
        Achmea
        ...
    python3 chaos_downloader.py --program dod --list-subdomains
        health.mil
        cac.mil
        eucom.mil
        dren.mil
        ...
    python3 chaos_downloader.py --program dod --subdomain health.mil,cac.mil,...
        dha-101-.health.mil
        dha-94-.health.mil
        cpe-198-255-.health.mil
        dha-227-.health.mil
        ...
    """

    parser = argparse.ArgumentParser(description='Download public subdomain information from chaos.projectdiscovery.com',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog = example_usage_text)
    parser.add_argument('--program','-p',help='Specify the program name to download data for.', required=False, type=str)
    parser.add_argument('--subdomain','-d',help='Restrict results to specific subdomains from a specified program. Accepts multiple subdomains separated by commas. Ex: subdomain1.com,subdomain2.com,...', required=False, type=str)
    parser.add_argument('--list-programs','-l',help='List all of the public programs available to download data for and exits.', required=False, action='store_true')
    parser.add_argument('--list-subdomains','-s',help='List all of the subdomains available in a specified program and exits.', required=False, action='store_true')
    parser.add_argument('--outfile','-o',help='Write subdomain results to specified outfile.', required=False, type=str)
    parser.add_argument('--silent','-n',help='Don\'t print any output to terminal.', required=False, action='store_true')
    parser.add_argument('--verbose','-v',help='Print extra information.', required=False, action='store_true')
    parser.add_argument('--force','-f',help='Ignore last_updated value and force redownload of program data.', required=False, action='store_true')
    args = parser.parse_args()

    # Setup arguments and program data
    program_data = get_programs()
    is_verbos = args.verbose
    is_silent = args.silent        

    # if --list flag is set, print a list of programs and exit
    if args.list_programs == True:
        for p in program_data:
            print(p['name'])
        sys.exit(0)

    # check if --program name is specified
    # if there is a program that matches, download data
    if args.program is not None:
        if is_verbos:
            print(f"[*] Searching for program {args.program} ...")
        
        for p in program_data:
            program_name = p['name'].lower().replace(" ", "_")

            if args.program.lower() not in program_name :
                continue

            if is_verbos:
                print(f"[+] Found program: {p['name']}")
                print(f"[*] Program project chaos data was last updated: {p['last_updated']}")

            # Set the program directory to download the zip to    
            download_dir = Path.cwd() / ".downloads" / program_name
            
            # if program doesn't already have a folder, create it
            if download_dir.is_dir() == False:
                if is_verbos:
                    print("[*] Program directory doesn't exist, creating new directory at %s", str(download_dir))
                download_dir.mkdir(parents=True)

            last_updated = download_dir / ".last_updated"

            # only download program data if it is not already up-to-date, unless --force flag was used
            if not is_up_to_date(last_updated, p['last_updated']) or args.force:
                if is_verbos:
                    print("[*] Program is not already up-to-date, downloading data ...")

                # download and unzip program data to program directory
                download_zip(program_name, p['URL'], download_dir)
                
                # update .last_updated file value
                with last_updated.open('w') as f:
                    f.write(p['last_updated'])

            # get a list of all program subdomains from the .txt file names in the program directory
            subdomain_files_all = list(download_dir.glob('*.txt'))

            # if --list-subdomains was used, print the program subdomains and exit
            if args.list_subdomains == True:
                print_subdomain_from_path(subdomain_files_all)
                sys.exit(0)

            # if the --subdomain flag is set, only get the results from the specific subdomain
            # else get all the subdomains
            if args.subdomain is not None:
                subdomain_args = args.subdomain.split(",")

                subdomain_text = ""
                for sub in subdomain_args:
                    subdomain_file = sub + ".txt"
                    subdomain_file = download_dir / subdomain_file
                    
                    with subdomain_file.open('r') as f:
                        subdomain_text += f.read()
                
                if is_silent == False:
                    print(subdomain_text)

                if args.outfile is not None:
                    with open(args.outfile, 'w') as f:
                        f.write(subdomain_text)

            else:
                subdomain_text = ""
                for sub in subdomain_files_all:
                    sub = download_dir / sub
                                
                    with sub.open('r') as f:
                        subdomain_text += f.read()

                if is_silent == False:
                    print(subdomain_text)

                if args.outfile is not None:
                    with open(args.outfile, 'w') as f:
                        f.write(subdomain_text)
                   

if __name__ == "__main__":
    main()
