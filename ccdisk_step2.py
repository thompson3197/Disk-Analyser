# ==============================================================================
# ccdisk_step2.py - Disk Usage vs. Apparent Size Analyzer (Python 2.7)
# ==============================================================================
import os
import sys
import stat

def get_file_metrics(file_path):
    """
    Retrieves apparent size, actual disk space allocated, and last modified time.
    Safely handles missing or restricted files via assertions and error catching.
    """
    assert isinstance(file_path, str), "Error: file_path must be a string."
    
    apparent_size = 0
    disk_usage = 0
    mtime = 0.0
    is_dir = False
    
    try:
        st = os.lstat(file_path)
        mtime = st.st_mtime
        is_dir = stat.S_ISDIR(st.st_mode)
        
        if not is_dir:
            apparent_size = st.st_size
            # st_blocks * 512 gives actual allocated disk blocks on many Unix-like systems.
            # On Windows, st_blocks may not be populated by default, so we fallback to apparent size.
            if hasattr(st, 'st_blocks') and st.st_blocks is not None:
                disk_usage = st.st_blocks * 512
            else:
                disk_usage = apparent_size
    except OSError as e:
        sys.stderr.write("WARNING: Could not stat {0}: {1}\n".format(file_path, e))
        
    return apparent_size, disk_usage, mtime, is_dir

def scan_disk_metrics(root_path):
    """
    Walks the directory tree iteratively, gathering apparent size, disk usage,
    file counts, modification times, and percentage shares.
    """
    assert os.path.exists(root_path), "Error: Root path does not exist."
    assert os.path.isdir(root_path), "Error: Root path must be a directory."

    items_data = {}
    dir_totals = {}
    queue = [root_path]
    
    # First pass: Collect all paths iteratively
    all_paths = []
    while len(queue) > 0:
        current_dir = queue.pop(0)
        try:
            entries = os.listdir(current_dir)
        except OSError as e:
            sys.stderr.write("WARNING: Cannot read directory {0}: {1}\n".format(current_dir, e))
            continue
            
        for entry in entries:
            full_path = os.path.join(current_dir, entry)
            all_paths.append(full_path)
            if os.path.isdir(full_path) and not os.path.islink(full_path):
                queue.append(full_path)

    # Second pass: Gather metrics for every item
    total_scan_apparent = 0
    total_scan_disk = 0
    
    for path in all_paths:
        app_size, disk_size, mtime, is_dir = get_file_metrics(path)
        items_data[path] = {
            "apparent_size": app_size,
            "disk_usage": disk_size,
            "mtime": mtime,
            "is_dir": is_dir
        }
        if not is_dir:
            total_scan_apparent += app_size
            total_scan_disk += disk_size

    print("Scan completed. Total Apparent Size: {0} bytes, Total Disk Usage: {1} bytes".format(
        total_scan_apparent, total_scan_disk
    ))
    return items_data

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_root = os.path.join(script_dir, "testroot")
    
    if os.path.exists(target_root):
        metrics = scan_disk_metrics(target_root)
    else:
        print("Error: testroot directory not found. Please run Step 1 setup first.")
