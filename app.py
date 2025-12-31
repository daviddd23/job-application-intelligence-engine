import streamlit as st
import openai
import json
import re

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Job Application Intelligence Engine", layout="wide")

st.title("🧠 Job Application Intelligence Engine")
st.caption("AI-powered analysis of CVs vs Job Descriptions")

# -----------------------------
# API KEY
# -----------------------------
openai.api_key = st.secrets.get("OPENAI_API_KEY")

if not openai.api_key:
    st.error("❌ OpenAI API key not found. Add it in Streamlit Secrets.")
    st.stop()

# -----------------------------
# INPUTS
# -----------------------------
job_description = st.text_area("📄 Paste Job Description", height=250)
cv_text = st.text_area("📄 Paste Your CV", height=250)

analyze_btn = st.button("🔍 Analyze Fit")

# -----------------------------
# GPT: Extract JD Intelligence
# -----------------------------
def extract_jd_intelligence(jd_text):
    prompt = f"""
You are a senior recruiter.

From the job description below, extract structured hiring requirements.

Return STRICT JSON with:
- core_skills (list)
- tools (list)
- soft_skills (list)
- experience_level (string)

JOB DESCRIPTION:
{jd_text}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You extract structured hiring requirements."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    content = response.choices[0].message.content
    return json.loads(content)

# -----------------------------
# MATCHING LOGIC
# -----------------------------
def normalize(text):
    return re.sub(r"[^a-z0-9 ]", "", text.lower())

def match_items(source, target_text):
    matched = []
    for item in source:
        if normalize(item) in normalize(target_text):
            matched.append(item)
    return matched

def calculate_fit(core, tools, cv):
    core_matches = match_items(core, cv)
    tool_matches = match_items(tools, cv)

    score = 0
    if core:
        score += (len(core_matches) / len(core)) * 60
    if tools:
        score += (len(tool_matches) / len(tools)) * 40

    return round(score, 1), core_matches, tool_matches

# -----------------------------
# ANALYSIS
# -----------------------------
if analyze_btn and job_description and cv_text:
    with st.spinner("🧠 Analyzing like a recruiter..."):
        jd_data = extract_jd_intelligence(job_description)

        fit_score, core_matched, tools_matched = calculate_fit(
            jd_data["core_skills"],
            jd_data["tools"],
            cv_text
        )

        missing_core = list(set(jd_data["core_skills"]) - set(core_matched))

        risk_flags = []
        if fit_score < 40:
            risk_flags.append("Low overall alignment")
        if missing_core:
            risk_flags.append("Missing key core skills")

    # -----------------------------
    # OUTPUT
    # -----------------------------
    st.subheader("📊 Fit Score")
    st.metric("Overall Match (%)", fit_score)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("✅ Matched Core Skills")
        st.write(core_matched or "None")

        st.subheader("🛠 Matched Tools")
        st.write(tools_matched or "None")

    with col2:
        st.subheader("❌ Missing Core Skills")
        st.write(missing_core or "None")

        st.subheader("⚠️ Risk Flags")
        st.write(risk_flags or "None")

    # -----------------------------
    # CV IMPROVEMENT SUGGESTIONS
    # -----------------------------
    st.subheader("📝 CV Improvement Suggestions")

    improvement_prompt = f"""
You are a hiring manager.

Job requirements:
{jd_data}

Candidate CV:
{cv_text}

Give concise, actionable CV improvement suggestions.
"""

    improve_resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You improve CVs for job alignment."},
            {"role": "user", "content": improvement_prompt}
        ],
        temperature=0.3
    )

    st.write(improve_resp.choices[0].message.content)

    # -----------------------------
    # COVER LETTER
    # -----------------------------
    st.subheader("✉️ Tailored Cover Letter")

    cover_prompt = f"""
Write a concise,human, professional cover letter for this job.

Job Description:
{job_description}

Candidate CV:
{cv_text}
"""

    cover_resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You write recruiter-ready cover letters."},
            {"role": "user", "content": cover_prompt}
        ],
        temperature=0.4
    )

    st.write(cover_resp.choices[0].message.content)
    # -----------------------------
# RECRUITER TALKING POINTS
# -----------------------------
st.subheader("🗣️ Recruiter Talking Points")

talking_points_prompt = f"""
You are a recruiter coaching a candidate.

Job Description:
{job_description}

Candidate CV:
{cv_text}

Matched Skills:
{core_matched}

Missing Skills:
{missing_core}

Generate 4–5 concise recruiter talking points the candidate can say confidently.
Each point should:
- Sound natural
- Emphasize strengths
- Address gaps intelligently (without lying)
"""

talking_resp = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You coach candidates for recruiter conversations."},
        {"role": "user", "content": talking_points_prompt}
    ],
    temperature=0.4
)

st.write(talking_resp.choices[0].message.content)

