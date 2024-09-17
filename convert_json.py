import json

def convert_stigmata_format(input_file, output_file):
    with open(input_file, 'r') as f:
        data = json.load(f)

    converted_data = []

    for stigmata_name, stigmata_info in data.items():
        new_entry = {
            "name": stigmata_name,
            "positions": [],
            "images": [],
            "setEffects": {}
        }

        for position, position_info in stigmata_info["positions"].items():
            new_position = {
                "position": position,
                "name": position_info["name"],
                "skillName": position_info["skill_name"],
                "skillDescription": position_info["skill_description"],
                "stats": {
                    "hp": int(position_info["stats"]["HP"]),
                    "atk": int(position_info["stats"]["ATK"]),
                    "def": int(position_info["stats"]["DEF"]),
                    "crt": int(position_info["stats"]["CRT"]),
                    "sp": int(position_info["stats"]["SP"])
                }
            }
            new_entry["positions"].append(new_position)

        for position, image_info in stigmata_info["images"].items():
            if image_info:
                new_image = {
                    "position": position,
                    "iconUrl": image_info.get("icon", ""),
                    "bigUrl": image_info.get("big", "")
                }
                new_entry["images"].append(new_image)

        if stigmata_info.get("set"):
            new_entry["setEffects"] = {
                "setName": stigmata_info["set"]["name"],
                "twoPieceName": stigmata_info["set"]["2_piece"]["name"],
                "twoPieceEffect": stigmata_info["set"]["2_piece"]["effect"],
                "threePieceName": stigmata_info["set"]["3_piece"]["name"],
                "threePieceEffect": stigmata_info["set"]["3_piece"]["effect"]
            }
        else:
            new_entry["setEffects"] = {}

        converted_data.append(new_entry)

    with open(output_file, 'w') as f:
        json.dump(converted_data, f, indent=2)

# Usage
convert_stigmata_format('updated_stigmata_data.json', 'converted_stigmata_data.json')
