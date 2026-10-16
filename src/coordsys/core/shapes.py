Point2D = tuple[float, float]
Point3D = tuple[float, float, float]


def demo_polygon_2d() -> list[Point2D]:
    return [
        (0.0, 0.0),
        (3.0, 0.0),
        (3.0, 1.0),
        (4.5, -0.5),
        (3.0, -2.0),
        (3.0, -1.0),
        (0.0, -1.0),
    ]


def demo_wireframe_3d() -> tuple[list[Point3D], list[tuple[int, int]]]:
    vertices: list[Point3D] = [
        (0.0, 0.0, 0.0),
        (2.0, 0.0, 0.0),
        (2.0, 1.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.5),
        (2.0, 0.0, 1.5),
        (2.0, 1.0, 1.5),
        (0.0, 1.0, 1.5),
        (0.3, 0.8, 2.6),
    ]
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7),
        (4, 8), (5, 8), (6, 8), (7, 8),
    ]
    return vertices, edges
