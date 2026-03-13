import json
from pathlib import Path

def merge_huc_metadata(data_root: str, output_filename: str = "all_site_dict.json"):
    root = Path(data_root)
    master_dict = {}

    # Look for all site_dict_discharge.json files in subdirectories
    for json_file in root.glob("*/site_dict_discharge.json"):
        print(f"Processing {json_file}...")
        with open(json_file, 'r') as f:
            data = json.load(f)
            # Assuming the JSON is a dictionary of site info
            master_dict.update(data)

    output_path = root / output_filename
    with open(output_path, 'w') as f:
        json.dump(master_dict, f, indent=4)
    
    print(f"Successfully merged {len(master_dict)} sites into {output_path}")

if __name__ == "__main__":
    merge_huc_metadata("data")
