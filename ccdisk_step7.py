# ==============================================================================
# ccdisk_step7.py - File Modification Age Bands & Color Coding (Python 2.7)
# ==============================================================================
import os
import sys
import time

# Define age band thresholds in seconds
SECONDS_IN_MONTH = 30 * 24 * 60 * 60
SECONDS_IN_YEAR = 365 * 24 * 60 * 60

def classify_age(mtime, current_time=None):
    """
    Classifies a modification timestamp into discrete age bands:
    - 'recent': < 1 month
    - 'moderate': 1 month to 1 year
    - 'old': > 1 year
    """
    if current_time is None:
        current_time = time.time()
        
    age_seconds = current_time - mtime
    
    if age_seconds < SECONDS_IN_MONTH:
        return "recent", "#2ecc71" # Green
    elif age_seconds < SECONDS_IN_YEAR:
        return "moderate", "#f1c40f" # Yellow
    else:
        return "old", "#e74c3c" # Red

def calculate_tree_ages(scanned_items_dict, current_time=None):
    """
    Calculates age categories for all files and propagates directory ages
    based on their most recently modified descendant.
    """
    if current_time is None:
        current_time = time.time()
        
    classified_items = {}
    
    # First pass: classify direct files and initialize directories with their own mtime
    for path, data in scanned_items_dict.items():
        mtime = data.get("mtime", current_time)
        is_dir = data.get("is_dir", False)
        
        band, color = classify_age(mtime, current_time)
        classified_items[path] = {
            "mtime": mtime,
            "is_dir": is_dir,
            "age_band": band,
            "color": color
        }
        
    # Second pass: propagate directory ages upwards based on newest descendants
    # Sorting paths by length descending ensures deepest children update parents first
    sorted_paths = sorted(scanned_items_dict.keys(), key=len, reverse=True)
    
    for path in sorted_paths:
        if scanned_items_dict[path].get("is_dir", False):
            dir_mtime = classified_items[path]["mtime"]
            
            # Find all immediate or nested descendants
            for child_path, child_data in classified_items.items():
                if child_path != path and child_path.startswith(path + os.sep):
                    if child_data["mtime"] > dir_mtime:
                        dir_mtime = child_data["mtime"]
                        
            band, color = classify_age(dir_mtime, current_time)
            classified_items[path]["mtime"] = dir_mtime
            classified_items[path]["age_band"] = band
            classified_items[path]["color"] = color

    return classified_items

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_root = os.path.join(script_dir, "testroot")
    
    if os.path.exists(target_root):
        print("Running age classification on testroot...")
        # Mock metrics dataset representing testroot contents
        mock_data = {
            target_root: {"is_dir": True, "mtime": time.time()},
            os.path.join(target_root, "old"): {"is_dir": True, "mtime": time.time() - (750 * 24 * 60 * 60)},
            os.path.join(target_root, "old", "archive.bin"): {"is_dir": False, "mtime": time.time() - (750 * 24 * 60 * 60)},
            os.path.join(target_root, "docs"): {"is_dir": True, "mtime": time.time() - 1000},
            os.path.join(target_root, "docs", "notes.txt"): {"is_dir": False, "mtime": time.time() - 1000},
        }
        
        results = calculate_tree_ages(mock_data)
        for p, info in results.items():
            print("  - {0} | Band: {1} | Color: {2}".format(os.path.basename(p) or p, info["age_band"], info["color"]))
    else:
        print("Error: testroot directory not found.")
