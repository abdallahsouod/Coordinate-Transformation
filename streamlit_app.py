import streamlit as st

st.set_page_config(
    page_title="Coordinate Transformation Studio",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

pages = {
    "Representations": [

        st.Page(
            "point_page.py",
            title="Point Representation",
            icon="📍",
            default=True
        ),

        st.Page(
            "vector_page.py",
            title="Vector Representation",
            icon="➡️"
        )

    ]
}

navigation = st.navigation(pages)

navigation.run()