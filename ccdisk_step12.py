# ==============================================================================
# ccdisk_step12.py - Safe OS Trash Migration & Post-Cleanup Rescan (Python 2.7)
# ==============================================================================
import os
import sys
import shutil
import stat

def move_to_trash_safely(item_path):
    """
    Moves an item to the operating system's recoverable Trash location.
    Returns (success: bool, destination_or_error: str).
    """
    assert os.path.exists(item_path) or os.path.islink(item_path), "Error: Path does not exist."
    abs_path = os.path.abspath(item_path)
    
    try:
        # Determine platform-appropriate trash directory
        home = os.path.expanduser("~")
        if sys.platform == "win32":
            trash_dir = os.path.join(os.path.dirname(abs_path), "..", ".Trash")
        elif sys.platform == "darwin":
            trash_dir = os.path.join(home, ".Trash")
        else:
            trash_dir = os.path.join(home, ".local", "share", "Trash", "files")
            
        if not os.path.exists(trash_dir):
            os.makedirs(trash_dir)
            
        dest_path = os.path.join(trash_dir, os.path.basename(abs_path))
        
        # Handle naming collisions in trash
        base, ext = os.path.splitext(dest_path)
        counter = 1
        while os.path.exists(dest_path):
            dest_path = "{0}_{1}{2}".format(base, counter, ext)
            counter += 1
            
        shutil.move(abs_path, dest_path)
        return True, dest_path
    except OSError as e:
        return False, str(e)

def execute_cleanup_and_rescan(approved_paths, scan_root):
    """
    Executes safe trash migration for approved items, reports failures without
    counting them as reclaimed, and performs a post-cleanup rescan summary.
    """
    assert isinstance(approved_paths, list), "Error: approved_paths must be a list."
    
    successfully_trashed = []
    failed_items = []
    actual_reclaimed_bytes = 0
    
    print("\n--- EXECUTING SAFE CLEANUP & TRASH MIGRATION ---")
    for path in approved_paths:
        if not os.path.exists(path) and not os.path.islink(path):
            print("[SKIP] Item already removed or missing: {0}".format(path))
            continue
            
        # Get disk size before moving
        try:
            st = os.lstat(path)
            size = st.st_size if not stat.S_ISDIR(st.st_mode) else 0
        except OSError:
            size = 0
            
        success, result = move_to_trash_safely(path)
        if success:
            successfully_trashed.append({"path": path, "trash_loc": result})
            actual_reclaimed_bytes += size
            print("[SUCCESS] Moved to Trash: {0} -> {1}".format(path, result))
        else:
            failed_items.append({"path": path, "reason": result})
            print("[FAILED] Could not move {0} to Trash: {1}".format(path, result))
            
    print("--------------------------------------------------\n")
    
    # Post-cleanup rescan summary
    print("Post-Cleanup Rescan Report:")
    print("  - Successfully Moved to Trash: {0} items".format(len(successfully_trashed)))
    print("  - Failed / Skipped Items: {0} items".format(len(failed_items)))
    print("  - Estimated Reclaimed Space: {0} bytes".format(actual_reclaimed_bytes))
    print("  Note: On most systems, space in Trash is only freed upon emptying the Trash bin.")
    
    return successfully_trashed, failed_items, actual_reclaimed_bytes

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_root = os.path.join(script_dir, "testroot")
    
    if os.path.exists(target_root):
        print("Testing Step 12: Safe Trash Migration & Rescan...")
        test_file = os.path.join(target_root, "old", "archive.bin")
        if os.path.exists(test_file):
            execute_cleanup_and_rescan([test_file], target_root)
        else:
            print("Test file 'old/archive.bin' not found.")
    else:
        print("Error: testroot directory not found.")
