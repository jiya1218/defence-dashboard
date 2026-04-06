import streamlit as st
import pandas as pd
import os
import threading
import time
import pytz
from datetime import datetime
from gem_backend import run_scraper

FILE_NAME = "gem_tenders.xlsx"
india_tz = pytz.timezone("Asia/Kolkata")

# --- ADD YOUR KEYWORDS HERE ---
MY_KEYWORDS = [] 

# ---------------- BACKGROUND SCHEDULER ----------------
def run_auto_job():
    """Background thread that runs every day at 11:00 AM IST"""
    while True:
        now = datetime.now(india_tz)
        if now.hour == 11 and now.minute == 0:
            print(f"[{now}] Initializing Scheduled Auto-Update...")
            run_scraper([], update_source="Auto")
            print(f"[{now}] Auto-Update Complete.")
            time.sleep(65)
        time.sleep(30)

if not any(t.name == "GemBackgroundJob" for t in threading.enumerate()):
    back_thread = threading.Thread(target=run_auto_job, name="GemBackgroundJob", daemon=True)
    back_thread.start()

def gem_dashboard():
    st.set_page_config(layout="wide")
    st.title("🇮🇳 GeM Tender Intelligence Dashboard")

    def load_data():
        if os.path.exists(FILE_NAME):
            df = pd.read_excel(FILE_NAME)
            df.columns = df.columns.str.strip()
            return df
        return pd.DataFrame()

    if "df_gem" not in st.session_state:
        st.session_state.df_gem = load_data()
    if "keyword_gem" not in st.session_state:
        st.session_state.keyword_gem = ""
    if "ministry_filter" not in st.session_state:
        st.session_state.ministry_filter = []
    if "category_filter" not in st.session_state:
        st.session_state.category_filter = []
    if "keyword_filter" not in st.session_state:
        st.session_state.keyword_filter = []
    if "active_only_gem" not in st.session_state:
        st.session_state.active_only_gem = False
    if "sort_deadline_gem" not in st.session_state:
        st.session_state.sort_deadline_gem = False

    df = st.session_state.df_gem

    if st.button("🔄 Refresh"):
        st.session_state.df_gem = load_data()
        st.session_state.keyword_gem = ""
        st.session_state.ministry_filter = []
        st.session_state.category_filter = []
        st.session_state.keyword_filter = []
        st.session_state.active_only_gem = False
        st.session_state.sort_deadline_gem = False
        st.rerun()

    st.session_state.keyword_gem = st.text_input(
        "🔍 Search / Add Keyword",
        value=st.session_state.keyword_gem
    )

    # UPDATED: Button now works without text in box
    if st.button("🚀 Get Latest Data"):
        # Logic: If box is empty, use MY_KEYWORDS list
        search_payload = [st.session_state.keyword_gem] if st.session_state.keyword_gem.strip() else MY_KEYWORDS
        
        left, center, right = st.columns([1, 2, 1])
        with center:
            st.markdown("### ⏳ Fetching Live Tender Data...")
            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(current, total, keyword, page):
                percent = int((current / total) * 100)
                progress_bar.progress(percent)
                status_text.markdown(f"**Progress:** {percent}% | 📌 Keyword: `{keyword}` | 📄 Page Scanned: {page}")

            combined_df, new_df = run_scraper(
                search_payload,
                update_source="Manual",
                progress_callback=update_progress
            )

            st.session_state.df_gem = combined_df
            df = combined_df
            progress_bar.progress(100)
            status_text.markdown("✅ **Completed Successfully**")
        st.success(f"✅ {len(new_df)} new records added")

    if "High Value Bid" in df.columns:
        df = df.drop(columns=["High Value Bid"])
    if "Bid Link" in df.columns:
        df = df.drop(columns=["Bid Link"])
    if "Start Date" in df.columns:
        df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce", utc=True)
        df["Start Date"] = df["Start Date"].dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    if "End Date" in df.columns:
        df["End Date"] = pd.to_datetime(df["End Date"], errors="coerce", utc=True)
        df["End Date"] = df["End Date"].dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)

    st.markdown("### 📊 Insights")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total", len(df))
    col2.metric("Keywords", df["Keyword"].nunique() if "Keyword" in df.columns else 0)
    col3.metric("Ministries", df["Ministry"].nunique() if "Ministry" in df.columns else 0)
    col4.metric("Categories", df["Category Name"].nunique() if "Category Name" in df.columns else 0)

    if "Keyword" in df.columns:
        st.session_state.keyword_filter = st.multiselect("Keyword Filter", df["Keyword"].dropna().unique(), default=st.session_state.keyword_filter)
    if "Ministry" in df.columns:
        st.session_state.ministry_filter = st.multiselect("Ministry", df["Ministry"].dropna().unique(), default=st.session_state.ministry_filter)
    if "Category Name" in df.columns:
        st.session_state.category_filter = st.multiselect("Category", df["Category Name"].dropna().unique(), default=st.session_state.category_filter)

    st.session_state.active_only_gem = st.checkbox("Active Tenders (Real-Time)", value=st.session_state.active_only_gem)
    st.session_state.sort_deadline_gem = st.checkbox("Sort by End Date", value=st.session_state.sort_deadline_gem)

    filtered = df.copy()
    if st.session_state.keyword_filter:
        filtered = filtered[filtered["Keyword"].isin(st.session_state.keyword_filter)]
    if st.session_state.ministry_filter:
        filtered = filtered[filtered["Ministry"].isin(st.session_state.ministry_filter)]
    if st.session_state.category_filter:
        filtered = filtered[filtered["Category Name"].isin(st.session_state.category_filter)]

    if st.session_state.keyword_gem.strip():
        search_input = st.session_state.keyword_gem.lower()
        if "+" in search_input:
            terms = [t.strip() for t in search_input.split("+")]
            filtered = filtered[filtered.apply(lambda row: all(term in " ".join(row.astype(str).str.lower()) for term in terms), axis=1)]
        else:
            filtered = filtered[filtered.apply(lambda row: row.astype(str).str.lower().str.contains(search_input, na=False).any(), axis=1)]

    if st.session_state.active_only_gem and "End Date" in filtered.columns:
        now = pd.Timestamp.now()
        filtered = filtered[filtered["End Date"] >= now]

    if st.session_state.sort_deadline_gem and "End Date" in filtered.columns:
        filtered = filtered.sort_values("End Date")

    filtered.index = range(1, len(filtered) + 1)
    if not filtered.empty:
        display_df = filtered.drop(columns=["Update Source"]) if "Update Source" in filtered.columns else filtered
        st.dataframe(display_df, use_container_width=True, height=600)
    else:
        st.warning("❌ No data found")

if __name__ == "__main__":
    gem_dashboard()
