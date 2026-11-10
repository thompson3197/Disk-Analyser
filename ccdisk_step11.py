# ==============================================================================
# ccdisk_step11.py - Review Screen & Safety Path Protections (Python 2.7)
# ==============================================================================
import os
import sys

# Protected system paths that must never be staged or removed
PROTECTED_SYSTEM_PATHS = {
    "/",
    "/System",
    "/usr",
    "/bin",
    "/etc",
    "C:\\Windows",
    "C:\\System32",
    "C:\\Program Files"
}

def is_path_protected(target_path):
    """
    Checks if a given path falls under protected system locations.
    """
    abs_target = os.path.abspath(target_path)
    for protected in PROTECTED_SYSTEM_PATHS:
        abs_prot = os.path.abspath(protected)
        if abs_target == abs_prot or abs_target.startswith(abs_prot + os.sep):
            return True
    return False

def validate_staged_item_safety(item_path, scan_root, original_stat_snapshot=None):
    """
    Validates an item right before cleanup confirmation:
    1. Ensures path is within the scan root.
    2. Ensures path is not a protected system path.
    3. Verifies path still exists and hasn't been swapped or altered.
    """
    abs_path = os.path.abspath(item_path)
    abs_root = os.path.abspath(scan_root)
    
    # Check 1: Must be inside scan root
    if not abs_path.startswith(abs_root):
        return False, "Error: Path is outside the active scan root."
        
    # Check 2: Must not be protected
    if is_path_protected(abs_path):
        return False, "Error: Path is a protected system location."
        
    # Check 3: Existence and state validation
    if not os.path.exists(abs_path) and not os.path.islink(abs_path):
        return False, "Error: Item has disappeared from the filesystem."
        
    if original_stat_snapshot is not None:
        try:
            current_st = os.lstat(abs_path)
            # Check if file type changed (e.g., file replaced by directory)
            if current_st.st_mode != original_stat_snapshot.get("st_mode", current_st.st_mode):
                return False, "Error: Item type or mode was swapped since being staged."
        except OSError:
            return False, "Error: Could not stat item during final safety check."
            
    return True, "Passed safety checks."

def run_review_screen(staged_paths, scan_root, stat_snapshots):
    """
    Simulates the interactive review screen. Validates every staged item
    and returns lists of approved items versus skipped items with reasons.
    """
    assert isinstance(staged_paths, (list, set)), "Error: staged_paths must be collection."
    
    approved_items = []
    skipped_items = []
    
    print("\n--- STAGED CLEANUP REVIEW SCREEN ---")
    for path in staged_paths:
        snapshot = stat_snapshots.get(path, None)
        is_safe, reason = validate_staged_item_safety(path, scan_root, snapshot)
        
        if is_safe:
            approved_items.append(path)
            print("[APPROVED] {0}".format(path))
        else:
            skipped_items.append({"path": path, "reason": reason})
            print("[SKIPPED]  {0} -> Reason: {1}".format(path, reason))
            
    print("------------------------------------\n")
    return approved_items, skipped_items

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_root = os.path.join(script_dir, "testroot")
    
    if os.path.exists(target_root):
        print("Testing Review Screen & Safety Barrier Engine...")
        
        # Test protection barrier on /usr or C:\Windows
        test_bad_path = "C:\\Windows"
        if is_path_protected(test_bad_path):
            print("Successfully blocked protected system path: {0}".format(test_bad_path))
            
        # Test review screen validation
        valid_file = os.path.join(target_root, "old", "archive.bin")
        mock_snapshots = {
            valid_file: {"st_mode": os.lstat(valid_file).st_mode if os.path.exists(valid_file) else 0}
        }
        
        approved, skipped = run_review_screen([valid_file, test_bad_path], target_root, mock_snapshots)
        print("Review complete. Approved count: {0}, Skipped count: {1}".format(len(approved), len(skipped)))
    else:
        print("Error: testroot directory not found.")
