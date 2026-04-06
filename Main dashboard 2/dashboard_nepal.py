import streamlit as st
import pandas as pd
import os
from datetime import datetime
from nepal_backend import run_scraper

FILE_NAME = "nepal_tenders.xlsx"

# --- ADD YOUR KEYWORDS HERE ---
MY_KEYWORDS = []

def nepal_dashboard():
    st.set_page_config(layout="wide")
    st.title("🇳🇵 Nepal Tender Intelligence Dashboard")

    def load_data():
        if os.path.exists(FILE_NAME):
            df = pd.read_excel(FILE_NAME)
            df.columns = df.columns.str.strip()
            return df
        return pd.DataFrame()

    if "df_nepal" not in st.session_state:
        st.session_state.df_nepal = load_data()

    if "keyword_nepal" not in st.session_state: st.session_state.keyword_nepal = ""
    if "entity_filter" not in st.session_state: st.session_state.entity_filter = []
    if "method_filter" not in st.session_state: st.session_state.method_filter = []
    if "keyword_filter" not in st.session_state: st.session_state.keyword_filter = []
    if "active_only_nepal" not in st.session_state: st.session_state.active_only_nepal = False
    if "sort_deadline_nepal" not in st.session_state: st.session_state.sort_deadline_nepal = False

    df = st.session_state.df_nepal

    if st.button("🔄 Refresh"):
        st.session_state.df_nepal = load_data()
        st.session_state.keyword_nepal = ""
        st.session_state.entity_filter = []
        st.session_state.method_filter = []
        st.session_state.keyword_filter = []
        st.session_state.active_only_nepal = False
        st.session_state.sort_deadline_nepal = False
        st.rerun()

    st.session_state.keyword_nepal = st.text_input("🔍 Search / Add Keyword", value=st.session_state.keyword_nepal)

    # UPDATED: Button now works without text in box
    if st.button("🚀 Get Latest Data"):
        # Logic: If box is empty, use MY_KEYWORDS list
        search_payload = [st.session_state.keyword_nepal] if st.session_state.keyword_nepal.strip() else MY_KEYWORDS
        
        left, center, right = st.columns([1, 2, 1])
        with center:
            st.markdown("### ⏳ Fetching Live Tender Data...")
            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(current, total, keyword, page):
                percent = int((current / total) * 100)
                progress_bar.progress(percent)
                status_text.markdown(f"**Progress:** {percent}% | 📌 Keyword: `{keyword}` | 📄 Page: {page} / 2")

            combined_df, new_df = run_scraper(search_payload, progress_callback=update_progress)
            st.session_state.df_nepal = combined_df
            df = combined_df
            progress_bar.progress(100)
            status_text.markdown("✅ Completed")
        st.success(f"✅ {len(new_df)} new records added")

    if not df.empty and "Deadline" in df.columns:
        df["Deadline"] = pd.to_datetime(df["Deadline"], errors="coerce")

    st.markdown("### 📊 Insights")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total", len(df))
    col2.metric("Keywords", df["Keyword"].nunique() if "Keyword" in df.columns else 0)
    col3.metric("Public Entities", df["Public Entity"].nunique() if "Public Entity" in df.columns else 0)
    col4.metric("Procurement Methods", df["Procurement Method"].nunique() if "Procurement Method" in df.columns else 0)

    if "Keyword" in df.columns:
        st.session_state.keyword_filter = st.multiselect("Keyword Filter", df["Keyword"].dropna().unique(), default=st.session_state.keyword_filter)
    if "Public Entity" in df.columns:
        st.session_state.entity_filter = st.multiselect("Public Entity", df["Public Entity"].dropna().unique(), default=st.session_state.entity_filter)
    if "Procurement Method" in df.columns:
        st.session_state.method_filter = st.multiselect("Procurement Method", df["Procurement Method"].dropna().unique(), default=st.session_state.method_filter)

    st.session_state.active_only_nepal = st.checkbox("Active Tenders (Deadline Today or Future)", value=st.session_state.active_only_nepal)
    st.session_state.sort_deadline_nepal = st.checkbox("Sort by Deadline", value=st.session_state.sort_deadline_nepal)

    filtered = df.copy()
    if st.session_state.keyword_filter:
        filtered = filtered[filtered["Keyword"].isin(st.session_state.keyword_filter)]
    if st.session_state.entity_filter:
        filtered = filtered[filtered["Public Entity"].isin(st.session_state.entity_filter)]
    if st.session_state.method_filter:
        filtered = filtered[filtered["Procurement Method"].isin(st.session_state.method_filter)]

    if st.session_state.keyword_nepal.strip():
        search_input = st.session_state.keyword_nepal.lower()
        if "+" in search_input:
            terms = [t.strip() for t in search_input.split("+")]
            filtered = filtered[filtered.apply(lambda row: all(term in " ".join(row.astype(str).str.lower()) for term in terms), axis=1)]
        else:
            filtered = filtered[filtered.apply(lambda row: row.astype(str).str.lower().str.contains(search_input, na=False).any(), axis=1)]

    if "Deadline" in filtered.columns:
        filtered["Deadline"] = pd.to_datetime(filtered["Deadline"], errors="coerce").dt.tz_localize(None)

    if st.session_state.active_only_nepal:
        today = pd.Timestamp(datetime.today().date())
        filtered = filtered[filtered["Deadline"] >= today]

    if st.session_state.sort_deadline_nepal:
        filtered = filtered.sort_values("Deadline")

    if "Keyword" in filtered.columns:
        cols = ["Keyword"] + [c for c in filtered.columns if c != "Keyword"]
        filtered = filtered[cols]

    filtered.index = range(1, len(filtered) + 1)

    if not filtered.empty:
        st.dataframe(filtered, use_container_width=True, height=600)
    else:
        st.warning("❌ No data found")

if __name__ == "__main__":
    nepal_dashboard()

