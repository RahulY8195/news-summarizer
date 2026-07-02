import os

import requests
import streamlit as st

API_URL = os.environ.get("API_URL", "http://localhost:8000")
API_KEY = os.environ.get("API_KEY", "dev-key")

st.set_page_config(page_title="AI News Summarizer", page_icon="📰", layout="centered")
st.title("AI News Summarizer")
st.caption("Enter a topic, fetch live news, and get an AI summary of each article.")

topic = st.text_input("Topic", value="technology", placeholder="e.g. artificial intelligence")
fetch_clicked = st.button("Fetch & Summarize", type="primary")

if fetch_clicked and topic.strip():
    with st.spinner(f"Fetching and summarizing articles about \"{topic}\"..."):
        try:
            resp = requests.post(
                f"{API_URL}/articles/fetch",
                params={"query": topic},
                headers={"X-API-Key": API_KEY},
                timeout=300,
            )
            resp.raise_for_status()
            st.session_state["result"] = resp.json()
        except requests.exceptions.RequestException as exc:
            st.error(f"Request failed: {exc}")

result = st.session_state.get("result")
if result:
    st.subheader(f'Results for "{result["topic"]}"')
    st.caption(f"{result['fetched']} articles fetched this run, {result['new']} were new.")

    if not result["articles"]:
        st.info("No articles found yet for this topic. Try fetching first.")

    for article in result["articles"]:
        with st.container(border=True):
            st.markdown(f"**[{article['title']}]({article['url']})**")
            meta = article["source"]
            if article["published_at"]:
                meta += f" · {article['published_at']}"
            st.caption(meta)
            st.write(article["summary"] or "_No summary available._")
else:
    st.info("Enter a topic above and click **Fetch & Summarize** to get started.")
