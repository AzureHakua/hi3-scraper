# Honkai 3rd Stigmata Tools

## stigmata_scraper.py

The `stigmata_scraper.py` script is a simple tool designed to extract comprehensive information about stigmata from the Honkai Impact 3rd fandom wiki utilizing the `BeautifulSoup4` libraries.

### Features
- Scrapes stigmata information from the Honkai Impact 3rd fandom wiki
- Extracts details such as stigmata names, set effects, individual piece effects, and more
- Organizes data into a structured format for easy analysis and use

### Installation and Usage
1. Install Python 3.x and BeautifulSoup4.
2. Simply run the script using `python stigmata_scraper.py <URL1> <URL2> ...`
3. Note that you can use quotes around the URL to avoid issues with special characters.
    - Example: `python stigmata_scraper.py 'https://honkaiimpact3.fandom.com/wiki/Benares_(Stigma)'`

### Output
The script generates a structured JSON output containing:
- Stigmata set names
- Individual stigmata piece names (Top, Middle, Bottom)
- Stigmata position name, stats, and effects
- Set effects and stats
- The big and icon images of the stigmata

### Disclaimer
This tool is for educational and research purposes only. Please respect the terms of service of the Honkai Impact 3rd fandom wiki when using this scraper.

## scraper-img-dl
Basically an extension of the stigmata scraper that downloads the images of the stigmata from the JSON output. 

### Usage
Place in the same directory as the JSON file, output the images to the output director, which is downloaded_images by default  
`output_dir = 'downloaded_images'`

## reverse_json.py
This script is the next step in the process. Given the directory of images and the JSON file, it will reverse the process and sanitize the image file names and create a new JSON file with the image names based on the directory.

### Usage
1. Move and rename the image directory to the name and location you desire. For example, if you want the images to be labeled under public/images, then place the images in that exact directory.
2. Update `image_dir = 'downloaded_images'` to the proper location. So in this example, `image_dir = 'public/images'`
3. Run the script in the root directory.
```
/--root
    reverse_json.py
    /--public
        /--images
            *images here*
``` 

## convert_json.py
This script is the final step in the process. Given the JSON file, it will convert the JSON file into an altered JSON format that can be used with specific POST requests. In this case, this file is quite specific and custom  designed for my specific use case, but it can be modified to fit your needs.

### Usage
Run this script in the directory with the JSON file you wish to convert. Update the variable with the appropriate files:  
`convert_stigmata_format('updated_stigmata_data.json', 'converted_stigmata_data.json')`