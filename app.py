import streamlit as st
import re
from openai import OpenAI

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="Job Application Intelligence Engine",
    layout="wide"
)

st.title("🧠 Job Application Intelligence Engine")
st.caption("AI-powered CV analysis against any job description")

# -----------------------------------
# API KEY
# -----------------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -----------------------------------
# GPT: Extract JD Intelligence
# -----------------------------------
def extract_jd_skills(jd_text):
    prompt = f"""
    Extract the core skills, tools, and competencies required from this job description.
    Return them as a clean comma-separated list.

    Job Description:
    {jd_text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    skills = response.choices[0].message.content.lower()
    return [s.strip() for s in skills.split(",") if s.strip()]

# -----------------------------------
# MATCHING LOGIC
# -----------------------------------
def extract_cv_skills(cv_text):
    words = re.findall(r"[a-zA-Z+/]+", cv_text.lower())
    return set(words)

# -----------------------------------
# ANALYSIS
# -----------------------------------
def analyze_fit(cv_text, jd_text):
    jd_skills = set(extract_jd_skills(jd_text))
    cv_skills = extract_cv_skills(cv_text)

    matched = sorted(jd_skills.intersection(cv_skills))
    missing = sorted(jd_skills.difference(cv_skills))

    fit_score = round((len(matched) / len(jd_skills)) * 100, 2) if jd_skills else 0

    return {
        "fit_score": fit_score,
        "core_matched": matched,
        "missing_core": missing
    }

# -----------------------------------
# CV IMPROVEMENT SUGGESTIONS
# -----------------------------------
def cv_improvements(missing_skills):
    suggestions = []
    for skill in missing_skills:
        suggestions.append(
            f"Add a bullet point demonstrating hands-on experience or learning in **{skill}**."
        )
    return suggestions

# -----------------------------------
# COVER LETTER
# -----------------------------------
def generate_cover_letter(cv_text, jd_text):
    prompt = f"""
    Write a concise, professional cover letter tailored to the job description.
    Emphasize transferable skills and growth mindset.

    CV:
    {cv_text}

    Job Description:
    {jd_text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# -----------------------------------
# UI INPUTS
# -----------------------------------
jd_text = st.text_area("📌 Paste Job Description", height=220)
cv_text = st.text_area("📄 Paste Your CV", height=220)

if st.button("🔍 Analyze Fit"):
    if not jd_text or not cv_text:
        st.warning("Please paste both the Job Description and your CV.")
    else:
        result = analyze_fit(cv_text, jd_text)

        fit_score = result["fit_score"]
        core_matched = result["core_matched"]
        missing_core = result["missing_core"]

        # -----------------------------------
        # RESULTS
        # -----------------------------------
        st.subheader("📊 Fit Score")
        st.metric("Overall Match (%)", fit_score)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("✅ Matched Skills")
            st.write(core_matched if core_matched else "No strong matches found.")

        with col2:
            st.subheader("❌ Missing Skills")
            st.write(missing_core if missing_core else "No major gaps identified.")

        # -----------------------------------
        # CV IMPROVEMENT SUGGESTIONS
        # -----------------------------------
        st.subheader("🛠 CV Improvement Suggestions")
        for tip in cv_improvements(missing_core):
            st.write(f"- {tip}")

        # -----------------------------------
        # RECRUITER TALKING POINTS
        # -----------------------------------
        st.subheader("💬 Recruiter Talking Points")

        for skill in core_matched:
            st.write(f"- Proven experience with **{skill}**, aligned with role requirements.")

        for skill in missing_core:
            st.write(f"- Actively developing proficiency in **{skill}**.")

        # -----------------------------------
        # COVER LETTER
        # -----------------------------------
        st.subheader("✉️ Generated Cover Letter")
        st.write(generate_cover_letter(cv_text, jd_text))
