import streamlit as st


def apply_dark_theme():
    """Apply dark theme styling"""
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0e1117 !important;
            color: #ffffff !important;
        }
        .stSidebar {
            background-color: #262730 !important;
        }
        .stSidebar .stSelectbox label, .stSidebar .stTextInput label, 
        .stSidebar .stMultiSelect label, .stSidebar .stRadio label,
        .stSidebar .stMarkdown, .stSidebar .stText, .stSidebar p, 
        .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar span {
            color: #ffffff !important;
        }
        .stSelectbox > div > div, .stSelectbox > div > div > div {
            background-color: #262730 !important;
            color: #ffffff !important;
        }
        .stTextInput > div > div > input {
            background-color: #262730 !important;
            color: #ffffff !important;
            border-color: #4a4a4a !important;
        }
        .stMultiSelect > div > div, .stMultiSelect > div > div > div {
            background-color: #262730 !important;
            color: #ffffff !important;
        }
        .stRadio > div {
            background-color: #262730 !important;
        }
        .stRadio > div > label > div {
            color: #ffffff !important;
        }
        .stExpander {
            background-color: #262730 !important;
            border: 1px solid #4a4a4a !important;
        }
        .stExpander > div > div > div > div {
            color: #ffffff !important;
        }
        .stButton > button {
            background-color: #262730 !important;
            color: #ffffff !important;
            border-color: #4a4a4a !important;
        }
        .stButton > button:hover {
            background-color: #4a4a4a !important;
        }
        .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, span, div {
            color: #ffffff !important;
        }
        .stSpinner > div > div {
            color: #ffffff !important;
        }
        .stSuccess, .stInfo, .stWarning, .stError {
            color: #ffffff !important;
        }
        div[data-testid="stMetricValue"] {
            color: #ffffff !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def apply_light_theme():
    """Apply light theme styling"""
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #ffffff !important;
            color: #262626 !important;
        }
        .stSidebar {
            background-color: #f0f2f6 !important;
        }
        .stSidebar .stSelectbox label, .stSidebar .stTextInput label, 
        .stSidebar .stMultiSelect label, .stSidebar .stRadio label,
        .stSidebar .stMarkdown, .stSidebar .stText, .stSidebar p, 
        .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar span {
            color: #262626 !important;
        }
        .stSelectbox > div > div, .stSelectbox > div > div > div {
            background-color: #ffffff !important;
            color: #262626 !important;
        }
        .stTextInput > div > div > input {
            background-color: #ffffff !important;
            color: #262626 !important;
            border-color: #cccccc !important;
        }
        .stMultiSelect > div > div, .stMultiSelect > div > div > div {
            background-color: #ffffff !important;
            color: #262626 !important;
        }
        .stRadio > div {
            background-color: #ffffff !important;
        }
        .stRadio > div > label > div {
            color: #262626 !important;
        }
        .stExpander {
            background-color: #ffffff !important;
            border: 1px solid #cccccc !important;
        }
        .stExpander > div > div > div > div {
            color: #262626 !important;
        }
        .stButton > button {
            background-color: #ffffff !important;
            color: #262626 !important;
            border-color: #cccccc !important;
        }
        .stButton > button:hover {
            background-color: #f0f2f6 !important;
        }
        .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, span, div {
            color: #262626 !important;
        }
        .stSpinner > div > div {
            color: #262626 !important;
        }
        .stSuccess, .stInfo, .stWarning, .stError {
            color: #262626 !important;
        }
        div[data-testid="stMetricValue"] {
            color: #262626 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def apply_theme(theme):
    """Apply the selected theme"""
    if theme == "Dark":
        apply_dark_theme()
    else:
        apply_light_theme()
