# ==============================================================================
# ccdisk_step10.py - Staged Cleanup Set & Free Space Predictions (Python 2.7)
# ==============================================================================
import os
import sys

class StagedCleanupManager(object):
    """
    Manages staged cleanup sets, prevents double-counting nested items and 
    hard links, and predicts volume free space changes.
    """
    def __init__(self):
        self.staged_paths = set()

    def stage_item(self, item_path):
        """
        Adds an item path to the staged cleanup set.
        """
        assert isinstance(item_path, str), "Error: item_path must be a string."
        abs_path = os.path.abspath(item_path)
        self.staged_paths.add(abs_path)

    def unstage_item(self, item_path):
        """
        Removes an item path from the staged cleanup set.
        """
        abs_path = os.path.abspath(item_path)
        if abs_path in self.staged_paths:
            self.staged_paths.remove(abs_path)

    def clear_stage(self):
        """
        Clears all staged items.
        """
        self.staged_paths.clear()

    def calculate_staged_savings(self, scanned_items_dict):
        """
        Calculates total unique disk bytes saved by the staged set.
        Guards against double-counting:
        1. If a parent directory is staged, descendants inside it are ignored.
        2. If hard links share an inode, their storage blocks are only counted once.
        """
        assert isinstance(scanned_items_dict, dict), "Error: scanned_items_dict required."
        
        # Sort staged paths by length ascending so parent directories are evaluated first
        sorted_staged = sorted(list(self.staged_paths), key=len)
        effective_staged_items = []
        covered_prefixes = set()

        for path in sorted_staged:
            # Check if this path is already covered by a parent directory in the stage set
            is_covered = False
            for prefix in covered_prefixes:
                if path == prefix or path.startswith(prefix + os.sep):
                    is_covered = True
                    break
                    
            if not is_covered:
                effective_staged_items.append(path)
                if scanned_items_dict.get(path, {}).get("is_dir", False):
                    covered_prefixes.add(path)

        total_savings = 0
        counted_inodes = set()

        for path in effective_staged_items:
            data = scanned_items_dict.get(path, {})
            if data.get("is_dir", False):
                # For directories, sum unique disk usage of un-covered descendants
                for sub_path, sub_data in scanned_items_dict.items():
                    if sub_path == path or sub_path.startswith(path + os.sep):
                        inode_key = sub_data.get("inode_key", None)
                        disk_usage = sub_data.get("disk_usage", 0)
                        
                        if inode_key and inode_key != (0, 0):
                            if inode_key not in counted_inodes:
                                counted_inodes.add(inode_key)
                                total_savings += disk_usage
                        else:
                            total_savings += disk_usage
            else:
                # Single file or link
                inode_key = data.get("inode_key", None)
                disk_usage = data.get("disk_usage", 0)
                
                if inode_key and inode_key != (0, 0):
                    if inode_key not in counted_inodes:
                        counted_inodes.add(inode_key)
                        total_savings += disk_usage
                else:
                    total_savings += disk_usage

        return total_savings

    def predict_free_space(self, current_free_bytes, scanned_items_dict):
        """
        Predicts volume free space after staged set removal:
        Predicted Free Space = Current Free Space + Staged Savings.
        """
        savings = self.calculate_staged_savings(scanned_items_dict)
        return current_free_bytes + savings

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_root = os.path.join(script_dir, "testroot")
    
    if os.path.exists(target_root):
        print("Testing Staged Cleanup Manager...")
        
        manager = StagedCleanupManager()
        archive_path = os.path.join(target_root, "old", "archive.bin")
        node_modules_path = os.path.join(target_root, "projects", "webapp", "node_modules")
        big_js_path = os.path.join(target_root, "projects", "webapp", "node_modules", "lib", "big.js")
        
        # Mock dataset
        mock_scan = {
            archive_path: {"is_dir": False, "disk_usage": 15728640, "inode_key": (1, 100)},
            node_modules_path: {"is_dir": True, "disk_usage": 21995520},
            big_js_path: {"is_dir": False, "disk_usage": 20971520, "inode_key": (1, 101)}
        }
        
        # Stage archive and node_modules
        manager.stage_item(archive_path)
        manager.stage_item(node_modules_path)
        # Stage big.js which is already inside node_modules (should not double count)
        manager.stage_item(big_js_path)
        
        savings = manager.calculate_staged_savings(mock_scan)
        print("Staged Items Count: {0}".format(len(manager.staged_paths)))
        print("Calculated Staged Savings: {0} bytes ({1:.2f} MB)".format(
            savings, savings / (1024.0 * 1024.0)
        ))
        
        current_free = 100 * 1024 * 1024 * 1024 # 100 GB mock free space
        predicted = manager.predict_free_space(current_free, mock_scan)
        print("Predicted Free Space: {0} bytes".format(predicted))
    else:
        print("Error: testroot directory not found.")
