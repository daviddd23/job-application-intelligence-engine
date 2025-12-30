import streamlit as st
import openai
import re

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(
    page_title="Job Application Intelligence Engine",
    page_icon="📄",
    layout="wide"
)

st.title("📊 Job Application Intelligence Engine")
st.write("Analyze your CV against any Job Description and get recruiter-ready insights.")

# OpenAI API Key (Streamlit Secrets)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ----------------------------
# SKILL EXTRACTION LOGIC
# ----------------------------
def extract_skills(text):
    text = text.lower()

    skill_keywords = [
        # Marketing / Sales
        "email marketing", "klaviyo", "hubspot", "salesforce", "crm",
        "funnels", "flows", "a/b testing", "segmentation", "lead generation",
        "copywriting", "conversion optimization", "campaign management",

        # Tech / Data
        "python", "sql", "excel", "pandas", "automation", "api",
        "machine learning", "ai", "data analysis",

        # Ops / General
        "project management", "stakeholder management", "communication",
        "analytics", "reporting", "strategy", "presentation"
    ]

    found = set()
    for skill in skill_keywords:
        if re.search(rf"\b{re.escape(skill)}\b", text):
            found.add(skill)

    return found


# ----------------------------
# FIT SCORE CALCULATION
# ----------------------------
def calculate_fit(job_skills, cv_skills):
    if not job_skills:
        return 0.0, set(), job_skills

    matched = job_skills.intersection(cv_skills)
    missing = job_skills.difference(cv_skills)

    score = round((len(matched) / len(job_skills)) * 100, 1)
    return score, matched, missing


# ----------------------------
# GPT INSIGHTS
# ----------------------------
def gpt_insights(score, matched, missing, job_desc):
    prompt = f"""
You are a senior recruiter.

Job Description:
{job_desc}

Candidate Fit Score: {score}/100

Matched skills:
{list(matched)}

Missing skills:
{list(missing)}

Provide:
1. Clear explanation of the score
2. CV improvement suggestions
3. How the candidate should position themselves
4. Recruiter talking points
5. A short tailored cover letter
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    return response["choices"][0]["message"]["content"]


# ----------------------------
# UI INPUTS
# ----------------------------
col1, col2 = st.columns(2)

with col1:
    job_description = st.text_area(
        "📌 Paste Job Description",
        height=300,
        placeholder="Paste the full job description here..."
    )

with col2:
    cv_text = st.text_area(
        "📄 Paste Your CV",
        height=300,
        placeholder="Paste your CV content here..."
    )

analyze = st.button("🚀 Analyze Application")

# ----------------------------
# RUN ANALYSIS
# ----------------------------
if analyze:
    if not job_description or not cv_text:
        st.warning("Please paste both a Job Description and a CV.")
    else:
        job_skills = extract_skills(job_description)
        cv_skills = extract_skills(cv_text)

        fit_score, matched, missing = calculate_fit(job_skills, cv_skills)

        st.subheader("📈 Fit Analysis Results")

        st.metric("Fit Score", f"{fit_score}%")

        colA, colB = st.columns(2)

        with colA:
            st.success("✅ Matched Skills")
            if matched:
                for skill in matched:
                    st.write(f"- {skill}")
            else:
                st.write("None detected")

        with colB:
            st.error("❌ Missing Skills")
            if missing:
                for skill in missing:
                    st.write(f"- {skill}")
            else:
                st.write("None")

        st.divider()

        st.subheader("🤖 AI Recruiter Insights")

        with st.spinner("Generating recruiter-level insights..."):
            insights = gpt_insights(
                fit_score,
                matched,
                missing,
                job_description
            )

        st.write(insights)

# ----------------------------
# FOOTER
# ----------------------------
st.divider()
st.caption("Built by David Idowu | AI Automation & Job Intelligence")
