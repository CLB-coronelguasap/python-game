import turtle
from svg.path import parse_path, Move, Line, CubicBezier, QuadraticBezier, Arc
from xml.etree import ElementTree as ET
import pycountry
import os

def draw_segment(t, segment, scale):
    """Draw a single segment using a turtle."""
    if isinstance(segment, Move):
        t.penup()
        t.goto(segment.start.real * scale, -segment.start.imag * scale)
    elif isinstance(segment, Line):
        t.pendown()
        t.goto(segment.end.real * scale, -segment.end.imag * scale)
    elif isinstance(segment, CubicBezier):
        for t_val in range(0, 11):  # Reduce steps for faster drawing
            t_val /= 10
            point = segment.point(t_val)
            t.goto(point.real * scale, -point.imag * scale)
    elif isinstance(segment, QuadraticBezier):
        for t_val in range(0, 11):  # Reduce steps for faster drawing
            t_val /= 10
            point = segment.point(t_val)
            t.goto(point.real * scale, -point.imag * scale)
    elif isinstance(segment, Arc):
        for t_val in range(0, 11):  # Reduce steps for faster drawing
            t_val /= 10
            point = segment.point(t_val)
            t.goto(point.real * scale, -point.imag * scale)

def get_country_name_from_filename(filename):
    """Extract the country name from the filename based on its abbreviation."""
    abbreviation = filename.split('.')[0].upper()  # Get the part before the extension and convert to uppercase
    country = pycountry.countries.get(alpha_2=abbreviation)
    return country.official_name if country and hasattr(country, 'official_name') else country.name if country else "Unknown Country"

def zoom_in_out(scale_factor, zoom_level, min_x, min_y, max_x, max_y):
    """Adjust the zoom level dynamically while preserving the aspect ratio."""
    zoom_factor = 1.1 if zoom_level > 0 else 0.9  # Gradual zoom in or out
    scale_factor *= zoom_factor

    # Calculate the new viewport dimensions while preserving the aspect ratio
    width = (max_x - min_x) * scale_factor
    height = (max_y - min_y) * scale_factor
    aspect_ratio = width / height

    # Center the viewport
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2

    # Adjust the world coordinates to preserve the aspect ratio
    if aspect_ratio > 1:  # Wider than tall
        turtle.setworldcoordinates(
            center_x - width / 2,
            center_y - (width / aspect_ratio) / 2,
            center_x + width / 2,
            center_y + (width / aspect_ratio) / 2
        )
    else:  # Taller than wide
        turtle.setworldcoordinates(
            center_x - (height * aspect_ratio) / 2,
            center_y - height / 2,
            center_x + (height * aspect_ratio) / 2,
            center_y + height / 2
        )

    return scale_factor

def move_view(dx, dy, scale_factor, min_x, min_y, max_x, max_y):
    """Move the view by adjusting the world coordinates."""
    width = (max_x - min_x) * scale_factor
    height = (max_y - min_y) * scale_factor

    # Adjust the world coordinates based on the movement
    turtle.setworldcoordinates(
        min_x * scale_factor + dx,
        min_y * scale_factor + dy,
        min_x * scale_factor + dx + width,
        min_y * scale_factor + dy + height
    )

