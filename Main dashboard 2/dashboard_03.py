import streamlit as st
import pandas as pd

def news_dashboard():
    FILE_NAME = "Data_collection3.xlsx"

    @st.cache_data
    def load_data():
        df = pd.read_excel(FILE_NAME)
        df["Date_parsed"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.sort_values("Date_parsed", ascending=False)
        df["Date"] = df["Date_parsed"].dt.strftime("%Y-%m-%d %H:%M:%S")
        return df

    try:
        df = load_data()
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return

    st.title("🛰️ Defence News Intelligence Dashboard")

    search = st.text_input("🔎 Search News", key="news_search")

    if search:
        keywords = [kw.strip() for kw in search.split("+") if kw.strip()]
        filtered = df.copy()
        for kw in keywords:
            filtered = filtered[
                filtered["Title"].str.contains(kw, case=False, na=False) |
                filtered["Summary"].str.contains(kw, case=False, na=False)
            ]
    else:
        filtered = df

    st.write(f"Articles Found: **{len(filtered)}**")

    # Display news list
    for i, row in filtered.iterrows():
        if st.button(row["Title"], key=f"news_{i}"):
            st.session_state["selected"] = i
        st.caption(row["Date"])
        st.write(f"Source: {row['Source']}")
        st.divider()

    # Sidebar logic - FORCED TO "Article Summary"
    if "selected" in st.session_state:
        article = df.loc[st.session_state["selected"]]
        
        # This block ensures the sidebar is wiped clean of any old "AI" text
        st.sidebar.empty()
        with st.sidebar:
            st.title("Article Summary")
            st.subheader(article["Title"])
            st.write(article["Summary"])
            st.write(f"**Source:** {article['Source']}")
            st.markdown(f"[Read Full Article]({article['Link']})")

if __name__ == "__main__":
    news_dashboard()
