# ==============================================================================
# ccdisk_step6.py - Item Inspector & Largest Children Ranking (Python 2.7)
# ==============================================================================
import os
import sys
import stat
import time

def inspect_item(item_path, parent_size=0):
    """
    Gathers detailed metrics for a selected item: full path, disk usage,
    apparent size, modification time, file count (if directory), and percentage share.
    """
    assert os.path.exists(item_path), "Error: Item path does not exist."
    
    abs_path = os.path.abspath(item_path)
    is_dir = os.path.isdir(abs_path)
    
    apparent_size = 0
    disk_usage = 0
    mtime = 0.0
    file_count = 0
    
    try:
        st = os.lstat(abs_path)
        mtime = st.st_mtime
        if not is_dir:
            apparent_size = st.st_size
            disk_usage = st.st_blocks * 512 if hasattr(st, 'st_blocks') and st.st_blocks is not None else apparent_size
        else:
            # Count immediate children entries
            file_count = len(os.listdir(abs_path))
    except OSError as e:
        sys.stderr.write("WARNING: Could not inspect {0}: {1}\n".format(abs_path, e))

    # Calculate percentage share of parent container if parent_size > 0
    pct_share = 0.0
    if parent_size > 0:
        target_size = disk_usage if not is_dir else apparent_size
        pct_share = (float(target_size) / parent_size) * 100.0

    formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))

    return {
        "path": abs_path,
        "is_dir": is_dir,
        "apparent_size": apparent_size,
        "disk_usage": disk_usage,
        "mtime_formatted": formatted_time,
        "file_count": file_count if is_dir else 1,
        "percentage_share": pct_share
    }

def get_largest_children(dir_path, items_metric_cache, limit=5):
    """
    Lists immediate children of a directory ordered by disk usage descending.
    """
    assert os.path.isdir(dir_path), "Error: Path must be a directory."
    
    try:
        entries = os.listdir(dir_path)
    except OSError as e:
        sys.stderr.write("WARNING: Cannot list directory {0}: {1}\n".format(dir_path, e))
        return []

    children_metrics = []
    for entry in entries:
        child_path = os.path.join(dir_path, entry)
        if child_path in items_metric_cache:
            m = items_metric_cache[child_path]
            children_metrics.append({
                "path": child_path,
                "name": entry,
                "disk_usage": m.get("disk_usage", 0),
                "apparent_size": m.get("apparent_size", 0)
            })
        else:
            try:
                st = os.lstat(child_path)
                size = st.st_size if not os.path.isdir(child_path) else 0
                children_metrics.append({
                    "path": child_path,
                    "name": entry,
                    "disk_usage": size,
                    "apparent_size": size
                })
            except OSError:
                continue

    # Sort descending by disk usage
    sorted_children = sorted(children_metrics, key=lambda x: x["disk_usage"], reverse=True)
    return sorted_children[:limit]

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_root = os.path.join(script_dir, "testroot")
    media_dir = os.path.join(target_root, "media")
    
    if os.path.exists(media_dir):
        print("Inspecting directory: {0}".format(media_dir))
        media_info = inspect_item(media_dir, parent_size=100000000)
        print("  - Path: {0}".format(media_info["path"]))
        print("  - File Count: {0}".format(media_info["file_count"]))
        print("  - Modified: {0}".format(media_info["mtime_formatted"]))
        
        print("\nLargest Children in media/:")
        mock_cache = {
            os.path.join(media_dir, "video.bin"): {"disk_usage": 41943040, "apparent_size": 41943040},
            os.path.join(media_dir, "photo1.bin"): {"disk_usage": 8388608, "apparent_size": 8388608},
            os.path.join(media_dir, "photo2.bin"): {"disk_usage": 2097152, "apparent_size": 2097152},
        }
        top_children = get_largest_children(media_dir, mock_cache)
        for c in top_children:
            print("  * {0} ({1} bytes)".format(c["name"], c["disk_usage"]))
    else:
        print("Error: testroot/media directory not found.")
