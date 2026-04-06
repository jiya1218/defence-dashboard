import streamlit as st
from PIL import Image

from dashboard_malaysia import malaysia_dashboard
from dashboard_global import global_dashboard
from dashboard_ted import ted_dashboard
from dashboard_gem import gem_dashboard
from dashboard_nepal import nepal_dashboard
from dashboard_vietnam import vietnam_dashboard


# ---------------- PAGE STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Tender Intelligence Dashboard",
    layout="wide"
)


# ---------------- STYLE CONFIG ----------------
TITLE_FONT_SIZE = "42px"
TITLE_FONT_WEIGHT = "900"

BUTTON_HEIGHT = "100px" # 🔥 increased slightly
BUTTON_FONT_SIZE = "24px" # 🔥 balanced size
BUTTON_BG_COLOR = "#ECF3F5"


# ---------------- CSS ----------------
st.markdown(f"""
<style>

/* Target ONLY main dashboard buttons */
.main-dashboard div.stButton > button {{
    height: {BUTTON_HEIGHT} !important;
    border-radius: 12px !important;
    background-color: {BUTTON_BG_COLOR} !important;
    color: black !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    padding: 5px !important;
    border: none !important;
}}

/* Button Text */
.main-dashboard div.stButton > button p {{
    font-size: {BUTTON_FONT_SIZE} !important;
    font-weight: 900 !important;
    margin: 0 !important;
}}

/* 🔥 Prevent layout stretching */
.main-dashboard .block-container {{
    padding-top: 0rem !important;
}}

/* Title Box */
.title-box {{
    background-color:#6A0DAD;
    padding:20px;
    border-radius:10px;
    color:white;
    font-size:{TITLE_FONT_SIZE};
    font-weight:{TITLE_FONT_WEIGHT};
}}

</style>
""", unsafe_allow_html=True)


# ---------------- HEADER ----------------
col1, col2 = st.columns([1,6])

with col1:
    try:
        image = Image.open(r"C:\Users\30212031\Downloads\45a2c12692f1f1a34789910689a0361b.jpg")
        st.image(image, width=150)
    except:
        st.error("Image not found. Check file path.")

with col2:
    st.markdown(f"""
    <div class="title-box">
        Adani Defence and Aerospace Tender Intelligence
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ---------------- MAIN DASHBOARD BUTTONS ----------------
st.markdown('<div class="main-dashboard">', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.session_state.page != "gem":
        if st.button("India (GeM)", use_container_width=True):
            st.session_state.page = "gem"
            st.rerun()

with col2:
    if st.session_state.page != "nepal":
        if st.button("Nepal (Bolpatra)", use_container_width=True):
            st.session_state.page = "nepal"
            st.rerun()


col3, col4 = st.columns(2)

with col3:
    if st.session_state.page != "vietnam":
        if st.button("Vietnam (Muasamcong)", use_container_width=True):
            st.session_state.page = "vietnam"
            st.rerun()

with col4:
    if st.session_state.page != "eu":
        if st.button("European Union (Tenders Electronic Daily)", use_container_width=True):
            st.session_state.page = "eu"
            st.rerun()


col5, col6 = st.columns(2)

with col5:
    if st.session_state.page != "malaysia":
        if st.button("Malaysia (Bidsinfo)", use_container_width=True):
            st.session_state.page = "malaysia"
            st.rerun()

with col6:
    if st.session_state.page != "global":
        if st.button("Global (Bidsinfo)", use_container_width=True):
            st.session_state.page = "global"
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)


# ---------------- PAGE NAVIGATION ----------------
if st.session_state.page == "malaysia":
    malaysia_dashboard()
    st.stop()

if st.session_state.page == "global":
    global_dashboard()
    st.stop()

if st.session_state.page == "eu":
    ted_dashboard()
    st.stop()

if st.session_state.page == "gem":
    gem_dashboard()
    st.stop()

if st.session_state.page == "nepal":
    nepal_dashboard()
    st.stop()

if st.session_state.page == "vietnam":
    vietnam_dashboard()
    st.stop()
