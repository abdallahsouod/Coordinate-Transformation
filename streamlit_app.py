import numpy as np
import streamlit as st
import plotly.graph_objects as go

from transformations import transform, to_cartesian


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Coordinate Transformation Studio",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================================================
# CONSTANTS
# ==================================================

SYSTEMS = ["Cartesian", "Cylindrical", "Spherical"]

COORDINATES = {
    "Cartesian": ["x", "y", "z"],
    "Cylindrical": ["rho (ρ)", "phi (φ) [deg]", "z"],
    "Spherical": [
        "r",
        "theta (θ) [deg]",
        "phi (φ) [deg]",
    ],
}


# ==================================================
# SESSION STATE
# ==================================================

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "last_plot" not in st.session_state:
    st.session_state.last_plot = None


# ==================================================
# CUSTOM STYLING
# ==================================================

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
    unsafe_allow_html=True,
)


# ==================================================
# HEADER
# ==================================================

st.markdown(
    """
    <div class="hero">
        <h1>📐 Coordinate Transformation Studio</h1>
        <p>
            Convert coordinate systems, perform vector operations,
            and explore 3D geometry interactively.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.markdown("## ⚙️ Operations")

    operation = st.radio(
        "Choose an operation",
        [
            "Convert Coordinates",
            "Vector Addition",
            "Vector Subtraction",
        ],
    )

    st.divider()

    st.markdown("### Coordinate Systems")

    st.markdown(
        """
        **Cartesian**

        `(x, y, z)`

        **Cylindrical**

        `(ρ, φ, z)`

        **Spherical**

        `(r, θ, φ)`
        """
    )

    st.caption("All angles are entered in degrees.")


# ==================================================
# INPUT FUNCTIONS
# ==================================================

def coordinate_inputs(title, system, key_prefix):

    st.markdown(f"#### {title}")

    values = []

    labels = COORDINATES[system]

    columns = st.columns(3)

    for i, label in enumerate(labels):

        with columns[i]:

            value = st.number_input(
                label,
                value=0.0,
                key=f"{key_prefix}_{system}_{i}",
                format="%.6f",
            )

            values.append(float(value))

    return values


def show_metrics(vector):

    x, y, z = [float(value) for value in vector]

    columns = st.columns(3)

    columns[0].metric("X Component", f"{x:.4f}")
    columns[1].metric("Y Component", f"{y:.4f}")
    columns[2].metric("Z Component", f"{z:.4f}")


def show_coordinates(values, system):

    labels = COORDINATES[system]

    for label, value in zip(labels, values):

        st.write(f"**{label}:** `{float(value):.4f}`")


# ==================================================
# 3D PLOT
# ==================================================

def create_3d_plot(vectors, title, addition=False):

    fig = go.Figure()

    all_values = [0.0]

    for vector, _, _ in vectors:

        all_values.extend(
            [abs(float(value)) for value in vector]
        )

    limit = max(all_values + [1.0]) * 1.3

    # X-axis
    fig.add_trace(
        go.Scatter3d(
            x=[-limit, limit],
            y=[0, 0],
            z=[0, 0],
            mode="lines",
            name="X-axis",
            line=dict(color="#ff6b6b", width=5),
        )
    )

    # Y-axis
    fig.add_trace(
        go.Scatter3d(
            x=[0, 0],
            y=[-limit, limit],
            z=[0, 0],
            mode="lines",
            name="Y-axis",
            line=dict(color="#4ade80", width=5),
        )
    )

    # Z-axis
    fig.add_trace(
        go.Scatter3d(
            x=[0, 0],
            y=[0, 0],
            z=[-limit, limit],
            mode="lines",
            name="Z-axis",
            line=dict(color="#60a5fa", width=5),
        )
    )

    # Origin
    fig.add_trace(
        go.Scatter3d(
            x=[0],
            y=[0],
            z=[0],
            mode="markers+text",
            text=["Origin"],
            textposition="bottom right",
            name="Origin",
            marker=dict(size=5, color="white"),
        )
    )

    colors = {
        "Point P": "#22d3ee",
        "Vector A": "#22d3ee",
        "Vector B": "#fbbf24",
        "Result": "#c084fc",
        "-Vector B": "#fb7185",
    }

    # Draw vectors
    for vector, name, _ in vectors:

        x, y, z = [float(value) for value in vector]

        color = colors.get(name, "#e5e7eb")

        fig.add_trace(
            go.Scatter3d(
                x=[0, x],
                y=[0, y],
                z=[0, z],
                mode="lines+markers+text",
                text=["", name],
                textposition="top center",
                name=f"{name}: ({x:.2f}, {y:.2f}, {z:.2f})",
                line=dict(color=color, width=7),
                marker=dict(size=4, color=color),
            )
        )

        # Arrowhead at the endpoint
        norm = np.linalg.norm([x, y, z])

        if norm > 1e-10:

            arrow_size = limit * 0.06

            fig.add_trace(
                go.Cone(
                    x=[x],
                    y=[y],
                    z=[z],
                    u=[x / norm * arrow_size],
                    v=[y / norm * arrow_size],
                    w=[z / norm * arrow_size],
                    anchor="tip",
                    sizemode="absolute",
                    sizeref=arrow_size,
                    colorscale=[
                        [0, color],
                        [1, color],
                    ],
                    showscale=False,
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

    # Parallelogram construction for addition
    if addition and len(vectors) >= 3:

        a = np.asarray(vectors[0][0], dtype=float)
        b = np.asarray(vectors[1][0], dtype=float)
        result = a + b

        fig.add_trace(
            go.Scatter3d(
                x=[a[0], result[0]],
                y=[a[1], result[1]],
                z=[a[2], result[2]],
                mode="lines",
                name="Parallelogram",
                line=dict(
                    color="#22d3ee",
                    width=3,
                    dash="dash",
                ),
            )
        )

        fig.add_trace(
            go.Scatter3d(
                x=[b[0], result[0]],
                y=[b[1], result[1]],
                z=[b[2], result[2]],
                mode="lines",
                showlegend=False,
                line=dict(
                    color="#fbbf24",
                    width=3,
                    dash="dash",
                ),
            )
        )

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=20, color="#f8fafc"),
        ),
        height=580,
        margin=dict(l=0, r=0, t=60, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e5e7eb"),
        legend=dict(
            bgcolor="rgba(15,23,42,0.75)",
            bordercolor="#334155",
            borderwidth=1,
        ),
        scene=dict(
            xaxis=dict(
                title="X",
                range=[-limit, limit],
                backgroundcolor="#111827",
                gridcolor="#334155",
            ),
            yaxis=dict(
                title="Y",
                range=[-limit, limit],
                backgroundcolor="#111827",
                gridcolor="#334155",
            ),
            zaxis=dict(
                title="Z",
                range=[-limit, limit],
                backgroundcolor="#111827",
                gridcolor="#334155",
            ),
            aspectmode="cube",
            camera=dict(
                eye=dict(x=1.6, y=1.6, z=1.3)
            ),
        ),
    )

    return fig


# ==================================================
# MAIN LAYOUT
# ==================================================

left, right = st.columns(
    [0.95, 1.05],
    gap="large",
)


# ==================================================
# INPUT PANEL
# ==================================================

with left:

    st.markdown("## 🧮 Input")

    if operation == "Convert Coordinates":

        source = st.selectbox(
            "Source Coordinate System",
            SYSTEMS,
            key="convert_source",
        )

        target = st.selectbox(
            "Target Coordinate System",
            SYSTEMS,
            key="convert_target",
        )

        values = coordinate_inputs(
            "Input Coordinates",
            source,
            "convert",
        )

        run_button = st.button(
            "🔄 Convert Coordinates",
            type="primary",
            use_container_width=True,
        )

        if run_button:

            try:

                cartesian = to_cartesian(values, source)

                result = transform(
                    values,
                    source,
                    target,
                )

                st.session_state.last_result = {
                    "kind": "convert",
                    "source": source,
                    "target": target,
                    "cartesian": cartesian,
                    "result": result,
                }

                st.session_state.last_plot = {
                    "vectors": [
                        (cartesian, "Point P", None)
                    ],
                    "title": "3D Coordinate Visualization",
                    "addition": False,
                }

            except (ValueError, TypeError) as error:

                st.error(f"Conversion failed: {error}")

    else:

        st.caption(
            "Vector A and Vector B can use different coordinate systems."
        )

        source_a = st.selectbox(
            "Vector A Coordinate System",
            SYSTEMS,
            key="source_a",
        )

        values_a = coordinate_inputs(
            "Vector A",
            source_a,
            "vector_a",
        )

        st.divider()

        source_b = st.selectbox(
            "Vector B Coordinate System",
            SYSTEMS,
            key="source_b",
        )

        values_b = coordinate_inputs(
            "Vector B",
            source_b,
            "vector_b",
        )

        target = st.selectbox(
            "Result Coordinate System",
            SYSTEMS,
            key="vector_target",
        )

        run_button = st.button(
            "▶ Apply Operation",
            type="primary",
            use_container_width=True,
        )

        if run_button:

            try:

                cart_a = to_cartesian(
                    values_a,
                    source_a,
                )

                cart_b = to_cartesian(
                    values_b,
                    source_b,
                )

                if operation == "Vector Addition":

                    result_cart = cart_a + cart_b

                    symbol = "+"

                    vectors = [
                        (cart_a, "Vector A", None),
                        (cart_b, "Vector B", None),
                        (result_cart, "Result", None),
                    ]

                    title = "Vector Addition: A + B"

                    addition = True

                else:

                    result_cart = cart_a - cart_b

                    symbol = "−"

                    vectors = [
                        (cart_a, "Vector A", None),
                        (cart_b, "Vector B", None),
                        (result_cart, "Result", None),
                        (-cart_b, "-Vector B", None),
                    ]

                    title = "Vector Subtraction: A − B"

                    addition = False

                result_target = transform(
                    result_cart.tolist(),
                    "Cartesian",
                    target,
                )

                st.session_state.last_result = {
                    "kind": "vector",
                    "symbol": symbol,
                    "target": target,
                    "cart_a": cart_a,
                    "cart_b": cart_b,
                    "cartesian": result_cart,
                    "result": result_target,
                }

                st.session_state.last_plot = {
                    "vectors": vectors,
                    "title": title,
                    "addition": addition,
                }

            except (ValueError, TypeError) as error:

                st.error(f"Vector operation failed: {error}")


# ==================================================
# RESULTS PANEL
# ==================================================

with right:

    st.markdown("## 📊 Results")

    result_data = st.session_state.last_result
    plot_data = st.session_state.last_plot

    if result_data is not None:

        if result_data["kind"] == "convert":

            st.success(
                f"Converted from {result_data['source']} "
                f"to {result_data['target']}."
            )

            st.markdown("### Converted Coordinates")

            show_coordinates(
                result_data["result"],
                result_data["target"],
            )

            st.markdown("### Cartesian Components")

            show_metrics(result_data["cartesian"])

        else:

            st.success(
                f"Operation completed: "
                f"A {result_data['symbol']} B"
            )

            st.markdown(
                "### Result in Cartesian Coordinates"
            )

            show_metrics(result_data["cartesian"])

            st.markdown(
                f"### Result in {result_data['target']} Coordinates"
            )

            show_coordinates(
                result_data["result"],
                result_data["target"],
            )

            with st.expander(
                "View input vectors in Cartesian coordinates"
            ):

                st.write(
                    "Vector A:",
                    np.round(result_data["cart_a"], 4),
                )

                st.write(
                    "Vector B:",
                    np.round(result_data["cart_b"], 4),
                )

    else:

        st.info(
            "Enter your coordinates and run an operation "
            "to display the result."
        )

    if plot_data is not None:

        st.plotly_chart(
            create_3d_plot(
                plot_data["vectors"],
                plot_data["title"],
                plot_data["addition"],
            ),
            use_container_width=True,
            config={
                "displaylogo": False,
                "scrollZoom": True,
            },
        )

    else:

        st.markdown(
            """
            ### Interactive 3D Plot

            Your coordinate or vector visualization
            will appear here after you run an operation.
            """
        )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "Coordinate Transformation Studio | "
    "Python • Streamlit • NumPy • Plotly"
)