def svg_to_turtle(svg_file):
    try:
        # Get the country name from the filename
        country_name = get_country_name_from_filename(os.path.basename(svg_file))
        print(f"Rendering map for: {country_name}")

        # Reset the turtle environment
        turtle.clearscreen()  # Clears the screen and resets all turtles
        turtle.tracer(0)  # Disable screen updates for faster drawing

        # Parse the SVG file
        tree = ET.parse(svg_file)
        root = tree.getroot()

        # Extract all path elements from the SVG file
        namespace = {'svg': 'http://www.w3.org/2000/svg'}
        path_elements = root.findall('.//svg:path', namespace)
        if not path_elements:
            print("No path elements found in the SVG file.")
            return

        # Calculate the bounding box of all paths
        min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')
        for path_element in path_elements:
            path_data = path_element.attrib.get('d')
            if not path_data:
                continue

            path = parse_path(path_data)
            for segment in path:
                for point in [segment.start, segment.end]:
                    if point:
                        min_x = min(min_x, point.real)
                        min_y = min(min_y, -point.imag)
                        max_x = max(max_x, point.real)
                        max_y = max(max_y, -point.imag)

        # Calculate width and height of the bounding box
        width = max_x - min_x
        height = max_y - min_y

        # Set maximum dimensions for the window
        max_width = 800  # Maximum width of the window
        max_height = 600  # Maximum height of the window

        # Scale down if the dimensions exceed the maximum
        scale_factor = min(max_width / (width + 40), max_height / (height + 40), 1)  # Add margin and ensure scale <= 1
        width *= scale_factor
        height *= scale_factor
        margin = 20 * scale_factor  # Scale the margin as well

        # Set up the turtle screen with the scaled dimensions
        screen_width = int(width + 2 * margin)
        screen_height = int(height + 2 * margin)

        turtle.setup(width=screen_width, height=screen_height)
        turtle.setworldcoordinates(
            min_x * scale_factor - margin,
            min_y * scale_factor - margin,
            max_x * scale_factor + margin,
            max_y * scale_factor + margin
        )

        # Create multiple turtles
        turtles = [turtle.Turtle() for _ in range(len(path_elements))]
        for t in turtles:
            t.speed(0)  # Set fastest drawing speed
            t.penup()
            t.fillcolor("lightblue")  # Set pastel blue fill color

        # Parse paths and interleave drawing operations
        paths = [parse_path(path_element.attrib.get('d')) for path_element in path_elements if path_element.attrib.get('d')]

        for path, t in zip(paths, turtles):
            t.penup()
            t.goto(path[0].start.real * scale_factor, -path[0].start.imag * scale_factor)
            t.begin_fill()
            for segment in path:
                draw_segment(t, segment, scale_factor)
            t.penup()  # Ensure no unintended lines are drawn
            t.goto(path[0].start.real * scale_factor, -path[0].start.imag * scale_factor)  # Close the path
            t.end_fill()
            t.hideturtle()

        turtle.update()  # Re-enable screen updates

        # Add zoom functionality
        def zoom_in():
            nonlocal scale_factor
            scale_factor = zoom_in_out(scale_factor, 1, min_x, min_y, max_x, max_y)

        def zoom_out():
            nonlocal scale_factor
            scale_factor = zoom_in_out(scale_factor, -1, min_x, min_y, max_x, max_y)

        # Add pan functionality
        def pan_left():
            move_view(-50, 0, scale_factor, min_x, min_y, max_x, max_y)

        def pan_right():
            move_view(50, 0, scale_factor, min_x, min_y, max_x, max_y)

        def pan_up():
            move_view(0, 50, scale_factor, min_x, min_y, max_x, max_y)

        def pan_down():
            move_view(0, -50, scale_factor, min_x, min_y, max_x, max_y)

        turtle.listen()
        turtle.onkey(zoom_in, "i")  # Press 'i' to zoom in
        turtle.onkey(zoom_out, "o")  # Press 'o' to zoom out
        turtle.onkey(pan_left, "Left")  # Press left arrow to pan left
        turtle.onkey(pan_right, "Right")  # Press right arrow to pan right
        turtle.onkey(pan_up, "Up")  # Press up arrow to pan up
        turtle.onkey(pan_down, "Down")  # Press down arrow to pan down
        turtle.mainloop()

    except turtle.Terminator:
        print("Turtle graphics window was closed. Restarting turtle environment...")
        turtle.Screen()  # Reinitialize the turtle screen
        svg_to_turtle(svg_file)  # Retry rendering the same file

# Example usage
while True:
    g = input("Enter path to SVG file (or 'exit' to quit): ").upper()
    svg_file_path = "maps/"+ g +".svg"
    if g.lower() == 'exit':
        break
    svg_to_turtle(svg_file_path)