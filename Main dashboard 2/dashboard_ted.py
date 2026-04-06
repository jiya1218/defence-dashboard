import streamlit as st
import pandas as pd
import os
import threading
import time
import pytz
from datetime import datetime
from ted_backend import run_scraper

FILE_NAME = "EU_TED_Tenders.xlsx"
india_tz = pytz.timezone("Asia/Kolkata")

# --- ADD YOUR KEYWORDS HERE ---
MY_KEYWORDS = []

# --- BACKGROUND SCHEDULER ---
def background_scheduler():
    while True:
        now = datetime.now(india_tz)
        if now.hour == 11 and now.minute == 0:
            run_scraper([], update_source="Auto")
            time.sleep(65)
        time.sleep(30)

if not any(t.name == "TEDScheduler" for t in threading.enumerate()):
    threading.Thread(target=background_scheduler, name="TEDScheduler", daemon=True).start()

def ted_dashboard():
    st.set_page_config(layout="wide")
    st.title("🇪🇺 EU TED Tender Intelligence Dashboard")

    def load_data():
        if os.path.exists(FILE_NAME):
            df = pd.read_excel(FILE_NAME)
            df.columns = df.columns.str.strip()
            return df
        return pd.DataFrame()

    if "df" not in st.session_state:
        st.session_state.df = load_data()

    if "keyword" not in st.session_state: st.session_state.keyword = ""
    if "keyword_filter" not in st.session_state: st.session_state.keyword_filter = []
    if "country_filter" not in st.session_state: st.session_state.country_filter = []
    if "contract_filter" not in st.session_state: st.session_state.contract_filter = []
    if "active_only" not in st.session_state: st.session_state.active_only = False
    if "sort_deadline" not in st.session_state: st.session_state.sort_deadline = False

    df = st.session_state.df

    if st.button("🔄 Refresh"):
        st.session_state.df = load_data()
        st.session_state.keyword = ""
        st.session_state.keyword_filter = []
        st.session_state.country_filter = []
        st.session_state.contract_filter = []
        st.session_state.active_only = False
        st.session_state.sort_deadline = False
        st.rerun()

    st.session_state.keyword = st.text_input("🔍 Search / Add Keyword", value=st.session_state.keyword)

    # UPDATED: Button now works without text in box
    if st.button("🚀 Get Latest Data"):
        # Logic: If box is empty, use MY_KEYWORDS list
        search_payload = [st.session_state.keyword] if st.session_state.keyword.strip() else MY_KEYWORDS
        
        left, center, right = st.columns([1, 2, 1])
        with center:
            st.markdown("### ⏳ Fetching Live Data...")
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
            status_text.markdown("✅ Completed Successfully")
        st.success(f"✅ {len(new_df)} new records added")

    if not df.empty and "Deadline" in df.columns:
        df["Deadline"] = pd.to_datetime(df["Deadline"], errors="coerce")

    st.markdown("### 📊 Insights")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total", len(df))
    col2.metric("Keywords", df["Keyword"].nunique() if "Keyword" in df.columns else 0)
    col3.metric("Countries", df["Location"].nunique() if "Location" in df.columns else 0)
    col4.metric("Contract Types", df["Industry"].nunique() if "Industry" in df.columns else 0)

    if "Keyword" in df.columns:
        st.session_state.keyword_filter = st.multiselect("Keyword", df["Keyword"].dropna().unique(), default=st.session_state.keyword_filter)
    if "Location" in df.columns:
        st.session_state.country_filter = st.multiselect("Country", df["Location"].dropna().unique(), default=st.session_state.country_filter)
    if "Industry" in df.columns:
        st.session_state.contract_filter = st.multiselect("Contract Type", df["Industry"].dropna().unique(), default=st.session_state.contract_filter)

    st.session_state.active_only = st.checkbox("Active Tenders (Real-Time)", value=st.session_state.active_only)
    st.session_state.sort_deadline = st.checkbox("Sort by Deadline", value=st.session_state.sort_deadline)

    filtered = df.copy()
    if st.session_state.keyword_filter:
        filtered = filtered[filtered["Keyword"].isin(st.session_state.keyword_filter)]
    if st.session_state.country_filter:
        filtered = filtered[filtered["Location"].isin(st.session_state.country_filter)]
    if st.session_state.contract_filter:
        filtered = filtered[filtered["Industry"].isin(st.session_state.contract_filter)]

    if st.session_state.keyword.strip():
        search_input = st.session_state.keyword.lower()
        if "+" in search_input:
            terms = [t.strip() for t in search_input.split("+")]
            filtered = filtered[filtered.apply(lambda row: all(term in " ".join(row.astype(str).str.lower()) for term in terms), axis=1)]
        else:
            filtered = filtered[filtered.apply(lambda row: row.astype(str).str.lower().str.contains(search_input, na=False).any(), axis=1)]

    if st.session_state.active_only and "Deadline" in filtered.columns:
        filtered = filtered[filtered["Deadline"] >= pd.Timestamp.now()]

    if st.session_state.sort_deadline and "Deadline" in filtered.columns:
        filtered = filtered.sort_values("Deadline")

    filtered.index = range(1, len(filtered) + 1)

    if "Keyword" in filtered.columns:
        cols = ["Keyword"] + [c for c in filtered.columns if c != "Keyword"]
        filtered = filtered[cols]

    if not filtered.empty:
        display_df = filtered.drop(columns=["Update Source"]) if "Update Source" in filtered.columns else filtered
        st.dataframe(
            display_df,
            use_container_width=True,
            height=600,
            column_config={
                "Tender Link": st.column_config.LinkColumn("Tender Link", display_text="🔗 View Tender")
            }
        )
    else:
        st.warning("❌ No data found")

if __name__ == "__main__":
    ted_dashboard()
