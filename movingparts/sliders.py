"""Functions to generate parts that can slide on or through each other"""
import build123d as bd
import numpy as np

def twist_extrude_cutout_sketch(
        sketch: bd.BuildSketch,
        height: float,
        rotation_angle_per_unit_height: float,
):
    assert len(sketch.faces()) == 1
    total_rotation_angle = rotation_angle_per_unit_height * height
    face = sketch.face()
    rotated_part = bd.Solid.extrude_linear_with_rotation(
        face,
        center=face.location.position,
        normal=(0, 0, height),
        angle=total_rotation_angle
    )
    return rotated_part

def make_twisted_slider(
        pattern_radius: float,
        slider_height: float,
        enclosure_height: float,
        rotation_angle_per_unit_height: float,
        number_of_patterns: int = 6,
        enclosure_gap: float = 0.3
):
    straight_fraction = 0.85
    radius_fraction = 0.2
    rotations = np.linspace(0, 360, number_of_patterns + 1)[1:-1]

    pattern = _make_pattern(
        straight_fraction, pattern_radius, radius_fraction, rotations
    )
    pattern_cutout = _make_pattern(
        straight_fraction, pattern_radius, radius_fraction, rotations, gap=enclosure_gap
    )

    inner_slider = twist_extrude_cutout_sketch(
        pattern, slider_height, rotation_angle_per_unit_height
    )
    enclosure_cutout = twist_extrude_cutout_sketch(
        pattern_cutout,
        enclosure_height,
        rotation_angle_per_unit_height
    )
    return inner_slider, enclosure_cutout

def _make_pattern(straight_fraction, pattern_radius, radius_fraction, rotations, gap=0):
    with bd.BuildSketch() as pattern:
        with bd.BuildLine() as curve:
            if gap > 1e-3:
                l1 = bd.Line((0, 0), (gap, 0))
                next_line_start = l1 @ 1
            else:
                next_line_start = (0, 0)
            l2 = bd.Line(
                next_line_start,
                (straight_fraction * pattern_radius, -radius_fraction * pattern_radius - gap)
            )
            l3 = bd.CenterArc(
                (straight_fraction * pattern_radius, 0),
                radius=radius_fraction * pattern_radius + gap,
                start_angle=270, arc_size=180
            )
            l4 = bd.Line(l3 @ 1, (-gap, 0))
            if gap > 1e-3:
                l5 = bd.Line(l4 @ 1, l1 @ 0)
        pattern_face = bd.make_face()

        for rotation_angle in rotations:
            rotated_pattern_face = pattern_face.rotate(bd.Axis.Z, rotation_angle)
            context = bd.BuildSketch._get_context()
            context._add_to_context(rotated_pattern_face)
        central_circle = bd.Circle(pattern_radius / 3 + gap)
    return pattern


if __name__ == "__main__":
    pattern_radius = 15
    gap = 0.3

    enclosure_prism_height = 40
    enclosure_cylinder_height = 10
    inner_slider, slider_cutout = make_twisted_slider(
        pattern_radius,
        15,
        2 * enclosure_prism_height + enclosure_cylinder_height,
        5,
        enclosure_gap=0.3
    )


    enclosure_size = slider_cutout.bounding_box().size
    with bd.BuildPart() as enclosure:
        with bd.BuildSketch() as bottom_circle:
            bd.Circle(enclosure_size.X / 4)
        with bd.BuildSketch(bottom_circle.faces()[0].offset(enclosure_prism_height)) as middle_circle_low:
            bd.Circle(enclosure_size.X / 2 + 5 * gap)
        bottom_prism = bd.loft()
        with bd.BuildSketch(bottom_prism.faces().sort_by(bd.Axis.Z)[-1]) as middle_cylinder:
            bd.Circle(enclosure_size.X / 2 + 5 * gap)
        middle_cylinder = bd.extrude(amount=enclosure_cylinder_height)
        with bd.BuildSketch(middle_cylinder.faces().sort_by(bd.Axis.Z)[-1]) as middle_circle_up:
            bd.Circle(enclosure_size.X / 2 + 5 * gap)
        with bd.BuildSketch(
                middle_cylinder.faces().sort_by(bd.Axis.Z)[-1].offset(
                    enclosure_prism_height
                )):
            bd.Circle(enclosure_size.X / 4)
        bd.loft()
    bd.export_stl(inner_slider, "slider.stl")
    bd.export_stl(enclosure.part - slider_cutout, "slider_enclosure.stl")