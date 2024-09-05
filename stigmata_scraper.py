import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
import os
import json
import re
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_stigmata_data(url):
    logging.info(f"Fetching URL: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    stigmata_data = {
        'name': '',
        'positions': {},
        'set': {},
        'images': []
    }
    
    # Extract name
    name_elem = soup.select_one('h1.page-header__title')
    if name_elem:
        stigmata_data['name'] = name_elem.text.strip().replace(' (Stigmata)', '').replace(' (Stigma)', '')
        logging.info(f"Extracted name: {stigmata_data['name']}")
    
    # Extract images
    first_word = stigmata_data['name'].split(':')[0].strip().split()[0].replace('"', '')
    images = soup.select(f'img[alt*="{first_word}"]')
    image_data = {}

    for img in images:
        if 'data-src' in img.attrs and 'small' not in img['alt'].lower() and 'back' not in img['alt'].lower():
            url = img['data-src']
            if '%28T%29' in url:
                pos = 'T'
            elif '%28M%29' in url:
                pos = 'M'
            elif '%28B%29' in url:
                pos = 'B'
            else:
                continue

            if pos not in image_data:
                image_data[pos] = {}

            if '(Icon)' in img['alt']:
                image_data[pos]['icon'] = url
            else:
                image_data[pos]['big'] = url

    stigmata_data['images'] = image_data
    logging.info(f"Extracted {len(stigmata_data['images'])} unique image URLs")

    # Extract level 50 data for each position
    max_elem = soup.find('b', string='Lv 50')
    if not max_elem:
        # If level 50 data doesn't exist, try to find level 35 data
        max_elem = soup.find('b', string='Lv 35')
        
        if not max_elem:
            # If level 35 data doesn't exist, try to find level 25 data
            max_elem = soup.find('b', string='Lv 25')

    if max_elem:
        content_div = max_elem.find_next('div', class_='mw-collapsible-content')
        if content_div:
            positions = content_div.find_all('div', class_='infobox-solid')
            for pos_div in positions:
                pos_name = pos_div.find('b', string=re.compile(r'\([TMB]\)')).text[-2]
                piece_name = pos_div.find('b', string=re.compile(r'\([TMB]\)')).text.strip()
                
                stats = {}
                for stat_div in pos_div.select('div[style*="display: flex; gap: 5px; padding: 0 5px;"]'):
                    stat_name = stat_div.select_one('span.color-blue').text.strip()
                    stat_value = stat_div.select_one('b').text.strip()
                    stats[stat_name] = stat_value
                
                skill_name_elem = pos_div.select_one('div[style*="font-style: italic"]')
                if skill_name_elem:
                    skill_name = skill_name_elem.text.strip()
                    skill_description = skill_name_elem.find_next_sibling('div').text.strip()
                else:
                    skill_name = ""
                    skill_description = ""
                
                stigmata_data['positions'][pos_name] = {
                    'name': piece_name.replace(' (Stigmata)', ''),
                    'stats': stats,
                    'skill_name': skill_name,
                    'skill_description': skill_description
                }
                logging.info(f"Extracted data for position {pos_name}")
    
    # Extract set information
    set_elem = soup.find('b', string=lambda text: text and text.strip() + ' set' in soup.text)
    if set_elem:
        set_name = set_elem.text.strip().replace(' (Stigmata)', '')
        stigmata_data['set']['name'] = set_name
        logging.info(f"Extracted set name: {set_name}")
        
        set_effects = soup.find_all('div', class_='infobox-solid')
        for effect in set_effects:
            effect_header = effect.find('div', style=lambda s: s and 'font-style: italic' in s)
            if effect_header:
                pieces = '3_piece' if '3-pieces effect' in effect_header.text else '2_piece'
                effect_name = effect_header.find('b').text.strip()
                effect_div = effect.find('div', style='padding: 0 5px;')
                if effect_div:
                    stigmata_data['set'][pieces] = {
                        'name': effect_name,
                        'effect': effect_div.text.strip()
                    }
        logging.info(f"Extracted set effects: 2-piece and 3-piece")
    
    return stigmata_data

def main():
    if len(sys.argv) < 2:
        print("Usage: python stigmata_scraper.py <URL1> <URL2> ...")
        sys.exit(1)

    urls = sys.argv[1:]
    json_file = 'stigmata_data.json'

    # Load existing data if file exists
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            all_stigmata_data = json.load(f)
    else:
        all_stigmata_data = {}
    
    for url in urls:
        stigmata_data = extract_stigmata_data(url)
        
        # Merge new data with existing data
        if stigmata_data['name'] in all_stigmata_data:
            all_stigmata_data[stigmata_data['name']].update(stigmata_data)
        else:
            all_stigmata_data[stigmata_data['name']] = stigmata_data
    
    # Sort the data alphabetically
    sorted_stigmata_data = dict(sorted(all_stigmata_data.items()))
    
    # Write updated data back to file
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_stigmata_data, f, ensure_ascii=False, indent=2)
    
    logging.info(f"Extracted and merged data for {len(urls)} stigmata and saved to {json_file}")

if __name__ == "__main__":
    main()