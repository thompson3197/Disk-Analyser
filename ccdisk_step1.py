# ==============================================================================
# ccdisk_step1.py - Iterative Read-Only Scanner with Auto-Setup (Python 2.7)
# ==============================================================================
import os
import sys

def setup_testroot(root_path):
    """Automatically creates the testroot playground on Windows if missing."""
    if os.path.exists(root_path):
        return
        
    print("Initializing testroot playground at: {0}".format(root_path))
    subdirs = [
        "docs", "media", "old", "locked",
        "projects/webapp/src", "projects/webapp/node_modules/lib",
        "projects/api/target", ".cache/app"
    ]
    
    for sub in subdirs:
        d = os.path.join(root_path, sub)
        if not os.path.exists(d):
            os.makedirs(d)
            
    def write_dummy_file(rel_path, size_bytes):
        p = os.path.join(root_path, rel_path)
        p_dir = os.path.dirname(p)
        if not os.path.exists(p_dir):
            os.makedirs(p_dir)
        with open(p, "wb") as f:
            f.write(b"A" * size_bytes)

    # Create files matching the challenge spec sizes
    write_dummy_file("docs/report.pdf", 5242880)
    write_dummy_file("docs/notes.txt", 10)
    write_dummy_file("media/video.bin", 41943040)
    write_dummy_file("media/photo1.bin", 8388608)
    write_dummy_file("media/photo2.bin", 2097152)
    write_dummy_file("projects/webapp/src/app.js", 15)
    write_dummy_file("projects/webapp/node_modules/lib/big.js", 20971520)
    write_dummy_file("projects/webapp/node_modules/lib/other.js", 1048576)
    write_dummy_file("projects/api/target/api.bin", 3145728)
    write_dummy_file(".cache/app/cache.db", 10485760)
    write_dummy_file("old/archive.bin", 15728640)
    write_dummy_file("locked/hidden.txt", 6)
    print("Testroot playground successfully created.")

def scan_directory_iterative(root_path):
    """
    Scans a directory tree iteratively (non-recursive) to comply with 
    deterministic software ground rules. Safely catches permission errors 
    and logs warnings without mutating the filesystem.
    """
    assert os.path.exists(root_path), "Error: Scan root path does not exist at '{0}'.".format(root_path)
    assert os.path.isdir(root_path), "Error: Scan root path must be a directory."

    scanned_items = []
    warning_log = []
    
    # Use a stack/queue for iterative traversal instead of recursion
    queue = [root_path]
    
    while len(queue) > 0:
        current_dir = queue.pop(0)
        
        try:
            entries = os.listdir(current_dir)
        except OSError as e:
            warning_msg = "WARNING: Cannot read directory {0}: {1}".format(current_dir, e)
            warning_log.append(warning_msg)
            sys.stderr.write(warning_msg + "\n")
            continue
            
        for entry in entries:
            full_path = os.path.join(current_dir, entry)
            scanned_items.append(full_path)
            
            if os.path.isdir(full_path) and not os.path.islink(full_path):
                queue.append(full_path)
                
    return scanned_items, warning_log

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_root = os.path.join(script_dir, "testroot")
    
    # Ensure testroot exists
    setup_testroot(target_root)

    print("Starting read-only scan of: {0}".format(target_root))
    items, warnings = scan_directory_iterative(target_root)
    print("Total items found: {0}".format(len(items)))
    print("Encountered {0} permission warnings.".format(len(warnings)))
