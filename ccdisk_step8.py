# ==============================================================================
# ccdisk_step8.py - Ranked File List & Size/Age Filtering (Python 2.7)
# ==============================================================================
import os
import sys
import time

def get_ranked_files(scan_items_dict, scope_path=None, min_size_bytes=0, min_age_seconds=0):
    """
    Returns a ranked list of files ordered by disk usage descending,
    filtered by optional scope path, minimum size threshold, and minimum age.
    """
    assert isinstance(scan_items_dict, dict), "Error: scan_items_dict must be a dictionary."
    
    current_time = time.time()
    ranked_candidates = []
    
    # Normalize scope path for prefix matching
    abs_scope = os.path.abspath(scope_path) if scope_path else None
    
    for path, data in scan_items_dict.items():
        if data.get("is_dir", False) or data.get("is_link", False):
            continue  # Only rank actual files
            
        abs_path = os.path.abspath(path)
        
        # Check if path falls within scope if scope is specified
        if abs_scope and not abs_path.startswith(abs_scope):
            continue
            
        disk_usage = data.get("disk_usage", 0)
        apparent_size = data.get("apparent_size", 0)
        mtime = data.get("mtime", current_time)
        age_seconds = current_time - mtime
        
        # Apply size filter
        if disk_usage < min_size_bytes:
            continue
            
        # Apply age filter
        if age_seconds < min_age_seconds:
            continue
            
        ranked_candidates.append({
            "path": abs_path,
            "name": os.path.basename(abs_path),
            "disk_usage": disk_usage,
            "apparent_size": apparent_size,
            "mtime": mtime,
            "age_days": age_seconds / (24 * 60 * 60)
        })
        
    # Sort descending by actual disk usage
    sorted_ranking = sorted(ranked_candidates, key=lambda x: x["disk_usage"], reverse=True)
    return sorted_ranking

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_root = os.path.join(script_dir, "testroot")
    
    if os.path.exists(target_root):
        print("Testing Ranked File Engine with Filters...")
        
        # Mock dataset matching testroot files
        current_t = time.time()
        year_in_secs = 365 * 24 * 60 * 60
        
        mock_scan = {
            os.path.join(target_root, "media", "video.bin"): {"is_dir": False, "disk_usage": 41943040, "apparent_size": 41943040, "mtime": current_t - 1000},
            os.path.join(target_root, "old", "archive.bin"): {"is_dir": False, "disk_usage": 15728640, "apparent_size": 15728640, "mtime": current_t - (2 * year_in_secs)},
            os.path.join(target_root, "sparse.img"): {"is_dir": False, "disk_usage": 0, "apparent_size": 1073741824, "mtime": current_t - 500},
        }
        
        # Filter: files >= 10 MB and older than 1 year
        filtered_files = get_ranked_files(
            mock_scan, 
            scope_path=target_root, 
            min_size_bytes=10 * 1024 * 1024, 
            min_age_seconds=year_in_secs
        )
        
        print("\nFiltered Results (Min Size: 10MB, Min Age: 1 Year):")
        for f in filtered_files:
            print("  * {0} | Disk Usage: {1} bytes | Age: {2:.1f} years".format(
                f["name"], f["disk_usage"], f["age_days"] / 365.0
            ))
    else:
        print("Error: testroot directory not found.")
