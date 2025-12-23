import json
import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="AI Health Coach", layout="wide")

DATA_FILE = Path("health_data.json")

if not DATA_FILE.exists():
    st.error("Run camera_ai.py first!")
    st.stop()

with open(DATA_FILE) as f:
    data = json.load(f)

df = pd.DataFrame(data["history"])
df["date"] = pd.to_datetime(df["date"])

st.title("💪 AI Personal Health Coach Dashboard")
st.info("📸 Camera workout runs locally. Dashboard shows synced workout data.")

c1, c2, c3 = st.columns(3)
c1.metric("Total Reps", int(df["reps"].sum()))
c2.metric("Avg Form", int(df["form_score"].mean()))
c3.metric("Sessions", len(df))

fig1 = px.line(df, x="date", y="reps", title="Reps Over Time")
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.bar(df, x="date", y="form_score", title="Form Score")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Workout History")
st.table(df[["date","exercise","reps","form_score"]])
