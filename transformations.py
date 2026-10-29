
import numpy as np

def to_cartesian(values, system):
    """Convert coordinates to Cartesian (x, y, z)."""

    system = system.lower()

    if system == "cartesian":
        x, y, z = values
        return np.array([x, y, z], dtype=float)

    elif system == "cylindrical":
        rho, phi, z = values

        # Convert degrees to radians
        phi = np.deg2rad(phi)

        x = rho * np.cos(phi)
        y = rho * np.sin(phi)

        return np.array([x, y, z], dtype=float)

    elif system == "spherical":
        r, theta, phi = values

        # theta: angle from positive z-axis
        # phi: azimuth angle in the xy-plane
        theta = np.deg2rad(theta)
        phi = np.deg2rad(phi)

        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)

        return np.array([x, y, z], dtype=float)

    else:
        raise ValueError("Unsupported coordinate system")

def from_cartesian(point, system):
    """Convert Cartesian (x, y, z) to another system."""

    x, y, z = point
    system = system.lower()

    if system == "cartesian":
        return np.array([x, y, z], dtype=float)

    elif system == "cylindrical":
        rho = np.hypot(x, y)
        phi = np.rad2deg(np.arctan2(y, x))

        # At the origin, the angle is undefined
        if np.isclose(rho, 0):
            phi = 0.0

        return np.array([rho, phi, z])

    elif system == "spherical":
        r = np.sqrt(x**2 + y**2 + z**2)

        if np.isclose(r, 0):
            theta = 0.0
            phi = 0.0
        else:
            theta = np.rad2deg(np.arccos(np.clip(z / r, -1, 1)))
            phi = np.rad2deg(np.arctan2(y, x))

            if np.isclose(np.hypot(x, y), 0):
                phi = 0.0

        return np.array([r, theta, phi])

    else:
        raise ValueError("Unsupported coordinate system")

def transform(values, source, target):
    """Convert coordinates from source system to target system."""

    point = to_cartesian(values, source)
    return from_cartesian(point, target)

if __name__ == "__main__":
    point = [1, 3, 4]

    result = transform(
        point,
        "cartesian",
        "cylindrical"
    )

    print("Input:", point)
    print("Output [rho, phi, z]:")
    print(np.round(result, 4))