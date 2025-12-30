import streamlit as st
import re
from collections import Counter

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Job Application Intelligence Engine",
    layout="wide"
)

st.title("🧠 Job Application Intelligence Engine")
st.caption("Role-agnostic CV vs Job Description analysis")

# -----------------------------
# SIMPLE SKILL EXTRACTION
# -----------------------------
STOPWORDS = set([
    "and", "or", "with", "for", "the", "a", "an", "to", "of", "in",
    "experience", "skills", "ability", "strong", "working", "knowledge"
])

def extract_skills(text):
    text = text.lower()
    words = re.findall(r"[a-zA-Z+#\.]{2,}", text)
    skills = [w for w in words if w not in STOPWORDS]
    return Counter(skills)

# -----------------------------
# FIT CALCULATION
# -----------------------------
def analyze_fit(job_text, cv_text):
    job_skills = extract_skills(job_text)
    cv_skills = extract_skills(cv_text)

    job_skill_set = set(job_skills.keys())
    cv_skill_set = set(cv_skills.keys())

    matched = job_skill_set.intersection(cv_skill_set)
    missing = job_skill_set - cv_skill_set

    if len(job_skill_set) == 0:
        fit_score = 0
    else:
        fit_score = round((len(matched) / len(job_skill_set)) * 100, 2)

    risk_flags = []
    if fit_score < 40:
        risk_flags.append("Low alignment with job requirements")
    if len(missing) >= 5:
        risk_flags.append("Multiple missing role-critical skills")

    return {
        "fit_score": fit_score,
        "matched_skills": sorted(list(matched)),
        "missing_skills": sorted(list(missing)),
        "risk_flags": risk_flags
    }

# -----------------------------
# INPUTS
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    job_description = st.text_area(
        "🧾 Paste Job Description",
        height=300,
        placeholder="Paste the full job description here..."
    )

with col2:
    cv_text = st.text_area(
        "📄 Paste Your CV / Experience",
        height=300,
        placeholder="Paste your CV or key experience here..."
    )

# -----------------------------
# RUN ANALYSIS
# -----------------------------
if st.button("Analyze Fit"):
    if not job_description or not cv_text:
        st.warning("Please paste both the job description and your CV.")
    else:
        result = analyze_fit(job_description, cv_text)

        st.subheader("📊 Fit Score")
        st.metric("Overall Match", f"{result['fit_score']} / 100")

        st.subheader("✅ Matched Skills")
        st.write(result["matched_skills"])

        st.subheader("❌ Missing Skills")
        st.write(result["missing_skills"])

        st.subheader("⚠️ Recruiter Risk Flags")
        if result["risk_flags"]:
            for r in result["risk_flags"]:
                st.write(f"- {r}")
        else:
            st.write("No major risks identified")

        st.subheader("🗣 Recruiter Talking Points")
        st.write(
            "The candidate demonstrates overlap with key job requirements and shows "
            "transferable skills that can be ramped quickly with role-specific onboarding."
        )

        st.subheader("✍️ Cover Letter Starter")
        st.write(
            "I am excited to apply for this role, bringing experience that aligns with several "
            "of your core requirements. While I continue strengthening certain areas, I have "
            "a proven ability to learn quickly and deliver results in dynamic environments."
        )
