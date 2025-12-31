import streamlit as st
import openai
import re

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="Job Application Intelligence Engine", layout="wide")

st.title("🧠 Job Application Intelligence Engine")
st.caption("AI-powered CV vs Job Description analysis")

# -------------------------------
# API KEY (Streamlit Secrets)
# -------------------------------
openai.api_key = st.secrets["OPENAI_API_KEY"]

# -------------------------------
# GPT: Extract JD Intelligence
# -------------------------------
def extract_jd_skills(jd_text):
    prompt = f"""
    Extract key skills, tools, and competencies from this job description.
    Return ONLY a comma-separated list.

    Job Description:
    {jd_text}
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    skills_text = response.choices[0].message["content"].lower()
    return [s.strip() for s in skills_text.split(",") if s.strip()]

# -------------------------------
# MATCHING LOGIC
# -------------------------------
def extract_cv_skills(cv_text):
    return set(re.findall(r"[a-zA-Z+/]+", cv_text.lower()))

# -------------------------------
# ANALYSIS
# -------------------------------
def analyze_fit(cv_text, jd_text):
    jd_skills = set(extract_jd_skills(jd_text))
    cv_skills = extract_cv_skills(cv_text)

    matched = sorted(jd_skills & cv_skills)
    missing = sorted(jd_skills - cv_skills)

    score = round((len(matched) / len(jd_skills)) * 100, 2) if jd_skills else 0

    return score, matched, missing

# -------------------------------
# CV IMPROVEMENT SUGGESTIONS
# -------------------------------
def cv_suggestions(missing):
    return [
        f"Add experience or projects demonstrating **{skill}**."
        for skill in missing
    ]

# -------------------------------
# COVER LETTER
# -------------------------------
def generate_cover_letter(cv_text, jd_text):
    prompt = f"""
    Write a short, professional cover letter tailored to the job description.

    CV:
    {cv_text}

    Job Description:
    {jd_text}
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    return response.choices[0].message["content"]

# -------------------------------
# UI
# -------------------------------
jd_text = st.text_area("📌 Paste Job Description", height=220)
cv_text = st.text_area("📄 Paste Your CV", height=220)

if st.button("🔍 Analyze Fit"):
    if not jd_text or not cv_text:
        st.warning("Please paste both the job description and your CV.")
        st.stop()

    score, core_matched, missing_core = analyze_fit(cv_text, jd_text)

    st.subheader("📊 Fit Score")
    st.metric("Match Percentage", f"{score}%")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("✅ Matched Skills")
        st.write(core_matched if core_matched else "No strong matches detected.")

    with col2:
        st.subheader("❌ Missing Skills")
        st.write(missing_core if missing_core else "No major gaps found.")

    st.subheader("🛠 CV Improvement Suggestions")
    for tip in cv_suggestions(missing_core):
        st.write(f"- {tip}")

    st.subheader("💬 Recruiter Talking Points")
    for skill in core_matched:
        st.write(f"- Demonstrated experience in **{skill}**.")
    for skill in missing_core:
        st.write(f"- Actively developing skills in **{skill}**.")

    st.subheader("✉️ Generated Cover Letter")
    st.write(generate_cover_letter(cv_text, jd_text))
