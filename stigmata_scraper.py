import requests
from bs4 import BeautifulSoup
import os
import json
import re
import logging
import sys
from pathlib import Path
from urllib.parse import unquote

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define position order
POSITION_ORDER = {'T': 0, 'M': 1, 'B': 2}

# Download images
def download_image(url, save_path):
    """
    Downloads an image from URL and saves it to the specified path.
    Returns the relative path for JSON storage.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        # Return relative path for JSON
        return os.path.join('public', 'img', 'stigmata', os.path.basename(save_path))
        
    except Exception as e:
        logging.error(f"Failed to download image from {url}: {str(e)}")
        return None


# Converts CSS styles to HTML tags
def convert_css(element):
    # Replace certain tags
    for tag in element.find_all(['a', 'big']):
        tag.unwrap()

    # Get contents of div
    if element.name == 'div':
        contents = element.decode_contents()
        element = BeautifulSoup(contents, 'html.parser')

    for tag in element.find_all(True):
        # Handle indentation with nbsp
        if 'style' in tag.attrs:
            style_str = tag['style']
            if 'padding-left: 3em' in style_str:
                # Add 6 non-breaking spaces for single indent
                tag.insert(0, '\u00A0' * 6)
                del tag['style']
            elif 'padding-left: 6em' in style_str:
                # Add 12 non-breaking spaces for double indent
                tag.insert(0, '\u00A0' * 12)
                del tag['style']
        
        # Handle inc class for blue text using font tag
        if 'class' in tag.attrs:
            classes = tag['class'] if isinstance(tag['class'], list) else tag['class'].split()
            if 'inc' in classes:
                tag.name = 'font'
                tag['color'] = '#00C3FF'
                del tag['class']

        # Remove empty spans
        if tag.name == 'span' and not tag.get('style') and not tag.get('class'):
            tag.unwrap()

    # Convert to string and replace escaped quotes
    result = str(element)
    result = result.replace('\"', '')
    
    return result

# Extracts stigmata data from the given URL
def extract_stigmata_data(url):
    logging.info(f"Fetching URL: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Create JSON structure
    stigmata_data = {
        'name': '',
        'positions': {},
        'images': [],
        'setEffects': {}
    }


    #
    # Extract name
    #
    name_elem = soup.select_one('h1.page-header__title')
    if name_elem:
        # Removes redundant "(Stigmata)" or "(Stigma)" from the name
        stigmata_data['name'] = name_elem.text.strip().replace(' (Stigmata)', '').replace(' (Stigma)', '')
        logging.info(f"Extracted name: {stigmata_data['name']}")


    #
    # Extract stigmata information, starting at Lv 50
    #
    max_elem = soup.find('b', string='Lv 50')
    if not max_elem:
        # If level 50 data doesn't exist, try to find level 35 data
        max_elem = soup.find('b', string='Lv 35')
        
        if not max_elem:
            # If level 35 data doesn't exist, try to find level 25 data
            max_elem = soup.find('b', string='Lv 25')

            if not max_elem:
                # If level 25 data doesn't exist, try to find level 15 data
                max_elem = soup.find('b', string='Lv 15')

    # Found max level stigmata, beginning extraction
    if max_elem:
        # Div containing stigmata data (more than 1)
        content_div = max_elem.find_next('div', class_='mw-collapsible-content')
        position_data = []

        if content_div:
            # Div containing a single stigma (T, M, or B)
            positions = content_div.find_all('div', class_='stigmata-entry-10padding')

            for pos_div in positions:
                pos_name = pos_div.find('b', string=re.compile(r'\([TMB]\)')).text[-2]
                piece_name = pos_div.find('b', string=re.compile(r'\([TMB]\)')).text.strip()
                logging.info(f'Extracted position: {pos_name} - {piece_name}')
                stats = {}

                for stat_div in pos_div.find_next('div', class_='stigmata-entry-info-stats'):
                    stat_name = stat_div.select_one('div', class_='color-blue').text.strip().lower()
                    stat_value = int(stat_div.select_one('b').text.strip())
                    stats[stat_name] = stat_value

                skill_name_elem = pos_div.find_next('div', class_='stigmata-entry-skill-name')
                if skill_name_elem:
                    skill_name = skill_name_elem.text.strip()
                    skill_description = convert_css(skill_name_elem.find_next_sibling('div'))
                else:
                    skill_name = ""
                    skill_description = ""

                # Create position entry
                position_data.append({
                    'position': pos_name,
                    'name': piece_name.replace(' (Stigmata)', ''),
                    'skillName': skill_name,
                    'skillDescription': skill_description,
                    'stats': stats
                })

                logging.info(f"Extracted data for position {pos_name}")

            position_data.sort(key=lambda x: POSITION_ORDER[x['position']])
            stigmata_data['positions'] = position_data


    #
    # Extract images
    #
    img_name = stigmata_data['name'].split(':')[0].strip().split()[0].replace('"', '')
    images = soup.select(f'img[alt*="{img_name}"]')
    image_data = []
    seen_urls = set()

    for img in images:
        if 'data-src' in img.attrs and 'small' not in img['alt'].lower() and 'back' not in img['alt'].lower():
            url = img['data-src']

            if url in seen_urls:
                continue

            if '%28T%29' in url:
                pos = 'T'
            elif '%28M%29' in url:
                pos = 'M'
            elif '%28B%29' in url:
                pos = 'B'
            else:
                continue
            
            seen_urls.add(url)
            # Create filename from stigmata name and position
            safe_name = re.sub(r'[^\w\-_]', '_', stigmata_data['name'])
            filename = f"{safe_name}_{pos}.png"
            save_path = os.path.join('public', 'img', 'stigmata', filename)
            
            # Download image and get relative path
            relative_path = download_image(url, save_path)
            if relative_path:
                image_data.append({
                    "position": pos,
                    "imgUrl": relative_path
                })

    # Sort using the same position_order as positions
    image_data.sort(key=lambda x: POSITION_ORDER[x['position']])
    stigmata_data['images'] = image_data
    logging.info(f"Extracted {len(stigmata_data['images'])} unique image URLs")


    #
    # Extract set information
    #
    set_elem = soup.find('b', string=lambda text: text and text.strip() + ' set' in soup.text)
    if set_elem:
        set_name = set_elem.text.strip().replace(' (Stigmata)', '')
        stigmata_data['setEffects']['setName'] = set_name
        logging.info(f"Extracted set name: {set_name}")

        # Extract 2-piece effect
        twoPiece_elem = soup.find('b', string=lambda text: text and '2-pieces effect ' + text.strip() in soup.text)
        if twoPiece_elem:
            twoPieceName = twoPiece_elem.text.strip()
            stigmata_data['setEffects']['twoPieceName'] = twoPieceName
            logging.info(f"Extracted 2-piece effect name: {twoPieceName}")

            twoEffect_elem = twoPiece_elem.find_parent('div').find_next('div')
            stigmata_data['setEffects']['twoPieceEffect'] = convert_css(twoEffect_elem)

        # Extract 3-piece effect
        threePiece_elem = soup.find('b', string=lambda text: text and '3-pieces effect ' + text.strip() in soup.text)
        if threePiece_elem:
            threePieceName = threePiece_elem.text.strip()
            stigmata_data['setEffects']['threePieceName'] = threePieceName
            logging.info(f"Extracted 3-piece effect name: {threePieceName}")

            threeEffect_elem = threePiece_elem.find_parent('div').find_next('div')
            stigmata_data['setEffects']['threePieceEffect'] = convert_css(threeEffect_elem)

        logging.info(f"Extracted set effects: 2-piece and 3-piece")

    # Finished extraction, return data
    return stigmata_data



def main():
    if len(sys.argv) < 2:
        print("Usage: python stigmata_scraper.py <URL1> <URL2> ...")
        sys.exit(1)

    urls = sys.argv[1:]
    json_file = 'stigmata_data.json'

    os.makedirs(os.path.join('public', 'img', 'stigmata'), exist_ok=True)

    # Load existing data if file exists
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            all_stigmata_data = json.load(f)
    else:
        all_stigmata_data = []
    
    for url in urls:
        stigmata_data = extract_stigmata_data(url)

        # Find existing entry by name if it exists
        existing_entry = next(
            (item for item in all_stigmata_data if item['name'] == stigmata_data['name']), 
            None
        )
    
        if existing_entry:
            existing_entry.update(stigmata_data)
        else:
            all_stigmata_data.append(stigmata_data)

    # Sort the list alphabetically by name
    sorted_stigmata_data = sorted(all_stigmata_data, key=lambda x: x['name'].lower())

    # Write updated data back to file
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_stigmata_data, f, ensure_ascii=False, indent=2)
    
    logging.info(f"Extracted and merged data for {len(urls)} stigmata and saved to {json_file}")

if __name__ == "__main__":
    main()