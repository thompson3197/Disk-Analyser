# ==============================================================================
# ccdisk_step4.py - Squarified Treemap Layout Engine (Python 2.7)
# ==============================================================================
import os
import sys

def normalize_sizes(items, total_area):
    """
    Normalizes item sizes relative to the total available bounding box area.
    """
    assert isinstance(items, list), "Error: items must be a list."
    total_size = sum(item["size"] for item in items)
    if total_size <= 0:
        return []
        
    normalized = []
    for item in items:
        # Scale each item's proportional area
        area = (float(item["size"]) / total_size) * total_area
        normalized.append({
            "name": item["name"],
            "size": item["size"],
            "area": area
        })
    return normalized

def worst_aspect_ratio(row, w):
    """
    Calculates the worst aspect ratio of a candidate row given width w.
    """
    if not row or w <= 0:
        return float("inf")
    s = sum(item["area"] for item in row)
    if s <= 0:
        return float("inf")
    
    max_area = max(item["area"] for item in row)
    min_area = min(item["area"] for item in row)
    
    # Standard aspect ratio metric for squarifying
    r1 = (w * w * max_area) / (s * s)
    r2 = (s * s) / (w * w * min_area)
    return max(r1, r2)

def layout_row(row, x, y, w, h, is_horizontal):
    """
    Lays out a single packed row/column of rectangles into the bounding box.
    """
    rectangles = []
    total_row_area = sum(item["area"] for item in row)
    
    if is_horizontal:
        # Row spans horizontally across width w
        row_height = total_row_area / w if w > 0 else 0
        curr_x = x
        for item in row:
            item_width = item["area"] / row_height if row_height > 0 else 0
            rectangles.append({
                "name": item["name"],
                "size": item["size"],
                "x": curr_x,
                "y": y,
                "w": item_width,
                "h": row_height
            })
            curr_x += item_width
    else:
        # Column spans vertically down height h
        row_width = total_row_area / h if h > 0 else 0
        curr_y = y
        for item in row:
            item_height = item["area"] / row_width if row_width > 0 else 0
            rectangles.append({
                "name": item["name"],
                "size": item["size"],
                "x": x,
                "y": curr_y,
                "w": row_width,
                "h": item_height
            })
            curr_y += item_height
            
    return rectangles

def squarify(items, x, y, w, h):
    """
    Recursively/iteratively packs sorted items into squarified treemap rectangles.
    """
    assert w >= 0 and h >= 0, "Error: Bounding box dimensions must be non-negative."
    if not items:
        return []
        
    # Sort items descending by size for optimal squarifying
    sorted_items = sorted(items, key=lambda k: k["area"], reverse=True)
    
    # If width is smaller than height, layout vertically; otherwise horizontally
    is_horizontal = w >= h
    short_side = h if is_horizontal else w
    
    row = []
    rectangles = []
    
    remaining = list(sorted_items)
    while len(remaining) > 0:
        next_item = remaining[0]
        
        # Test if adding the item worsens the aspect ratio
        if not row or worst_aspect_ratio(row + [next_item], short_side) <= worst_aspect_ratio(row, short_side):
            row.append(remaining.pop(0))
        else:
            # Layout current row and update bounding box
            row_rects = layout_row(row, x, y, w, h, is_horizontal)
            rectangles.extend(row_rects)
            
            # Recalculate remaining bounding box space
            total_row_area = sum(item["area"] for item in row)
            if is_horizontal:
                y += total_row_area / w if w > 0 else 0
                h -= total_row_area / w if w > 0 else 0
                short_side = h
            else:
                x += total_row_area / h if h > 0 else 0
                w -= total_row_area / h if h > 0 else 0
                short_side = w
                
            row = []
            
    if row:
        row_rects = layout_row(row, x, y, w, h, is_horizontal)
        rectangles.extend(row_rects)
        
    return rectangles

if __name__ == "__main__":
    # Test layout with mock disk metrics matching testroot media files
    mock_items = [
        {"name": "video.bin", "size": 41943040},
        {"name": "photo1.bin", "size": 8388608},
        {"name": "photo2.bin", "size": 2097152}
    ]
    
    total_box_area = 1000.0 * 1000.0 # 1000x1000 canvas
    normalized = normalize_sizes(mock_items, total_box_area)
    rects = squarify(normalized, 0.0, 0.0, 1000.0, 1000.0)
    
    print("Squarified Treemap Layout Generated:")
    for r in rects:
        print("  - Item: {0} | Box: x={1:.1f}, y={2:.1f}, w={3:.1f}, h={4:.1f}".format(
            r["name"], r["x"], r["y"], r["w"], r["h"]
        ))
