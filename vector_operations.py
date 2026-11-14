import numpy as np


SYSTEMS = ("Cartesian", "Cylindrical", "Spherical")


# =========================
# BASIS MATRIX
# =========================

def basis_matrix(system, angles=None):
    """
    Return matrix M such that:
    Cartesian components = M @ local components

    Cylindrical angles: (phi,)
    Spherical angles: (theta, phi)

    All angles are in degrees.
    """

    system = system.lower()

    if system == "cartesian":

        return np.eye(3)

    angles = angles or ()

    if system == "cylindrical":

        if len(angles) != 1:

            raise ValueError(
                "Cylindrical basis needs phi."
            )

        phi = np.deg2rad(float(angles[0]))

        c = np.cos(phi)
        s = np.sin(phi)

        return np.array([
            [c, -s, 0],
            [s,  c, 0],
            [0,  0, 1]
        ])

    if system == "spherical":

        if len(angles) != 2:

            raise ValueError(
                "Spherical basis needs theta and phi."
            )

        theta, phi = np.deg2rad(
            np.asarray(angles, dtype=float)
        )

        st = np.sin(theta)
        ct = np.cos(theta)

        sp = np.sin(phi)
        cp = np.cos(phi)

        return np.array([
            [st * cp, ct * cp, -sp],
            [st * sp, ct * sp,  cp],
            [ct,      -st,      0]
        ])

    raise ValueError(
        f"Unsupported coordinate system: {system}"
    )


# =========================
# VECTOR TO CARTESIAN
# =========================

def vector_to_cartesian(
    components,
    system,
    angles=None
):

    components = np.asarray(
        components,
        dtype=float
    )

    if components.shape != (3,):

        raise ValueError(
            "A vector must contain exactly three components."
        )

    matrix = basis_matrix(
        system,
        angles
    )

    return matrix @ components


# =========================
# VECTOR FROM CARTESIAN
# =========================

def vector_from_cartesian(
    cartesian,
    system,
    angles=None
):

    cartesian = np.asarray(
        cartesian,
        dtype=float
    )

    if cartesian.shape != (3,):

        raise ValueError(
            "A vector must contain exactly three components."
        )

    matrix = basis_matrix(
        system,
        angles
    )

    # The basis is orthonormal, so inverse = transpose

    return matrix.T @ cartesian


# =========================
# VECTOR TRANSFORMATION
# =========================

def transform_vector(
    components,
    source,
    source_angles=None,
    target="Cartesian",
    target_angles=None
):

    cartesian = vector_to_cartesian(
        components,
        source,
        source_angles
    )

    result = vector_from_cartesian(
        cartesian,
        target,
        target_angles
    )

    return result, cartesian


# =========================
# DOT PRODUCT
# =========================

def dot_product(
    a,
    system_a,
    angles_a,
    b,
    system_b,
    angles_b
):

    cart_a = vector_to_cartesian(
        a,
        system_a,
        angles_a
    )

    cart_b = vector_to_cartesian(
        b,
        system_b,
        angles_b
    )

    result = np.dot(
        cart_a,
        cart_b
    )

    return float(result), cart_a, cart_b


# =========================
# CROSS PRODUCT
# =========================

def cross_product(
    a,
    system_a,
    angles_a,
    b,
    system_b,
    angles_b,
    result_system="Cartesian",
    result_angles=None
):

    cart_a = vector_to_cartesian(
        a,
        system_a,
        angles_a
    )

    cart_b = vector_to_cartesian(
        b,
        system_b,
        angles_b
    )

    cart_result = np.cross(
        cart_a,
        cart_b
    )

    result = vector_from_cartesian(
        cart_result,
        result_system,
        result_angles
    )

    return result, cart_result, cart_a, cart_b


# =========================
# SCALAR TRIPLE PRODUCT
# =========================

def scalar_triple_product(
    a,
    system_a,
    angles_a,
    b,
    system_b,
    angles_b,
    c,
    system_c,
    angles_c
):
    """
    Calculate Scalar Triple Product:

        A . (B x C)

    All vectors are first converted to Cartesian components.
    """

    cart_a = vector_to_cartesian(
        a,
        system_a,
        angles_a
    )

    cart_b = vector_to_cartesian(
        b,
        system_b,
        angles_b
    )

    cart_c = vector_to_cartesian(
        c,
        system_c,
        angles_c
    )

    cross_result = np.cross(
        cart_b,
        cart_c
    )

    result = np.dot(
        cart_a,
        cross_result
    )

    return (
        float(result),
        cart_a,
        cart_b,
        cart_c
    )