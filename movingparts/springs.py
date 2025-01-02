import build123d as bd

def spring(spring_radius: float, coil_radius: float, height: float, pitch: float) -> bd.Part:
    """Make a spring. This is based on the demo here: https://github.com/gumyr/build123d/issues/759,
    and is mostly a placeholder for later development to make the design more robust and user-friendly.

    Some notes/warnings:
    * Springs are best printed on their sides, as this reduces overhang as well as the stress
    on the coils themselves. In the future I should add an option to trim the outer edges of
    the coils so they can lay flat better, and I should probably set the default orientation
    to be flat.
    * PLA does not have an incredibly large bending range, and will snap if stressed too much.
    You can mitigate this somewhat by using a smaller pitch angle, which controls how spaced
    out each coil wind is (at the expense of having less movement range). 
    """
    p = bd.Part()
    helix = bd.Helix(radius=spring_radius, pitch=pitch, height=height, cone_angle=0)
    p += bd.sweep(
        path=helix,
        sections=((helix ^ 0) * bd.Circle(radius=coil_radius)),
    )
    return p