import streamlit as st 

# -----------------------------
# PAGE SETUP
# -----------------------------
st.set_page_config(page_title="Job Application Intelligence Engine", layout="wide")
st.title("🧠 Job Application Intelligence Engine")

st.write("Analyze your CV against a job description and get recruiter-ready insights.")

# -----------------------------
# JOB REQUIREMENTS (STATIC FOR NOW)
# -----------------------------
job_requirements = {
    "core_skills": ["klaviyo", "email marketing", "flows", "segmentation", "a/b testing"],
    "supporting_skills": ["shopify", "analytics", "copywriting", "design collaboration"],
    "tools": ["shopify", "facebook ads", "google analytics"]
}

skill_synonyms = {
    "email marketing": ["email automation", "email campaigns"],
    "flows": ["automation", "workflows"],
    "segmentation": ["audience segmentation"],
    "a/b testing": ["split testing"],
    "analytics": ["data analysis", "reporting"]
}

# -----------------------------
# FUNCTIONS
# -----------------------------
def normalize_skills(skills):
    normalized = set(skills)
    for main, synonyms in skill_synonyms.items():
        for s in skills:
            for syn in synonyms:
                if syn in s:
                    normalized.add(main)
    return list(normalized)

def generate_risk_flags(missing):
    flags = []
    if "klaviyo" in missing:
        flags.append("No direct Klaviyo experience")
    if len(missing) >= 3:
        flags.append("Multiple core skill gaps")
    return flags

def calculate_fit(job, skills):

    def score(req, weight):
        matched = [s for s in req if any(s in cv for cv in skills)]
        return (len(matched) / len(req)) * weight, matched

    core_score, core_matched = score(job["core_skills"], 50)
    sup_score, sup_matched = score(job["supporting_skills"], 30)
    tool_score, tool_matched = score(job["tools"], 20)

    missing = list(set(job["core_skills"]) - set(core_matched))

    return {
        "fit_score": round(core_score + sup_score + tool_score, 2),
        "core_matched": core_matched,
        "missing_core": missing,
        "supporting_matched": sup_matched,
        "tools_matched": tool_matched,
        "risk_flags": generate_risk_flags(missing)
    }

# -----------------------------
# INPUTS
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    cv_input = st.text_area("📄 Paste your CV skills / experience", height=250)

with col2:
    jd_input = st.text_area("🧾 Paste the Job Description (optional for now)", height=250)

# -----------------------------
# RUN ANALYSIS
# -----------------------------
if st.button("Analyze Fit"):

    cv_skills = [s.strip().lower() for s in cv_input.split(",") if s.strip()]
    cv_skills = normalize_skills(cv_skills)

    result = calculate_fit(job_requirements, cv_skills)

    st.subheader("📊 Fit Score")
    st.metric("Overall Match", f"{result['fit_score']} / 100")

    st.subheader("✅ Matched Core Skills")
    st.write(result["core_matched"])

    st.subheader("❌ Missing Core Skills")
    st.write(result["missing_core"])

    st.subheader("⚠️ Risk Flags")
    st.write(result["risk_flags"])

    st.subheader("🗣 Recruiter Talking Points")
    for r in result["risk_flags"]:
        st.write(f"- {r}")

    st.subheader("✍️ Cover Letter Starter")
    st.write(
        "I’m excited to apply for this role, bringing strong experience in email automation "
        "and workflow-driven systems. While I continue expanding my hands-on Klaviyo expertise, "
        "I adapt quickly to new platforms and focus on data-backed optimization."
    )
