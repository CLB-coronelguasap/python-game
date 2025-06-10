import turtle
from svg.path import parse_path, Move, Line, CubicBezier, QuadraticBezier, Arc
from xml.etree import ElementTree as ET

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

def svg_to_turtle(svg_file):
    try:
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
        max_segments = max(len(path) for path in paths)

        for i in range(max_segments):
            for t, path in zip(turtles, paths):
                if i < len(path):
                    segment = path[i]
                    if i == 0:  # Start filling at the beginning of the path
                        t.begin_fill()
                    draw_segment(t, segment, scale_factor)  # Apply scale factor to drawing
            for t, path in zip(turtles, paths):
                if i == len(path) - 1:  # End filling at the end of the path
                    t.end_fill()
                    t.hideturtle()  # Hide the turtle after it finishes drawing

        turtle.update()  # Re-enable screen updates
    except turtle.Terminator:
        print("Turtle graphics window was closed. Restarting turtle environment...")
        turtle.Screen()  # Reinitialize the turtle screen
        svg_to_turtle(svg_file)  # Retry rendering the same file

# Example usage
while True:
    svg_file_path = input("Enter path to SVG file (or 'exit' to quit): ")
    if svg_file_path.lower() == 'exit':
        break
    svg_to_turtle(svg_file_path)