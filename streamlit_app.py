import json
import pandas as pd
import streamlit as st
from actionitems.pipeline import run

st.set_page_config(page_title="Meeting action items", page_icon="✅", layout="wide")
st.title("✅ Meeting action-item extractor")
mode = st.sidebar.radio("Extractor", ["rules", "llm"], help="'rules' works offline; 'llm' needs OPENAI_API_KEY")
min_conf = st.sidebar.slider("Minimum confidence", 0.0, 1.0, 0.3)
up = st.file_uploader("Upload a transcript (.txt)", type="txt")
text = up.getvalue().decode() if up else st.text_area("...or paste one", height=240,
        placeholder="# Meeting date: 2026-10-12\nPriya: Sam, can you review the pricing copy by Wednesday?")
if st.button("Extract action items", type="primary") and text.strip():
    items, ref = run(text, mode)
    rows = [i.to_dict() for i in items if i.confidence >= min_conf]
    if not rows:
        st.info("No action items found. Check that lines look like 'Name: sentence'.")
    else:
        df = pd.DataFrame(rows); df["flags"] = df["flags"].apply(", ".join)
        st.caption(f"Meeting date {ref} · {len(df)} action items")
        st.dataframe(df[["task", "owner", "deadline", "status", "confidence", "flags", "evidence"]], use_container_width=True)
        c1, c2 = st.columns(2)
        c1.download_button("Download CSV", df.to_csv(index=False), "action_items.csv")
        c2.download_button("Download JSON", json.dumps(rows, indent=2), "action_items.json")
