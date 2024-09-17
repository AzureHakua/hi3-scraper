import json
import os
import requests
from urllib.parse import urlparse

def download_image(url, file_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded: {file_path}")
    else:
        print(f"Failed to download: {url}")

def get_file_extension(url):
    path = urlparse(url).path
    return os.path.splitext(path)[1].lower()

def process_equipment(equipment_data, output_dir):
    for item_name, item_data in equipment_data.items():
        if 'images' in item_data:
            for position, image_data in item_data['images'].items():
                for size, url in image_data.items():
                    if url:
                        extension = get_file_extension(url)
                        if not extension:
                            extension = '.png'  # Default to .png if no extension is found
                        file_name = f"{item_name.replace(':', '_')}_{position}_{size}{extension}"
                        file_path = os.path.join(output_dir, file_name)
                        download_image(url, file_path)

def main():
    # Load JSON data
    with open('stigmata_data.json', 'r') as file:
        data = json.load(file)

    # Create output directory
    output_dir = 'downloaded_images'
    os.makedirs(output_dir, exist_ok=True)

    # Process and download images
    process_equipment(data, output_dir)

if __name__ == "__main__":
    main()