import os
import math
from svgpathtools import svg2paths
import shutil

def calculate_bounding_box(paths):
    """Calculate the bounding box of all paths."""
    min_x, min_y = float('inf'), float('inf')
    max_x, max_y = float('-inf'), float('-inf')
    for path in paths:
        for segment in path:
            min_x = min(min_x, segment.start.real, segment.end.real)
            min_y = min(min_y, segment.start.imag, segment.end.imag)
            max_x = max(max_x, segment.start.real, segment.end.real)
            max_y = max(max_y, segment.start.imag, segment.end.imag)
    return min_x, min_y, max_x, max_y

def calculate_empty_space_ratio(paths, svg_width, svg_height):
    """Calculate the ratio of empty space to the total SVG area."""
    min_x, min_y, max_x, max_y = calculate_bounding_box(paths)
    element_area = (max_x - min_x) * (max_y - min_y)
    svg_area = svg_width * svg_height
    if svg_area == 0:  # Avoid division by zero
        return 1  # Assume full empty space
    empty_space_ratio = 1 - (element_area / svg_area)
    return empty_space_ratio

def extract_svg_dimensions(attributes):
    """Extract width and height from SVG attributes."""
    width = 1000  # Default width
    height = 1000  # Default height
    for attr in attributes:
        if 'width' in attr:
            width = float(attr['width'].replace('px', ''))
        if 'height' in attr:
            height = float(attr['height'].replace('px', ''))
    return width, height

def process_svg_file(file_path, output_dir, threshold=0.8):
    """Process an SVG file to detect excessive empty space."""
    paths, attributes = svg2paths(file_path)
    svg_width, svg_height = extract_svg_dimensions(attributes)
    empty_space_ratio = calculate_empty_space_ratio(paths, svg_width, svg_height)

    if empty_space_ratio > threshold:
        # Copy file to output directory and delete original
        output_path = os.path.join(output_dir, os.path.basename(file_path))
        shutil.copy(file_path, output_path)
        os.remove(file_path)
        print(f"Moved and deleted {file_path} -> {output_path}")
    else:
        print(f"Retained {file_path} (empty space ratio: {empty_space_ratio:.2f})")

def main():
    maps_dir = "cleaned_maps"
    output_dir = "excess_empty_space"
    os.makedirs(output_dir, exist_ok=True)

    for file_name in os.listdir(maps_dir):
        if file_name.endswith(".svg"):
            file_path = os.path.join(maps_dir, file_name)
            process_svg_file(file_path, output_dir)

if __name__ == "__main__":
    main()