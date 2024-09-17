import json
import os
import re

def sanitize_filename(filename):
    # Remove special characters and replace spaces with underscores
    sanitized = re.sub(r'[^\w\-_\. ]', '', filename)
    sanitized = sanitized.replace(' ', '_')
    return sanitized

def rename_files_in_directory(directory):
    for filename in os.listdir(directory):
        old_path = os.path.join(directory, filename)
        new_filename = sanitize_filename(filename)
        new_path = os.path.join(directory, new_filename)
        os.rename(old_path, new_path)

def update_image_paths(data, image_dir):
    for item_name, item_data in data.items():
        if 'images' in item_data:
            for position, image_data in item_data['images'].items():
                for size in ['icon', 'big']:
                    if size in image_data:
                        old_file_name = f"{item_name.replace(':', '_')}_{position}_{size}.png"
                        new_file_name = sanitize_filename(old_file_name)
                        old_path = os.path.join(image_dir, old_file_name)
                        new_path = os.path.join(image_dir, new_file_name)
                        
                        if os.path.exists(old_path):
                            os.rename(old_path, new_path)
                            image_data[size] = new_path
                        elif os.path.exists(new_path):
                            image_data[size] = new_path
                        else:
                            print(f"Warning: {old_path} not found")

def main():
    # Load JSON data
    with open('stigmata_data.json', 'r') as file:
        data = json.load(file)

    # Rename files in the directory
    image_dir = 'downloaded_images'
    rename_files_in_directory(image_dir)

    # Update image paths
    update_image_paths(data, image_dir)

    # Save updated JSON
    with open('updated_stigmata_data.json', 'w') as file:
        json.dump(data, file, indent=2)

if __name__ == "__main__":
    main()
