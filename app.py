import streamlit as st
import re
from collections import Counter
from openai import OpenAI

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Job Application Intelligence Engine", layout="wide")
st.title("🧠 Job Application Intelligence Engine")
st.caption("AI-powered CV vs Job Description analysis")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -----------------------------
# SKILL EXTRACTION
# -----------------------------
STOPWORDS = {
    "and","or","with","for","the","a","an","to","of","in","experience",
    "skills","ability","strong","working","knowledge"
}

def extract_skills(text):
    words = re.findall(r"[a-zA-Z+#\.]{2,}", text.lower())
    return Counter([w for w in words if w not in STOPWORDS])

# -----------------------------
# CORE ANALYSIS
# -----------------------------
def analyze_fit(job_text, cv_text):
    job = extract_skills(job_text)
    cv = extract_skills(cv_text)

    job_set, cv_set = set(job), set(cv)
    matched = job_set & cv_set
    missing = job_set - cv_set

    score = round((len(matched) / len(job_set)) * 100, 2) if job_set else 0

    return score, matched, missing

# -----------------------------
# GPT INSIGHTS
# -----------------------------
def gpt_insights(score, matched, missing):
    prompt = f"""
You are a recruiter.

Candidate fit score: {score}/100

Matched skills: {list(matched)}
Missing skills: {list(missing)}

Explain:
1. Why the score is what it is
2. How the candidate should position themselves
3. What to improve on the CV
4. Recruiter talking points
5. Write a short tailored cover letter
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0.4
    )

    return response.choices[0].message.content

# -----------------------------
# INPUTS
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    job_description = st.text_area("🧾 Job Description", height=300)

with col2:
    cv_text = st.text_area("📄 Your CV", height=300)

# -----------------------------
# RUN
# -----------------------------
if st.button("Analyze Fit"):
    if not job_description or not cv_text:
        st.warning("Please fill in both fields.")
    else:
        score, matched, missing = analyze_fit(job_description, cv_text)

        st.subheader("📊 Fit Score")
        st.metric("Overall Match", f"{score} / 100")

        st.subheader("✅ Matched Skills")
        st.write(list(matched))

        st.subheader("❌ Missing Skills")
        st.write(list(missing))

        st.subheader("🧠 AI Recruiter Insights")
        with st.spinner("Thinking like a recruiter..."):
            insights = gpt_insights(score, matched, missing)
            st.write(insights)
