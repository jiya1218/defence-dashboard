import streamlit as st
from PIL import Image
import pandas as pd

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Import the dashboard functions from your existing files
from dashboard_malaysia import malaysia_dashboard
from dashboard_global import global_dashboard
from dashboard_ted import ted_dashboard
from dashboard_gem import gem_dashboard
from dashboard_nepal import nepal_dashboard
from dashboard_vietnam import vietnam_dashboard

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Adani Defence Intelligence",
    page_icon="🛡️",
    layout="wide"
)

# --- INITIALIZE STATE ---
if "main_mode" not in st.session_state:
    st.session_state.main_mode = "home"
if "tender_page" not in st.session_state:
    st.session_state.tender_page = "home"
if "selected_news" not in st.session_state:
    st.session_state.selected_news = None

# --- STYLING ---
TITLE_FONT_SIZE = "40px"
TITLE_FONT_WEIGHT = "900"
BUTTON_HEIGHT = "100px"
BUTTON_FONT_SIZE = "24px"
BUTTON_BG_COLOR = "#ECF3F5"

st.markdown(f"""
<style>
    /* Main Dashboard Large Buttons */
    .main-nav div.stButton > button {{
        height: {BUTTON_HEIGHT} !important;
        border-radius: 12px !important;
        background-color: {BUTTON_BG_COLOR} !important;
        color: black !important;
        border: 2px solid #6A0DAD !important;
    }}
    .main-nav div.stButton > button p {{
        font-size: {BUTTON_FONT_SIZE} !important;
        font-weight: 900 !important;
    }}
    /* Title Box */
    .title-box {{
        background-color:#6A0DAD;
        padding:20px;
        border-radius:10px;
        color:white;
        text-align: center;
        font-size:{TITLE_FONT_SIZE};
        font-weight:{TITLE_FONT_WEIGHT};
    }}
</style>
""", unsafe_allow_html=True)

# --- DATA LOADING (NEWS) ---
@st.cache_data
def load_news_data():
    try:
        df = pd.read_excel("Data_collection3.xlsx")
        # convert date safely  
        df["Date_parsed"] = pd.to_datetime(df["Date"], errors="coerce")  
        # newest first  
        df = df.sort_values("Date_parsed", ascending=False)  
        # clean display format  
        df["Date_display"] = df["Date_parsed"].dt.strftime("%Y-%m-%d %H:%M:%S")  
        return df
    except Exception as e:
        st.error(f"Error loading Excel: {e}")
        return pd.DataFrame()

# --- HEADER (LOGO & TITLE) ---
header_col1, header_col2 = st.columns([1, 6])
# with header_col1:
#     try:
#         img = Image.open(r"C:\Users\30212031\Downloads\45a2c12692f1f1a34789910689a0361b.jpg")
#         st.image(img, width=150)
#     except:
#         st.error("Logo Path Error")

with header_col1:
    pass  # logo will be added later

with header_col2:
    st.markdown('<div class="title-box">Adani Defence & Aerospace Intelligence</div>', unsafe_allow_html=True)

# --- NAVIGATION ROW (Under Title/Logo) ---
nav_col1, nav_col2, _ = st.columns([1.5, 1.5, 7])

with nav_col1:
    if st.session_state.main_mode != "home":
        if st.button("🏠 MAIN HOME", use_container_width=True):
            st.session_state.main_mode = "home"
            st.session_state.tender_page = "home"
            st.session_state.selected_news = None
            st.rerun()

with nav_col2:
    if st.session_state.main_mode == "tender" and st.session_state.tender_page != "home":
        if st.button("⬅️ COUNTRIES", use_container_width=True):
            st.session_state.tender_page = "home"
            st.rerun()

st.divider()

# --- DASHBOARD LOGIC ---

# 1. MAIN HOME SELECTOR
if st.session_state.main_mode == "home":
    st.markdown('<div class="main-nav">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📰 DEFENCE NEWS\nINTELLIGENCE", use_container_width=True):
            st.session_state.main_mode = "news"
            st.rerun()
    with c2:
        if st.button("📑 TENDER\nINTELLIGENCE", use_container_width=True):
            st.session_state.main_mode = "tender"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 2. NEWS INTELLIGENCE MODE
elif st.session_state.main_mode == "news":
    st.title("🛰️ Defence News Intelligence Dashboard")
    df_news = load_news_data()

    if not df_news.empty:
        search = st.text_input("🔎 Search News", placeholder="Search defence procurement, drone, navy etc...")
        
        # Filtering logic
        if search:
            keywords = [kw.strip() for kw in search.split("+") if kw.strip()]
            filtered = df_news.copy()
            for kw in keywords:
                filtered = filtered[
                    filtered["Title"].astype(str).str.contains(kw, case=False, na=False) | 
                    filtered["Summary"].astype(str).str.contains(kw, case=False, na=False)
                ]
        else:
            filtered = df_news

        st.write(f"Articles Found: {len(filtered)}")
        st.divider()

        # Display News List
        for i, row in filtered.iterrows():
            col_t, col_d = st.columns([6, 1])
            with col_t:
                if st.button(row["Title"], key=f"news_btn_{i}"):
                    st.session_state.selected_news = i
            with col_d:
                st.caption(row["Date_display"])
            st.markdown(f"**Source:** {row['Source']}")
            st.divider()

        # Side Panel for AI Summary
        if st.session_state.selected_news is not None:
            article = df_news.loc[st.session_state.selected_news]
            st.sidebar.title("🧠 AI Article Summary")
            st.sidebar.subheader(article["Title"])
            st.sidebar.write(article["Summary"])
            st.sidebar.markdown("---")
            st.sidebar.markdown(f"Source: **{article['Source']}**")
            st.sidebar.markdown(f"[Read Full Article]({article['Link']})")
    else:
        st.warning("No data found in Data_collection3.xlsx")

# 3. TENDER INTELLIGENCE MODE
elif st.session_state.main_mode == "tender":
    if st.session_state.tender_page == "gem": gem_dashboard()
    elif st.session_state.tender_page == "nepal": nepal_dashboard()
    elif st.session_state.tender_page == "vietnam": vietnam_dashboard()
    elif st.session_state.tender_page == "eu": ted_dashboard()
    elif st.session_state.tender_page == "malaysia": malaysia_dashboard()
    elif st.session_state.tender_page == "global": global_dashboard()
    
    else:
        st.markdown('<div class="main-nav">', unsafe_allow_html=True)
        menu = [
            ("India (GeM)", "gem", "Nepal (Bolpatra)", "nepal"),
            ("Vietnam (Muasamcong)", "vietnam", "EU (TED)", "eu"),
            ("Malaysia (Bidsinfo)", "malaysia", "Global (Bidsinfo)", "global")
        ]
        for l1, c1, l2, c2 in menu:
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button(l1, use_container_width=True):
                    st.session_state.tender_page = c1
                    st.rerun()
            with col_b:
                if st.button(l2, use_container_width=True):
                    st.session_state.tender_page = c2
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
