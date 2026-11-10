# ==============================================================================
# ccdisk_step3.py - De-duplication, Symlink Safety & Live Progress (Python 2.7)
# ==============================================================================
import os
import sys
import stat

def scan_with_deduplication(root_path):
    """
    Scans a directory tree iteratively, tracking inodes to prevent double-counting
    hard links, ignoring symlink targets to prevent infinite loops, and 
    displaying live progress counters.
    """
    assert os.path.exists(root_path), "Error: Root path does not exist."
    assert os.path.isdir(root_path), "Error: Root path must be a directory."

    seen_inodes = set()  # Tracks (st_dev, st_ino) for hard link de-duplication
    scanned_items = []
    queue = [root_path]
    
    total_items_scanned = 0
    total_apparent_bytes = 0
    total_disk_bytes = 0
    
    print("Beginning high-speed iterative scan with hard link de-duplication...")
    
    while len(queue) > 0:
        current_dir = queue.pop(0)
        
        try:
            entries = os.listdir(current_dir)
        except OSError as e:
            sys.stderr.write("WARNING: Cannot read directory {0}: {1}\n".format(current_dir, e))
            continue
            
        for entry in entries:
            full_path = os.path.join(current_dir, entry)
            total_items_scanned += 1
            
            # Live progress indicator every 5 items
            if total_items_scanned % 5 == 0:
                sys.stdout.write("\r[Live Progress] Scanned items: {0} | Apparent: {1} bytes".format(
                    total_items_scanned, total_apparent_bytes
                ))
                sys.stdout.flush()

            is_symlink = os.path.islink(full_path)
            
            try:
                # Use lstat to inspect the link itself, not its target
                st = os.lstat(full_path)
            except OSError as e:
                sys.stderr.write("WARNING: Could not lstat {0}: {1}\n".format(full_path, e))
                continue
                
            is_dir = stat.S_ISDIR(st.st_mode)
            apparent_size = 0
            disk_usage = 0
            
            if not is_dir and not is_symlink:
                apparent_size = st.st_size
                if hasattr(st, 'st_blocks') and st.st_blocks is not None:
                    disk_usage = st.st_blocks * 512
                else:
                    disk_usage = apparent_size
                    
                # Hard link de-duplication check
                # On Windows, st_ino might be 0, so we use dev+ino tuple where supported
                inode_key = (getattr(st, 'st_dev', 0), getattr(st, 'st_ino', 0))
                if inode_key != (0, 0):
                    if inode_key in seen_inodes:
                        # Already counted storage blocks elsewhere; 0 out storage cost
                        disk_usage = 0
                    else:
                        seen_inodes.add(inode_key)
                        
                total_apparent_bytes += apparent_size
                total_disk_bytes += disk_usage
                
            scanned_items.append({
                "path": full_path,
                "is_dir": is_dir,
                "is_link": is_symlink,
                "apparent_size": apparent_size,
                "disk_usage": disk_usage
            })
            
            # If it's a valid directory and NOT a symlink, push to queue
            if is_dir and not is_symlink:
                queue.append(full_path)

    print("\n\nScan Complete.")
    print("Total Items Discovered: {0}".format(len(scanned_items)))
    print("Total Apparent Size: {0} bytes".format(total_apparent_bytes))
    print("Total Unique Disk Usage (Hard links de-duplicated): {0} bytes".format(total_disk_bytes))
    return scanned_items

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_root = os.path.join(script_dir, "testroot")
    
    if os.path.exists(target_root):
        scan_with_deduplication(target_root)
    else:
        print("Error: testroot directory not found. Please run Step 1 setup first.")
