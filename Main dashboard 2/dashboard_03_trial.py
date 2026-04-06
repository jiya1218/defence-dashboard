import streamlit as st
import pandas as pd
from gtts import gTTS
import tempfile
from streamlit_mic_recorder import speech_to_text

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Defence News Intelligence Dashboard",
    page_icon="🛰️",
    layout="wide"
)

FILE_NAME = "Data_collection3.xlsx"


# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():

    df = pd.read_excel(FILE_NAME)

    df["Date_parsed"] = pd.to_datetime(df["Date"], errors="coerce")

    df = df.sort_values("Date_parsed", ascending=False)

    df["Date"] = df["Date_parsed"].dt.strftime("%Y-%m-%d %H:%M:%S")

    return df


df = load_data()


# ---------------- HEADER ----------------
st.title("🛰️ Defence News Intelligence Dashboard")

st.divider()


# ---------------- SEARCH AREA ----------------
col1, col2 = st.columns([5,1])

with col1:

    search = st.text_input(
        "🔎 Search News",
        placeholder="Search defence procurement, drone, missile, navy etc..."
    )

with col2:

    voice_text = speech_to_text(
        language='en',
        start_prompt="🎤 Voice Search",
        stop_prompt="Stop",
        just_once=True,
        use_container_width=True
    )

    if voice_text:
        search = voice_text
        st.success(f"You said: {voice_text}")


# ---------------- FILTER ----------------
if search:

    filtered = df[
        df["Title"].str.contains(search, case=False, na=False)
        | df["Summary"].str.contains(search, case=False, na=False)
    ]

else:

    filtered = df


st.write(f"Articles Found: **{len(filtered)}**")

st.divider()


# ---------------- NEWS LIST ----------------
for i, row in filtered.iterrows():

    col1, col2 = st.columns([6,1])

    with col1:

        if st.button(row["Title"], key=i):

            st.session_state["selected"] = i

    with col2:

        st.caption(row["Date"])

    st.markdown(f"**Source:** {row['Source']}")

    st.divider()


# ---------------- ARTICLE SUMMARY ----------------
if "selected" in st.session_state:

    article = df.loc[st.session_state["selected"]]

    st.sidebar.title("🧠 AI Article Summary")

    st.sidebar.subheader(article["Title"])

    st.sidebar.write(article["Summary"])

    st.sidebar.markdown("---")

    st.sidebar.markdown(f"Source: **{article['Source']}**")

    st.sidebar.markdown(f"[Read Full Article]({article['Link']})")


    if st.sidebar.button("🔊 Read Summary"):

        tts = gTTS(article["Summary"])

        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")

        tts.save(temp_audio.name)

        audio_file = open(temp_audio.name, "rb")

        st.sidebar.audio(audio_file.read(), format="audio/mp3")
