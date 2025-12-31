import streamlit as st
import re

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Job Application Intelligence Engine",
    layout="wide"
)

# -------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------
if "score" not in st.session_state:
    st.session_state.score = 0

if "core_matched" not in st.session_state:
    st.session_state.core_matched = []

if "missing_core" not in st.session_state:
    st.session_state.missing_core = []

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

# -------------------------------
# SKILL EXTRACTION LOGIC
# -------------------------------
def extract_skills(text):
    skills = [
        "python", "sql", "excel", "power bi", "tableau",
        "data analysis", "machine learning", "ai",
        "marketing", "email marketing", "seo", "content",
        "sales", "crm", "lead generation",
        "project management", "agile", "scrum",
        "communication", "presentation", "stakeholder",
        "finance", "trading", "risk management",
        "software development", "javascript", "react",
        "cloud", "aws", "azure", "docker"
    ]

    found = []
    text = text.lower()

    for skill in skills:
        if re.search(rf"\b{re.escape(skill)}\b", text):
            found.append(skill)

    return list(set(found))

# -------------------------------
# FIT ANALYSIS
# -------------------------------
def analyze_fit(cv_text, jd_text):
    jd_skills = extract_skills(jd_text)
    cv_skills = extract_skills(cv_text)

    core_matched = [s for s in jd_skills if s in cv_skills]
    missing_core = [s for s in jd_skills if s not in cv_skills]

    if len(jd_skills) == 0:
        score = 0
    else:
        score = round((len(core_matched) / len(jd_skills)) * 100, 1)

    return score, core_matched, missing_core

# -------------------------------
# UI
# -------------------------------
st.title("🧠 Job Application Intelligence Engine")
st.caption("AI-inspired analysis of CVs vs Job Descriptions")

col1, col2 = st.columns(2)

with col1:
    jd_text = st.text_area("📄 Paste Job Description", height=250)

with col2:
    cv_text = st.text_area("👤 Paste Your CV", height=250)

# -------------------------------
# ANALYZE BUTTON
# -------------------------------
if st.button("🔍 Analyze Fit"):
    if jd_text.strip() == "" or cv_text.strip() == "":
        st.warning("Please paste both the Job Description and your CV.")
    else:
        score, core_matched, missing_core = analyze_fit(cv_text, jd_text)

        st.session_state.score = score
        st.session_state.core_matched = core_matched
        st.session_state.missing_core = missing_core
        st.session_state.analysis_done = True

# -------------------------------
# RESULTS
# -------------------------------
if st.session_state.analysis_done:

    st.divider()
    st.subheader("📊 Fit Score")
    st.metric("Overall Match (%)", st.session_state.score)

    # -------------------------------
    # MATCHED SKILLS
    # -------------------------------
    st.subheader("✅ Matched Skills")
    if st.session_state.core_matched:
        for skill in st.session_state.core_matched:
            st.write(f"• {skill.title()}")
    else:
        st.write("No direct skill matches found.")

    # -------------------------------
    # MISSING SKILLS
    # -------------------------------
    st.subheader("⚠️ Missing Skills")
    if st.session_state.missing_core:
        for skill in st.session_state.missing_core:
            st.write(f"• {skill.title()}")
    else:
        st.write("No major skill gaps detected.")

    # -------------------------------
    # CV IMPROVEMENT SUGGESTIONS
    # -------------------------------
    st.divider()
    st.subheader("🛠️ CV Improvement Suggestions")

    if st.session_state.missing_core:
        for skill in st.session_state.missing_core:
            st.write(
                f"- Add a bullet point demonstrating experience, exposure, or coursework in **{skill.title()}**."
            )
    else:
        st.write("Your CV already aligns strongly with this role.")

    # -------------------------------
    # COVER LETTER
    # -------------------------------
    st.divider()
    st.subheader("✉️ Tailored Cover Letter (Draft)")

    cover_letter = f"""
Dear Hiring Manager,

I am excited to apply for this role, as my background strongly aligns with the key requirements outlined in the job description.

I bring hands-on experience in {", ".join(st.session_state.core_matched) if st.session_state.core_matched else "relevant transferable skills"}, and I am actively strengthening my capabilities in areas such as {", ".join(st.session_state.missing_core) if st.session_state.missing_core else "the full skill set required for this role"}.

I am confident that my ability to learn quickly, communicate effectively, and deliver results would allow me to add value to your team from day one.

Kind regards,  
Your Name
"""
    st.text_area("Generated Cover Letter", cover_letter, height=220)

    # -------------------------------
    # RECRUITER TALKING POINTS
    # -------------------------------
    st.divider()
    st.subheader("💬 Recruiter Talking Points")

    if st.session_state.core_matched:
        st.write("**Strengths to Highlight:**")
        for skill in st.session_state.core_matched:
            st.write(f"- Proven experience in **{skill.title()}**")

    if st.session_state.missing_core:
        st.write("**How to Address Gaps:**")
        for skill in st.session_state.missing_core:
            st.write(
                f"- Currently developing **{skill.title()}** through self-study, projects, or practical exposure"
            )
