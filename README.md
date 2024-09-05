# Honkai 3rd Stigmata Scraper

## Overview

The `stigmata_scraper.py` script is a simple tool designed to extract comprehensive information about stigmata from the Honkai Impact 3rd fandom wiki utilizing the `BeautifulSoup4` libraries.

## Features

- Scrapes stigmata information from the Honkai Impact 3rd fandom wiki
- Extracts details such as stigmata names, set effects, individual piece effects, and more
- Organizes data into a structured format for easy analysis and use

## Installation and Usage

1. Install Python 3.x and BeautifulSoup4.
2. Simply run the script using `python stigmata_scraper.py <URL1> <URL2> ...`
3. Note that you can use quotes around the URL to avoid issues with special characters.
    - Example: `python stigmata_scraper.py 'https://honkaiimpact3.fandom.com/wiki/Benares_(Stigma)'`

## Output

The script generates a structured JSON output containing:
- Stigmata set names
- Individual stigmata piece names (Top, Middle, Bottom)
- Stigmata position name, stats, and effects
- Set effects and stats
- The big and icon images of the stigmata

## Disclaimer

This tool is for educational and research purposes only. Please respect the terms of service of the Honkai Impact 3rd fandom wiki when using this scraper.