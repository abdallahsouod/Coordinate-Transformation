import numpy as np
import streamlit as st
import plotly.graph_objects as go

from vector_operations import (
    SYSTEMS,
    transform_vector,
    dot_product,
    cross_product,
    scalar_triple_product
)


# =========================
# CUSTOM DARK THEME
# =========================

st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(
                135deg,
                #0b1220 0%,
                #101a2c 55%,
                #111827 100%
            );
        }

        [data-testid="stSidebar"] {
            background: #111827;
            border-right: 1px solid #263449;
        }

        .hero {
            padding: 1.5rem;
            border: 1px solid #263449;
            border-radius: 18px;
            background: linear-gradient(
                120deg,
                #182a43,
                #111827
            );
            margin-bottom: 1.5rem;
        }

        .hero h1 {
            margin: 0;
            font-size: 2.2rem;
            color: #f8fafc;
        }

        .hero p {
            color: #b8c7dc;
            margin-top: 0.6rem;
        }

        .stButton button {
            border-radius: 10px;
            font-weight: bold;
            min-height: 45px;
        }

        div[data-testid="stMetric"] {
            background: rgba(30, 41, 59, 0.72);
            border: 1px solid #334155;
            padding: 12px;
            border-radius: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================
# PAGE HEADER
# =========================

st.title("➡️ Vector Representation")

st.caption(
    "Vector components are transformed using Cartesian, "
    "Cylindrical, and Spherical unit-vector bases."
)


# =========================
# BASIS ANGLES
# =========================

def basis_angles(system, key, label="Basis orientation"):

    if system == "Cartesian":

        st.caption(
            f"{label}: Cartesian basis (no angles required)."
        )

        return None

    if system == "Cylindrical":

        phi = st.number_input(
            f"{label} — φ (degrees)",
            value=0.0,
            key=f"{key}_phi"
        )

        return (phi,)

    theta_col, phi_col = st.columns(2)

    with theta_col:

        theta = st.number_input(
            f"{label} — θ (degrees, from +z)",
            value=90.0,
            key=f"{key}_theta"
        )

    with phi_col:

        phi = st.number_input(
            f"{label} — φ (degrees, azimuth)",
            value=0.0,
            key=f"{key}_phi"
        )

    return (theta, phi)


# =========================
# VECTOR INPUTS
# =========================

def vector_inputs(label, system, key):

    labels = {
        "Cartesian": ("A_x", "A_y", "A_z"),
        "Cylindrical": ("A_ρ", "A_φ", "A_z"),
        "Spherical": ("A_r", "A_θ", "A_φ")
    }

    st.markdown(f"**{label} components ({system})**")

    cols = st.columns(3)

    values = []

    for i, (col, component) in enumerate(
        zip(cols, labels[system])
    ):

        with col:

            value = st.number_input(
                component,
                value=0.0,
                key=f"{key}_component_{i}",
                format="%.6f"
            )

            values.append(value)

    angles = basis_angles(
        system,
        key,
        f"{label} basis"
    )

    return np.asarray(values, dtype=float), angles


# =========================
# 3D VECTOR PLOT
# =========================

def show_vector_plot(vectors, title):

    fig = go.Figure()

    palette = [
        "#22d3ee",
        "#fbbf24",
        "#c084fc"
    ]

    max_abs = max(
        [1.0] + [
            abs(float(x))
            for vector, _ in vectors
            for x in vector
        ]
    )

    limit = max_abs * 1.3

    axes = [
        ("X", "#f87171", [-limit, limit], [0, 0], [0, 0]),
        ("Y", "#4ade80", [0, 0], [-limit, limit], [0, 0]),
        ("Z", "#60a5fa", [0, 0], [0, 0], [-limit, limit])
    ]

    for axis, color, xs, ys, zs in axes:

        fig.add_trace(
            go.Scatter3d(
                x=xs,
                y=ys,
                z=zs,
                mode="lines",
                name=f"{axis}-axis",
                line=dict(
                    color=color,
                    width=4
                )
            )
        )

    for i, (vector, name) in enumerate(vectors):

        x, y, z = map(float, vector)

        fig.add_trace(
            go.Scatter3d(
                x=[0, x],
                y=[0, y],
                z=[0, z],
                mode="lines+markers+text",
                text=["", name],
                textposition="top center",
                name=name,
                line=dict(
                    color=palette[i % len(palette)],
                    width=7
                ),
                marker=dict(size=4)
            )
        )

    fig.update_layout(
        title=title,
        height=520,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e5e7eb"),

        scene=dict(
            xaxis=dict(
                title="X",
                range=[-limit, limit]
            ),

            yaxis=dict(
                title="Y",
                range=[-limit, limit]
            ),

            zaxis=dict(
                title="Z",
                range=[-limit, limit]
            ),

            aspectmode="cube"
        ),

        margin=dict(
            l=0,
            r=0,
            t=50,
            b=0
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displaylogo": False,
            "scrollZoom": True
        }
    )


# =========================
# SIDEBAR
# =========================

operation = st.sidebar.radio(
    "Choose Vector Operation",
    [
        "Vector Transformation",
        "Dot Product",
        "Cross Product",
        "Scalar Triple Product"
    ]
)

st.sidebar.markdown("---")

st.sidebar.caption(
    "Angles are entered in degrees. "
    "Spherical θ is measured from +z."
)


left, right = st.columns([1, 1], gap="large")


# =========================
# INPUTS
# =========================

with left:

    st.subheader("Inputs")

    # -------------------------
    # VECTOR TRANSFORMATION
    # -------------------------

    if operation == "Vector Transformation":

        source = st.selectbox(
            "Source coordinate system",
            SYSTEMS,
            key="vt_source"
        )

        components, source_angles = vector_inputs(
            "Vector A",
            source,
            "vt_source_vector"
        )

        st.divider()

        target = st.selectbox(
            "Target coordinate system",
            SYSTEMS,
            key="vt_target"
        )

        target_angles = basis_angles(
            target,
            "vt_target_basis",
            "Target basis"
        )

        st.info(
            "Source and target angles define the orientation "
            "of each coordinate basis."
        )

        run = st.button(
            "Transform Vector",
            type="primary",
            use_container_width=True
        )

        if run:

            try:

                result, cart = transform_vector(
                    components,
                    source,
                    source_angles,
                    target,
                    target_angles
                )

                st.session_state["vector_result"] = {
                    "kind": "transform",
                    "result": result,
                    "cart": cart,
                    "target": target,
                    "plot": [
                        (cart, "Vector A")
                    ]
                }

            except (ValueError, TypeError) as exc:

                st.error(str(exc))

    # -------------------------
    # VECTOR OPERATIONS
    # -------------------------

    else:

        # Vector A

        system_a = st.selectbox(
            "Vector A coordinate system",
            SYSTEMS,
            key="op_system_a"
        )

        a, angles_a = vector_inputs(
            "Vector A",
            system_a,
            "op_a"
        )

        st.divider()

        # Vector B

        system_b = st.selectbox(
            "Vector B coordinate system",
            SYSTEMS,
            key="op_system_b"
        )

        b, angles_b = vector_inputs(
            "Vector B",
            system_b,
            "op_b"
        )

        st.divider()

        # -------------------------
        # VECTOR C
        # Only for Scalar Triple Product
        # -------------------------

        if operation == "Scalar Triple Product":

            system_c = st.selectbox(
                "Vector C coordinate system",
                SYSTEMS,
                key="op_system_c"
            )

            c, angles_c = vector_inputs(
                "Vector C",
                system_c,
                "op_c"
            )

        # -------------------------
        # CROSS PRODUCT RESULT
        # -------------------------

        if operation == "Cross Product":

            result_system = st.selectbox(
                "Result coordinate system",
                SYSTEMS,
                key="cross_result_system"
            )

            result_angles = basis_angles(
                result_system,
                "cross_result_basis",
                "Result basis"
            )

        # -------------------------
        # CALCULATE BUTTON
        # -------------------------

        run = st.button(
            "Calculate",
            type="primary",
            use_container_width=True
        )

        if run:

            try:

                # =====================
                # DOT PRODUCT
                # =====================

                if operation == "Dot Product":

                    value, cart_a, cart_b = dot_product(
                        a,
                        system_a,
                        angles_a,
                        b,
                        system_b,
                        angles_b
                    )

                    st.session_state["vector_result"] = {
                        "kind": "dot",
                        "value": value,
                        "plot": [
                            (cart_a, "Vector A"),
                            (cart_b, "Vector B")
                        ]
                    }

                # =====================
                # CROSS PRODUCT
                # =====================

                elif operation == "Cross Product":

                    result, cart_result, cart_a, cart_b = cross_product(
                        a,
                        system_a,
                        angles_a,
                        b,
                        system_b,
                        angles_b,
                        result_system,
                        result_angles
                    )

                    st.session_state["vector_result"] = {
                        "kind": "cross",
                        "result": result,
                        "cart": cart_result,
                        "target": result_system,
                        "plot": [
                            (cart_a, "Vector A"),
                            (cart_b, "Vector B"),
                            (cart_result, "A × B")
                        ]
                    }

                # =====================
                # SCALAR TRIPLE PRODUCT
                # =====================

                else:

                    value, cart_a, cart_b, cart_c = scalar_triple_product(
                        a,
                        system_a,
                        angles_a,
                        b,
                        system_b,
                        angles_b,
                        c,
                        system_c,
                        angles_c
                    )

                    # Calculate parallelepiped volume
                    volume = abs(value)

                    # Check coplanarity
                    scale = (
                        np.linalg.norm(cart_a)
                        * np.linalg.norm(cart_b)
                        * np.linalg.norm(cart_c)
                    )

                    tolerance = 1e-9 * max(scale, 1.0)

                    coplanar = abs(value) <= tolerance

                    st.session_state["vector_result"] = {
                        "kind": "triple",
                        "value": value,
                        "volume": volume,
                        "coplanar": coplanar,
                        "plot": [
                            (cart_a, "Vector A"),
                            (cart_b, "Vector B"),
                            (cart_c, "Vector C")
                        ]
                    }

            except (ValueError, TypeError) as exc:

                st.error(str(exc))


# =========================
# RESULTS
# =========================

with right:

    st.subheader("Results")

    data = st.session_state.get("vector_result")

    if data:

        # =====================
        # TRANSFORMATION RESULT
        # =====================

        if data["kind"] == "transform":

            st.success("Vector transformation completed.")

            st.markdown(
                f"**Components in {data['target']}**"
            )

            st.write(
                np.round(data["result"], 6)
            )

            st.markdown("**Cartesian components**")

            st.write(
                np.round(data["cart"], 6)
            )

            show_vector_plot(
                data["plot"],
                "3D Vector Transformation"
            )

        # =====================
        # DOT PRODUCT RESULT
        # =====================

        elif data["kind"] == "dot":

            st.success("Dot product calculated.")

            st.metric(
                "A · B",
                f"{data['value']:.6f}"
            )

            show_vector_plot(
                data["plot"],
                "3D Input Vectors"
            )

        # =====================
        # CROSS PRODUCT RESULT
        # =====================

        elif data["kind"] == "cross":

            st.success("Cross product calculated.")

            st.markdown(
                f"**A × B in {data['target']} components**"
            )

            st.write(
                np.round(data["result"], 6)
            )

            st.markdown("**Cartesian components**")

            st.write(
                np.round(data["cart"], 6)
            )

            show_vector_plot(
                data["plot"],
                "3D Cross Product"
            )

        # =====================
        # SCALAR TRIPLE PRODUCT RESULT
        # =====================

        elif data["kind"] == "triple":

            st.success("Scalar Triple Product calculated.")

            st.metric(
                "A · (B × C)",
                f"{data['value']:.6f}"
            )

            st.metric(
                "Parallelepiped Volume",
                f"{data['volume']:.6f}"
            )

            st.divider()

            if data["coplanar"]:

                st.success(
                    "The three vectors are COPLANAR."
                )

                st.write(
                    "Scalar Triple Product is approximately zero."
                )

            else:

                st.warning(
                    "The three vectors are NOT COPLANAR."
                )

                st.write(
                    "Scalar Triple Product is not zero."
                )

            show_vector_plot(
                data["plot"],
                "3D Scalar Triple Product"
            )

    else:

        st.info(
            "Choose an operation, enter the vector components, "
            "and calculate to see the result and 3D visualization."
        )


# =========================
# FOOTER
# =========================

st.divider()

st.caption(
    "Vector Representation | NumPy • Streamlit • Plotly"
)