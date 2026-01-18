"""
Merge partial atlas scans into a single file.
"""

import glob
import json


def merge():
    files = glob.glob("atlas_part_*.json")
    combined = []

    print(f"Found {len(files)} partial files.")

    for fpath in files:
        try:
            with open(fpath, "r") as f:
                data = json.load(f)
                combined.extend(data)
                print(f"Loaded {len(data)} items from {fpath}")
        except Exception as e:
            print(f"Error reading {fpath}: {e}")

    print(f"Total points: {len(combined)}")

    with open("atlas_grid.json", "w") as f:
        json.dump(combined, f, indent=2)
    print("Saved to atlas_grid.json")


if __name__ == "__main__":
    merge()
