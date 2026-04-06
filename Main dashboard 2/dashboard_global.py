import streamlit as st
import pandas as pd
import os
import threading
import time
import pytz
from datetime import datetime
from global_backend import run_scraper

FILE_NAME = "Global_bidsinfo_tenders.xlsx"
india_tz = pytz.timezone("Asia/Kolkata")

# --- ADD YOUR KEYWORDS HERE ---
MY_KEYWORDS = []

# --- BACKGROUND SCHEDULER LOGIC ---
def background_job():
    while True:
        now = datetime.now(india_tz)
        if now.hour == 11 and now.minute == 0:
            run_scraper([], update_source="Auto")
            time.sleep(65)
        time.sleep(30)

if not any(t.name == "GlobalScheduler" for t in threading.enumerate()):
    threading.Thread(target=background_job, name="GlobalScheduler", daemon=True).start()

def global_dashboard():
    st.set_page_config(layout="wide")
    st.title("🌍 Global Tender Intelligence Dashboard")

    def load_data():
        if os.path.exists(FILE_NAME):
            df = pd.read_excel(FILE_NAME)
            if df.empty: return pd.DataFrame()
            df.columns = df.columns.str.strip()
            return df
        return pd.DataFrame()

    if "df" not in st.session_state:
        st.session_state.df = load_data()

    if "keyword" not in st.session_state: st.session_state.keyword = ""
    if "loc_filter" not in st.session_state: st.session_state.loc_filter = []
    if "ind_filter" not in st.session_state: st.session_state.ind_filter = []
    if "keyword_filter" not in st.session_state: st.session_state.keyword_filter = []
    if "active_only" not in st.session_state: st.session_state.active_only = False
    if "sort_deadline" not in st.session_state: st.session_state.sort_deadline = False

    df = st.session_state.df

    if st.button("🔄 Refresh"):
        st.session_state.df = load_data()
        st.session_state.keyword = ""
        st.session_state.loc_filter = []
        st.session_state.ind_filter = []
        st.session_state.keyword_filter = []
        st.session_state.active_only = False
        st.session_state.sort_deadline = False
        st.rerun()

    st.session_state.keyword = st.text_input("🔍 Search / Add Keyword", value=st.session_state.keyword)

    # UPDATED: Removed check for keyword.strip() to allow empty search
    if st.button("🚀 Get Latest Data"):
        # Logic: Use input if available, else use MY_KEYWORDS
        search_payload = [st.session_state.keyword] if st.session_state.keyword.strip() else MY_KEYWORDS
        
        left, center, right = st.columns([1, 2, 1])
        with center:
            st.markdown("### ⏳ Fetching Live Tender Data...")
            progress_bar = st.progress(0)
            status_text = st.empty()
            def update_progress(current, total, keyword, page):
                percent = int((current / total) * 100)
                progress_bar.progress(percent)
                status_text.markdown(f"**Progress:** {percent}% | 📌 Keyword: `{keyword}` | 📄 Page: {page}")

            combined_df, new_df = run_scraper(search_payload, update_source="Manual", progress_callback=update_progress)
            st.session_state.df = combined_df
            df = combined_df
            progress_bar.progress(100)
            status_text.markdown("✅ Completed")
        st.success(f"✅ {len(new_df)} new records added")

    if not df.empty:
        df.columns = df.columns.str.strip()
        if "Keyword" not in df.columns: df["Keyword"] = ""
        if "Location" not in df.columns: df["Location"] = ""
        if "Industry" not in df.columns: df["Industry"] = ""
        if "Deadline" in df.columns: df["Deadline"] = pd.to_datetime(df["Deadline"], errors="coerce")

    st.markdown("### 📊 Insights")
    col1, col2, col3, col4 = st.columns(4)
    if not df.empty:
        col1.metric("Total", len(df))
        col2.metric("Keywords", df["Keyword"].nunique())
        col3.metric("Entities", df["Location"].nunique())
        col4.metric("Industry", df["Industry"].nunique())
    else:
        for c in [col1, col2, col3, col4]: c.metric("Total", 0)

    st.session_state.keyword_filter = st.multiselect("Keyword Filter", df["Keyword"].dropna().unique() if "Keyword" in df.columns else [], default=st.session_state.keyword_filter)
    st.session_state.loc_filter = st.multiselect("Location", df["Location"].dropna().unique() if "Location" in df.columns else [], default=st.session_state.loc_filter)
    st.session_state.ind_filter = st.multiselect("Industry", df["Industry"].dropna().unique() if "Industry" in df.columns else [], default=st.session_state.ind_filter)
    st.session_state.active_only = st.checkbox("Active Tenders (Deadline Today or Future)", value=st.session_state.active_only)
    st.session_state.sort_deadline = st.checkbox("Sort by Deadline", value=st.session_state.sort_deadline)

    filtered = df.copy()
    if "Keyword" in filtered.columns and st.session_state.keyword_filter:
        filtered = filtered[filtered["Keyword"].isin(st.session_state.keyword_filter)]
    if "Location" in filtered.columns and st.session_state.loc_filter:
        filtered = filtered[filtered["Location"].isin(st.session_state.loc_filter)]
    if "Industry" in filtered.columns and st.session_state.ind_filter:
        filtered = filtered[filtered["Industry"].isin(st.session_state.ind_filter)]

    if st.session_state.keyword.strip():
        search = st.session_state.keyword.lower()
        filtered = filtered[filtered.apply(lambda row: row.astype(str).str.lower().str.contains(search, na=False).any(), axis=1)]

    if st.session_state.active_only and "Deadline" in filtered.columns:
        filtered = filtered[filtered["Deadline"] >= pd.Timestamp(datetime.today().date())]

    if st.session_state.sort_deadline and "Deadline" in filtered.columns:
        filtered = filtered.sort_values("Deadline")

    if "Keyword" in filtered.columns:
        cols = ["Keyword"] + [c for c in filtered.columns if c != "Keyword"]
        filtered = filtered[cols]

    filtered.index = range(1, len(filtered) + 1)
    if not filtered.empty:
        display_df = filtered.drop(columns=["Update Source"]) if "Update Source" in filtered.columns else filtered
        st.dataframe(
            display_df,
            use_container_width=True,
            height=600,
            column_config={
                "Tender Link": st.column_config.LinkColumn("Tender Link", display_text="🔗 View Tender"),
                "Deadline": st.column_config.DateColumn("Deadline", format="DD-MM-YYYY")
            }
        )
    else:
        st.warning("❌ No data found")

if __name__ == "__main__":
    global_dashboard()
