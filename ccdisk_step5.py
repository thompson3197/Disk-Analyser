# ==============================================================================
# ccdisk_step5.py - Interactive Navigation, Breadcrumbs & Resizing (Python 2.7)
# ==============================================================================
import os
import sys

class TreemapNavigator(object):
    """
    Manages state for hierarchical treemap navigation, breadcrumb trails,
    item selection highlighting, and viewport resizing.
    """
    def __init__(self, root_path, canvas_width, canvas_height):
        assert os.path.exists(root_path), "Error: Root path must exist."
        assert os.path.isdir(root_path), "Error: Root path must be a directory."
        
        self.root_path = os.path.abspath(root_path)
        self.current_scope = self.root_path
        self.breadcrumb_stack = [self.root_path]
        self.selected_item = None
        self.width = float(canvas_width)
        self.height = float(canvas_height)

    def push_scope(self, directory_path):
        """
        Zoom into a nested directory so its contents fill the whole treemap.
        """
        assert os.path.isdir(directory_path), "Error: Scope must be a valid directory."
        abs_path = os.path.abspath(directory_path)
        self.breadcrumb_stack.append(abs_path)
        self.current_scope = abs_path
        self.selected_item = None # Clear selection on scope change

    def pop_scope(self):
        """
        Go back up one level in the breadcrumb trail.
        """
        if len(self.breadcrumb_stack) > 1:
            self.breadcrumb_stack.pop()
            self.current_scope = self.breadcrumb_stack[-1]
            self.selected_item = None
            return True
        return False

    def jump_to_root(self):
        """
        Jump straight back to the top-level scan root in one action.
        """
        if len(self.breadcrumb_stack) > 0:
            self.current_scope = self.breadcrumb_stack[0]
            self.breadcrumb_stack = [self.current_scope]
            self.selected_item = None

    def select_item(self, item_path):
        """
        Highlight and select a specific item in the treemap.
        """
        self.selected_item = item_path

    def resize_canvas(self, new_width, new_height):
        """
        Adjust viewport dimensions for dynamic window/terminal resizing 
        without breaking layout bounds.
        """
        assert new_width > 0 and new_height > 0, "Error: Dimensions must be positive."
        self.width = float(new_width)
        self.height = float(new_height)

    def get_breadcrumbs(self):
        """
        Return the active breadcrumb path hierarchy.
        """
        return list(self.breadcrumb_stack)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_root = os.path.join(script_dir, "testroot")
    
    if os.path.exists(target_root):
        nav = TreemapNavigator(target_root, 800.0, 600.0)
        print("Initial Scope: {0}".format(nav.current_scope))
        print("Breadcrumbs: {0}".format(nav.get_breadcrumbs()))
        
        # Simulate navigating into media directory
        media_path = os.path.join(target_root, "media")
        if os.path.exists(media_path):
            nav.push_scope(media_path)
            print("\nZoomed In Scope: {0}".format(nav.current_scope))
            print("Breadcrumbs: {0}".format(nav.get_breadcrumbs()))
            
            nav.select_item(os.path.join(media_path, "video.bin"))
            print("Selected Item Highlight: {0}".format(nav.selected_item))
            
            # Jump straight back to root in one action
            nav.jump_to_root()
            print("\nJumped Back to Root: {0}".format(nav.current_scope))
            print("Breadcrumbs: {0}".format(nav.get_breadcrumbs()))
    else:
        print("Error: testroot directory not found.")
