# Chaos Downloader
## Description
Script for searching and download public subdomain data from [Project Discovery Chaos](https://chaos.projectdiscovery.io/#/).

## Usage

```
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
```
