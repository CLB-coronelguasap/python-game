import os
from svgpathtools import svg2paths, wsvg
import xml.etree.ElementTree as ET

def fix_ru_svg(file_path, output_path):
    """Fix RU.svg by moving objects on the far left next to the furthest right object and resizing the viewport."""
    # Parse the SVG file
    paths, attributes = svg2paths(file_path)
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Calculate the bounding box of all paths
    min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')
    for path in paths:
        for segment in path:
            min_x = min(min_x, segment.start.real, segment.end.real)
            min_y = min(min_y, segment.start.imag, segment.end.imag)
            max_x = max(max_x, segment.start.real, segment.end.real)
            max_y = max(max_y, segment.start.imag, segment.end.imag)

    # Identify objects on the far left
    left_objects = []
    remaining_objects = []
    left_attributes = []
    remaining_attributes = []
    for path, attr in zip(paths, attributes):
        is_left_object = False
        for segment in path:
            if segment.start.real < min_x + (max_x - min_x) * 0.1:  # Objects on the far left
                is_left_object = True
                break
        if is_left_object:
            left_objects.append(path)
            left_attributes.append(attr)
        else:
            remaining_objects.append(path)
            remaining_attributes.append(attr)

    # Move left objects next to the furthest right object
    move_distance = max_x - min_x # Move slightly to the right of the furthest right object
    for path in left_objects:
        for segment in path:
            segment.start += complex(move_distance, 0)
            segment.end += complex(move_distance, 0)

    # Combine moved objects with remaining objects
    updated_paths = remaining_objects + left_objects
    updated_attributes = remaining_attributes + left_attributes

    # Recalculate the bounding box after moving objects
    min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')
    for path in updated_paths:
        for segment in path:
            min_x = min(min_x, segment.start.real, segment.end.real)
            min_y = min(min_y, segment.start.imag, segment.end.imag)
            max_x = max(max_x, segment.start.real, segment.end.real)
            max_y = max(max_y, segment.start.imag, segment.end.imag)

    # Resize the viewport to fit the entire image
    root.attrib["viewBox"] = f"{min_x} {min_y} {max_x - min_x} {max_y - min_y}"
    root.attrib["width"] = f"{max_x - min_x}px"
    root.attrib["height"] = f"{max_y - min_y}px"

    # Save the modified SVG with original attributes
    wsvg(updated_paths, attributes=updated_attributes, filename=output_path)
    print(f"Fixed RU.svg -> {output_path}")

def main():
    maps_dir = "maps"
    output_dir = "fixed_maps"
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(maps_dir, "RU.svg")
    output_path = os.path.join(output_dir, "RU_fixed.svg")
    fix_ru_svg(file_path, output_path)

if __name__ == "__main__":
    main()