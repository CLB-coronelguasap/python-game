import os
from svgpathtools import svg2paths, wsvg
import xml.etree.ElementTree as ET

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

def scale_svg_file(file_path, output_path, target_resolution):
    """Scale the SVG file content and dimensions."""
    # Parse the SVG file
    paths, attributes = svg2paths(file_path)
    min_x, min_y, max_x, max_y = calculate_bounding_box(paths)
    current_width = max_x - min_x
    current_height = max_y - min_y

    # Calculate scaling factor
    scale_factor = max(target_resolution / current_width, target_resolution / current_height)

    # Scale paths
    scaled_paths = [path.scaled(scale_factor) for path in paths]

    # Update SVG dimensions and viewport
    tree = ET.parse(file_path)
    root = tree.getroot()
    width = float(root.attrib.get("width", "1000").replace("px", ""))
    height = float(root.attrib.get("height", "1000").replace("px", ""))
    scaled_width = max(width * scale_factor, target_resolution)
    scaled_height = max(height * scale_factor, target_resolution)
    root.attrib["width"] = f"{scaled_width}px"
    root.attrib["height"] = f"{scaled_height}px"
    root.attrib["viewBox"] = f"0 0 {scaled_width} {scaled_height}"

    # Write scaled paths back to the SVG
    wsvg(scaled_paths, filename=output_path)
    tree.write(output_path)
    print(f"Scaled {file_path} -> {output_path}")

def process_svg_file(file_path, output_dir, target_resolution):
    """Process an SVG file to scale it up if necessary."""
    output_path = os.path.join(output_dir, os.path.basename(file_path))
    scale_svg_file(file_path, output_path, target_resolution)

def main():
    maps_dir = "cleaned_maps"
    output_dir = "scaled_maps"
    target_resolution = 1000  # Minimum resolution for width or height
    os.makedirs(output_dir, exist_ok=True)

    for file_name in os.listdir(maps_dir):
        if file_name.endswith(".svg"):
            file_path = os.path.join(maps_dir, file_name)
            process_svg_file(file_path, output_dir, target_resolution)

if __name__ == "__main__":
    main()