import streamlit as st
import pandas as pd
import os
from datetime import datetime
from malaysia_backend import run_scraper

FILE_NAME = "bidsinfo_tenders.xlsx"

def malaysia_dashboard():
    st.set_page_config(layout="wide")
    st.title("🇲🇾 Malaysia Tender Intelligence Dashboard")

    # ---------------- LOAD DATA ----------------
    def load_data():
        if os.path.exists(FILE_NAME):
            df = pd.read_excel(FILE_NAME)
            df.columns = df.columns.str.strip()
            return df
        return pd.DataFrame()

    # ---------------- SESSION STATE INIT ----------------
    if "df" not in st.session_state:
        st.session_state.df = load_data()
    if "keyword" not in st.session_state:
        st.session_state.keyword = ""
    if "loc_filter" not in st.session_state:
        st.session_state.loc_filter = []
    if "ind_filter" not in st.session_state:
        st.session_state.ind_filter = []
    if "keyword_filter" not in st.session_state: # ✅ ADDED
        st.session_state.keyword_filter = [] # ✅ ADDED
    if "active_only" not in st.session_state:
        st.session_state.active_only = False
    if "sort_deadline" not in st.session_state:
        st.session_state.sort_deadline = False

    df = st.session_state.df

    # ---------------- REFRESH BUTTON ----------------
    if st.button("🔄 Refresh"):
        st.session_state.df = load_data()
        st.session_state.keyword = ""
        st.session_state.loc_filter = []
        st.session_state.ind_filter = []
        st.session_state.keyword_filter = [] # ✅ ADDED
        st.session_state.active_only = False
        st.session_state.sort_deadline = False
        st.rerun()

    # ---------------- SEARCH INPUT ----------------
    st.session_state.keyword = st.text_input(
        "🔍 Search / Add Keyword",
        value=st.session_state.keyword
    )

    # ---------------- GET LATEST DATA ----------------
    if st.button("🚀 Get Latest Data") and st.session_state.keyword.strip():
        with st.spinner("Fetching latest data..."):
            combined_df, new_df = run_scraper([st.session_state.keyword])
            st.session_state.df = combined_df
            df = combined_df
        st.success(f"✅ {len(new_df)} new records added")

    # ---------------- CLEAN DEADLINE ----------------
    if not df.empty and "Deadline" in df.columns:
        df["Deadline"] = pd.to_datetime(df["Deadline"], errors="coerce")

    # ---------------- KPI METRICS ----------------
    st.markdown("### 📊 Insights")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total", len(df))
    col2.metric("Keywords", df["Keyword"].nunique() if "Keyword" in df.columns else 0)
    col3.metric("Entities", df["Location"].nunique() if "Location" in df.columns else 0)
    col4.metric("Industry", df["Industry"].nunique() if "Industry" in df.columns else 0)

    # ---------------- FILTERS ----------------
    if "Location" in df.columns:
        st.session_state.loc_filter = st.multiselect(
            "Location",
            options=df["Location"].dropna().unique(),
            default=st.session_state.loc_filter
        )

    if "Industry" in df.columns:
        st.session_state.ind_filter = st.multiselect(
            "Industry",
            options=df["Industry"].dropna().unique(),
            default=st.session_state.ind_filter
        )

    # ✅ KEYWORD DROPDOWN FILTER (ONLY ADDITION)
    if "Keyword" in df.columns:
        st.session_state.keyword_filter = st.multiselect(
            "Keyword Filter",
            options=df["Keyword"].dropna().unique(),
            default=st.session_state.keyword_filter
        )

    st.session_state.active_only = st.checkbox(
        "Active Tenders (Deadline Today or Future)",
        value=st.session_state.active_only
    )

    st.session_state.sort_deadline = st.checkbox(
        "Sort by Deadline",
        value=st.session_state.sort_deadline
    )

    # ---------------- APPLY FILTERS ----------------
    filtered = df.copy()

    if "Location" in df.columns and st.session_state.loc_filter:
        filtered = filtered[filtered["Location"].isin(st.session_state.loc_filter)]

    if "Industry" in df.columns and st.session_state.ind_filter:
        filtered = filtered[filtered["Industry"].isin(st.session_state.ind_filter)]

    # ✅ APPLY KEYWORD FILTER (ONLY ADDITION)
    if "Keyword" in df.columns and st.session_state.keyword_filter:
        filtered = filtered[filtered["Keyword"].isin(st.session_state.keyword_filter)]

    # ✅ ORIGINAL SEARCH (UNCHANGED)
    if st.session_state.keyword.strip() and "Title" in df.columns:
        filtered = filtered[
            filtered["Title"].str.contains(
                st.session_state.keyword, case=False, na=False
            )
        ]

    if st.session_state.active_only and "Deadline" in df.columns:
        today = pd.Timestamp(datetime.today().date())
        filtered = filtered[filtered["Deadline"] >= today]

    if st.session_state.sort_deadline and "Deadline" in df.columns:
        filtered = filtered.sort_values("Deadline")

    # ---------------- DATA TABLE ----------------
    if not filtered.empty:

        display_df = filtered.copy()

        # NUMBERING
        display_df.insert(0, "No.", range(1, len(display_df) + 1))

        # KEYWORD POSITION + EMOJI
        if "Keyword" in display_df.columns:
            cols = display_df.columns.tolist()
            cols.remove("Keyword")
            cols.insert(1, "Keyword")
            display_df = display_df[cols]
            display_df["Keyword"] = display_df["Keyword"].astype(str).apply(lambda x: f"🟢 {x}")

        display_df["Select"] = False

        edited = st.data_editor(display_df, use_container_width=True, hide_index=True)

        selected = edited[edited["Select"]]

        if not selected.empty:
            st.download_button(
                "⬇ Download Selected Tenders",
                selected.drop(columns=["Select"]).to_csv(index=False),
                "selected_tenders.csv"
            )

    else:
        st.warning("❌ No data found")


# ---------------- RUN ----------------
if __name__ == "__main__":
    malaysia_dashboard()
