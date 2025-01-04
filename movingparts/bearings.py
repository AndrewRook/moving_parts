"""Create ball bearings"""
import build123d as bd
import numpy as np
from math import pi, sqrt, tan

def make_bearing(
        inner_diameter: float,
        outer_diameter: float,
        enclosure_height: float,
        vertical_curvature_ratio: float = 1.5,
        opening_size: float = 0.2,
        minimum_object_gap: float = 0.1,
):
    ball_radius = (outer_diameter - inner_diameter) / 2
    inner_diameter -= minimum_object_gap
    outer_diameter += minimum_object_gap
    torus_center_diameter = (inner_diameter + outer_diameter) / 2.
    torus_center_radius = torus_center_diameter / 2.

    # Given the vertical opening size desired, we have to figure out how tall the
    # bearing enclosure must be in order to preserve the minimum object gap on each side.
    # To do that we calculate where the circular bearings (plus minimum gap) will intersect the opening:
    assert opening_size <= 2 * ball_radius
    assert vertical_curvature_ratio >= 1
    enclosure_half_height = enclosure_height / 2  # height above/below zero

    # The borehole is a complicated object. To reduce the amount of contact
    # between the bearing and the faces, the vertical dimension can be set
    # to be larger than the horizontal dimension (the horizontal diameter is
    # fixed to be outer_diameter - inner_diameter), which
    # then controls the ellipticity of the main part of the borehole. However,
    # to make an opening the size of vertical_opening_size, the ellipse is connected
    # to a line with slope of 30 degrees. This minimizes the amount of
    # pure overhang that needs to be extruded.
    ellipse_x_radius = ball_radius + 2 * minimum_object_gap
    ellipse_z_radius = ellipse_x_radius * vertical_curvature_ratio

    opening_radius = opening_size / 2
    min_gap_height = sqrt((ball_radius + minimum_object_gap) ** 2 - opening_radius ** 2)
    assert min_gap_height <= enclosure_half_height

    join_line_slope = -tan(30 * pi / 180)
    join_line_intercept = min_gap_height - join_line_slope * opening_radius

    z_values = np.linspace(-enclosure_half_height, enclosure_half_height, 100)
    x_values = np.zeros(len(z_values))

    for i, z_value in enumerate(z_values):
        ellipse_x_value = None if abs(z_value) > ellipse_z_radius else ellipse_x_radius * sqrt(
            1 - (z_value / ellipse_z_radius) ** 2)
        line_x_value = (abs(z_value) - join_line_intercept) / join_line_slope
        if abs(z_value) > min_gap_height:
            x_values[i] = opening_radius
        elif ellipse_x_value is None or line_x_value < ellipse_x_value:
            x_values[i] = abs(line_x_value)
        else:
            x_values[i] = ellipse_x_value

    x_values_inner = -x_values + torus_center_radius
    x_values_outer = x_values + torus_center_radius

    outer_spline_points = list(zip(x_values_outer, z_values))
    inner_spline_points = list(zip(x_values_inner, z_values))

    with bd.BuildPart() as bearing_cutout:
        with bd.BuildSketch(bd.Plane.XZ) as sketch:
            with bd.BuildLine() as line:
                l1 = bd.Line(
                    (x_values_inner[0], z_values[0]),
                    (x_values_outer[0], z_values[0])
                )
                l2 = bd.Spline(outer_spline_points)
                l3 = bd.Line(
                    (x_values_outer[-1], z_values[-1]),
                    (x_values_inner[-1], z_values[-1])
                )
                l4 = bd.Spline(inner_spline_points)

            bd.make_face()

        bd.revolve(axis=bd.Axis.Z, revolution_arc=360)


    circumference = torus_center_diameter * pi
    number_of_balls = int(circumference // (2 * ball_radius))
    ball_center_angles = np.linspace(0, 2 * pi, number_of_balls + 1)[:-1]
    ball_center_x_coordinates = torus_center_diameter * np.cos(ball_center_angles) / 2
    ball_center_y_coordinates = torus_center_diameter * np.sin(ball_center_angles) / 2

    print(min_gap_height, enclosure_half_height)

    with bd.BuildPart() as bearings:
        with bd.Locations(*zip(ball_center_x_coordinates, ball_center_y_coordinates)):
            bd.Sphere(ball_radius)

    return bearing_cutout, bearings


if __name__ == "__main__":
    enclosure_height = 10
    enclosure_width = 40
    bearing_cutout, bearings = make_bearing(
        20, 30, enclosure_height,
        opening_size=4, minimum_object_gap=0.1
    )
    with bd.BuildPart() as enclosure:
        # Add flat cylinders for the enclosure bracket
        enclosure_block = bd.Cylinder(enclosure_width / 2, enclosure_height)

    final_part = enclosure.part - bearing_cutout.part + bearings.part
    bd.export_stl(final_part, "test.stl")
