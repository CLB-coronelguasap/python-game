import os
import math
from svgpathtools import svg2paths, wsvg

def calculate_centroid(paths):
    """Calculate the centroid of a group of paths."""
    x_coords = []
    y_coords = []
    for path in paths:
        for segment in path:
            x_coords.append(segment.start.real)
            y_coords.append(segment.start.imag)
    if not x_coords or not y_coords:
        return None
    return (sum(x_coords) / len(x_coords), sum(y_coords) / len(y_coords))

def calculate_dynamic_threshold(paths, centroid):
    """Calculate a dynamic threshold based on the average distance of paths from the centroid."""
    distances = []
    for path in paths:
        for segment in path:
            distance = math.sqrt((segment.start.real - centroid[0])**2 + (segment.start.imag - centroid[1])**2)
            distances.append(distance)
    if not distances:
        return 100  # Default threshold if no distances are calculated
    average_distance = sum(distances) / len(distances)
    return average_distance * 5.0  # Adjust multiplier as needed

def filter_noise(paths, centroid, threshold):
    """Filter out paths that are too far from the centroid."""
    filtered_paths = []
    for path in paths:
        for segment in path:
            distance = math.sqrt((segment.start.real - centroid[0])**2 + (segment.start.imag - centroid[1])**2)
            if distance <= threshold:
                filtered_paths.append(path)
                break
    return filtered_paths

def process_svg_file(file_path, output_dir):
    """Process an SVG file to remove noise."""
    try:
        paths, attributes = svg2paths(file_path)
        if not paths:
            print(f"No paths found in {file_path}. Skipping...")
            return
        centroid = calculate_centroid(paths)
        if centroid is None:
            print(f"Failed to calculate centroid for {file_path}. Skipping...")
            return
        threshold = calculate_dynamic_threshold(paths, centroid)
        filtered_paths = filter_noise(paths, centroid, threshold)
        if not filtered_paths:
            print(f"No paths passed the noise filter for {file_path}. Skipping...")
            return
        output_path = os.path.join(output_dir, os.path.basename(file_path))
        wsvg(filtered_paths, filename=output_path)
        print(f"Processed {file_path} -> {output_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    maps_dir = "maps"
    output_dir = "cleaned_maps"
    os.makedirs(output_dir, exist_ok=True)

    for file_name in os.listdir(maps_dir):
        if file_name.endswith(".svg"):
            file_path = os.path.join(maps_dir, file_name)
            print(f"Processing {file_path}...")
            process_svg_file(file_path, output_dir)

if __name__ == "__main__":
    main()