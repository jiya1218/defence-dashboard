# dashboard_vietnam.py
import streamlit as st
import pandas as pd
import os
from datetime import datetime
from vietnam_backend import run_scraper

FILE_NAME = "vietnam_tenders.xlsx"

# --- ADD YOUR KEYWORDS HERE ---
MY_KEYWORDS = []

def vietnam_dashboard():
    st.set_page_config(layout="wide")
    st.title("🇻🇳 Vietnam Tender Intelligence Dashboard")

    def load_data():
        if os.path.exists(FILE_NAME):
            df = pd.read_excel(FILE_NAME)
            df.columns = df.columns.str.strip()
            return df
        return pd.DataFrame()

    if "df_vn" not in st.session_state:
        st.session_state.df_vn = load_data()
    if "keyword_vn" not in st.session_state:
        st.session_state.keyword_vn = ""
    if "province_filter" not in st.session_state:
        st.session_state.province_filter = []
    if "status_filter" not in st.session_state:
        st.session_state.status_filter = []
    if "keyword_filter" not in st.session_state:
        st.session_state.keyword_filter = []
    if "active_only_vn" not in st.session_state:
        st.session_state.active_only_vn = False
    if "sort_closing_date" not in st.session_state:
        st.session_state.sort_closing_date = False

    df = st.session_state.df_vn

    if st.button("🔄 Refresh"):
        st.session_state.df_vn = load_data()
        st.session_state.keyword_vn = ""
        st.session_state.province_filter = []
        st.session_state.status_filter = []
        st.session_state.keyword_filter = []
        st.session_state.active_only_vn = False
        st.session_state.sort_closing_date = False
        st.rerun()

    st.session_state.keyword_vn = st.text_input(
        "🔍 Search / Add Keyword",
        value=st.session_state.keyword_vn
    )

    # UPDATED: Button now works without text in box
    if st.button("🚀 Get Latest Data"):
        # Logic: If box is empty, use MY_KEYWORDS list
        search_payload = [st.session_state.keyword_vn] if st.session_state.keyword_vn.strip() else MY_KEYWORDS

        left, center, right = st.columns([1, 2, 1])
        with center:
            st.markdown("### ⏳ Fetching Live Data...")
            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(current, total, keyword, page):
                percent = int((current / total) * 100)
                progress_bar.progress(percent)
                status_text.markdown(f"""
                **Progress:** {percent}%  
                📌 Keyword: `{keyword}`  
                📄 Page: {page}
                """)

            combined_df, new_df = run_scraper(
                search_payload,
                progress_callback=update_progress
            )

            st.session_state.df_vn = combined_df
            df = combined_df
            progress_bar.progress(100)
            status_text.markdown("✅ Completed Successfully")
        st.success(f"✅ {len(new_df)} new records added")

    if not df.empty and "Closing Date (IST)" in df.columns:
        df["Closing Date (IST)"] = pd.to_datetime(df["Closing Date (IST)"], errors="coerce")

    st.markdown("### 📊 Insights")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Tenders", len(df))
    col2.metric("Keywords", df["Keyword EN"].nunique() if "Keyword EN" in df.columns else 0)
    col3.metric("Provinces", df["Province (EN)"].nunique() if "Province (EN)" in df.columns else 0)
    col4.metric("Status", df["Status"].nunique() if "Status" in df.columns else 0)

    st.markdown("### 🎯 Filters")
    if "Keyword EN" in df.columns:
        st.session_state.keyword_filter = st.multiselect("Keyword", options=df["Keyword EN"].dropna().unique(), default=st.session_state.keyword_filter)
    if "Province (EN)" in df.columns:
        st.session_state.province_filter = st.multiselect("Province", options=df["Province (EN)"].dropna().unique(), default=st.session_state.province_filter)
    if "Status" in df.columns:
        st.session_state.status_filter = st.multiselect("Status", options=df["Status"].dropna().unique(), default=st.session_state.status_filter)

    st.session_state.active_only_vn = st.checkbox("Active Tenders (Closing Date Today or Future)", value=st.session_state.active_only_vn)
    st.session_state.sort_closing_date = st.checkbox("Sort by Closing Date", value=st.session_state.sort_closing_date)

    filtered = df.copy()
    if st.session_state.keyword_filter:
        filtered = filtered[filtered["Keyword EN"].isin(st.session_state.keyword_filter)]
    if st.session_state.province_filter:
        filtered = filtered[filtered["Province (EN)"].isin(st.session_state.province_filter)]
    if st.session_state.status_filter:
        filtered = filtered[filtered["Status"].isin(st.session_state.status_filter)]

    if st.session_state.keyword_vn.strip():
        search_input = st.session_state.keyword_vn.lower().strip()
        if "+" in search_input:
            terms = [t.strip() for t in search_input.split("+")]
            filtered = filtered[filtered.apply(lambda row: all(term in " ".join(row.astype(str).str.lower()) for term in terms), axis=1)]
        else:
            filtered = filtered[filtered.apply(lambda row: row.astype(str).str.lower().str.contains(search_input, na=False).any(), axis=1)]

    if st.session_state.active_only_vn:
        today = pd.Timestamp(datetime.today().date())
        filtered = filtered[filtered["Closing Date (IST)"] >= today]

    if st.session_state.sort_closing_date and "Closing Date (IST)" in filtered.columns:
        filtered = filtered.sort_values("Closing Date (IST)")

    if not filtered.empty:
        filtered = filtered.reset_index(drop=True)
        if "No." in filtered.columns:
            filtered = filtered.drop(columns=["No."])
        filtered.insert(0, "No.", range(1, len(filtered) + 1))
        if "Keyword EN" in filtered.columns:
            cols = list(filtered.columns)
            cols.insert(1, cols.pop(cols.index("Keyword EN")))
            filtered = filtered[cols]
        st.dataframe(filtered, use_container_width=True, height=600, hide_index=True)
    else:
        st.warning("❌ No data found")

if __name__ == "__main__":
    vietnam_dashboard()
