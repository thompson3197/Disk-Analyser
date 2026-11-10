# ==============================================================================
# ccdisk_step9.py - Reclaimable Cache & Build Folder Detection (Python 2.7)
# ==============================================================================
import os
import sys

# Define known reclaimable directory names and patterns
RECLAIMABLE_PATTERNS = {
    "node_modules",
    "target",
    "build",
    "dist",
    ".next",
    "__pycache__",
    ".cache",
    "Caches",
    "npm",
    "gradle"
}

def detect_reclaimable_items(scanned_items_dict):
    """
    Scans items to identify well-known cache directories and build output folders.
    Calculates total estimated reclaimable space without modifying the filesystem.
    """
    assert isinstance(scanned_items_dict, dict), "Error: scanned_items_dict must be a dictionary."
    
    reclaimable_found = []
    total_reclaimable_bytes = 0
    
    for path, data in scanned_items_dict.items():
        if not data.get("is_dir", False):
            continue  # Only evaluate directories for cache/build detection
            
        dir_name = os.path.basename(path)
        path_tokens = path.split(os.sep)
        
        # Check if directory name matches known build/cache patterns
        is_match = False
        if dir_name in RECLAIMABLE_PATTERNS:
            is_match = True
        elif ".cache" in path_tokens or "Caches" in path_tokens:
            is_match = True
            
        if is_match:
            disk_usage = data.get("disk_usage", 0)
            apparent_size = data.get("apparent_size", 0)
            
            reclaimable_found.append({
                "path": path,
                "name": dir_name,
                "disk_usage": disk_usage,
                "apparent_size": apparent_size
            })
            total_reclaimable_bytes += disk_usage
            
    return reclaimable_found, total_reclaimable_bytes

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_root = os.path.join(script_dir, "testroot")
    
    if os.path.exists(target_root):
        print("Detecting Reclaimable Cache and Build Folders...")
        
        # Mock scan dataset matching testroot structure
        mock_scan = {
            target_root: {"is_dir": True, "disk_usage": 0},
            os.path.join(target_root, "docs"): {"is_dir": True, "disk_usage": 5242890},
            os.path.join(target_root, "media"): {"is_dir": True, "disk_usage": 52428800},
            os.path.join(target_root, "projects", "webapp", "node_modules"): {"is_dir": True, "disk_usage": 21995520},
            os.path.join(target_root, "projects", "api", "target"): {"is_dir": True, "disk_usage": 3145728},
            os.path.join(target_root, ".cache", "app"): {"is_dir": True, "disk_usage": 10485760},
        }
        
        items, total_bytes = detect_reclaimable_items(mock_scan)
        print("\nReclaimable Candidates Found:")
        for item in items:
            print("  * [RECLAIMABLE] {0} ({1} bytes)".format(item["path"], item["disk_usage"]))
            
        print("\nTotal Estimated Reclaimable Space: {0} bytes ({1:.2f} MB)".format(
            total_bytes, total_bytes / (1024.0 * 1024.0)
        ))
    else:
        print("Error: testroot directory not found.")
