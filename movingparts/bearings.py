"""Create ball bearings"""
import build123d as bd
import numpy as np
from math import pi, sqrt

def make_bearing(
        inner_diameter: float,
        outer_diameter: float,
        enclosure_height: float,
        vertical_curvature_ratio: float = 1.5,
        vertical_opening_size: float = 0.2,
        minimum_object_gap: float = 0.1,
):
    # The borehole is a rotated ellipse. To reduce the amount of contact
    # between the bearing and the faces, the vertical dimension can be set
    # to be larger than the horizontal dimension (the horizontal dimension is
    # fixed to be at the radius of the ball plus the minimum_object_gap).
    torus_x_diameter = (inner_diameter + outer_diameter) / 2.
    torus_z_diameter = torus_x_diameter * vertical_curvature_ratio
    ball_radius = (outer_diameter - inner_diameter) / 2 - minimum_object_gap

    # Given the vertical opening size desired, we have to figure out how tall the
    # bearing enclosure must be in order to preserve the minimum object gap on each side.
    # To do that we calculate where the circular bearings will intersect the opening:
    assert vertical_opening_size <= 2 * ball_radius

    minimum_enclosure_height = sqrt(
        (ball_radius) ** 2 -
        (vertical_opening_size / 2) ** 2
    ) * 2
    assert enclosure_height >= minimum_enclosure_height

    full_component_width = outer_diameter * 1.5 / 2

    circumference = torus_x_diameter * pi
    number_of_balls = int(circumference // (2 * ball_radius))
    ball_center_angles = np.linspace(0, 2 * pi, number_of_balls + 1)[:-1]
    ball_center_x_coordinates = torus_x_diameter * np.cos(ball_center_angles) / 2
    ball_center_y_coordinates = torus_x_diameter * np.sin(ball_center_angles) / 2

    print(minimum_enclosure_height, enclosure_height)

    with bd.BuildPart() as elliptical_cutout_cylinder:
        # Make the main cylinder
        main_block = bd.Cylinder(full_component_width, enclosure_height)

        # Bore out the toroidal hole where the bearings will go
        with bd.BuildSketch(bd.Plane.XZ):
            with bd.Locations(((torus_x_diameter / 2), 0)):
                bd.Ellipse(ball_radius + minimum_object_gap, torus_z_diameter + minimum_object_gap)
        bd.revolve(axis=bd.Axis.Z, mode=bd.Mode.SUBTRACT)

    with bd.BuildPart() as enclosure:
        # Add flat cylinders for the enclosure bracket
        enclosure_block = bd.Cylinder(full_component_width, enclosure_height)
        central_cutout = bd.Cylinder(
            full_component_width, minimum_enclosure_height,
            mode=bd.Mode.SUBTRACT
        )
        #bore out a cylinder of vertical_opening_radius * 2
        with bd.BuildSketch(bd.Plane.XZ):
            with bd.Locations(((torus_x_diameter / 2), 0)):
                bd.Rectangle(vertical_opening_size, enclosure_height)
        bd.revolve(axis=bd.Axis.Z, mode=bd.Mode.SUBTRACT)

    with bd.BuildPart() as bearings:
        with bd.Locations(*zip(ball_center_x_coordinates, ball_center_y_coordinates)):
            bd.Sphere(ball_radius)


    final_part = (
            elliptical_cutout_cylinder.part
            + enclosure.part
            + bearings.part
    )
    return final_part


if __name__ == "__main__":
    bearing = make_bearing(
        15, 20, 5,
        vertical_opening_size=2, minimum_object_gap=0.2
    )
    bd.export_stl(bearing, "test.stl")


"""

with bd.BuildPart() as everything:
    block = bd.Cylinder(outer_diameter * 1.5 / 2, ball_radius * 1.9)
    with bd.BuildSketch(bd.Plane.XZ):
        with bd.Locations((torus_diameter / 2, 0)):
            bd.Circle(ball_radius + torus_spacing)
    bd.revolve(axis=bd.Axis.Z, mode=bd.Mode.SUBTRACT)
    with bd.Locations(*zip(ball_center_x_coordinates, ball_center_y_coordinates)):
        bd.Sphere(ball_radius)
    with bd.BuildSketch(block.faces().sort_by(bd.Axis.Z)[0]) as bottom:
        bd.Rectangle(outer_diameter * 1.5, outer_diameter * 1.5)
    bd.extrude(amount=2, mode=bd.Mode.SUBTRACT)
    with bd.BuildSketch(block.faces().sort_by(bd.Axis.Z)[-1]) as top:
        bd.Rectangle(outer_diameter * 1.5, outer_diameter * 1.5)
    bd.extrude(amount=2, mode=bd.Mode.SUBTRACT)
"""