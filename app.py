from flask import Flask, render_template, request
import pdfplumber
import re

app = Flask(__name__)

# =========================
# MASTER SKILLS
# =========================
MASTER_SKILLS = {
    "python","java","c","c++","c#","javascript","typescript",
    "html","css","react","angular","vue","js","node","express",
    "flask","django","spring","spring boot","fastapi",
    "sql","mysql","postgresql","mongodb","sqlite","oracle",
    "pandas","numpy","matplotlib","seaborn","excel","power bi","tableau",
    "aws","azure","gcp","docker","kubernetes","jenkins","github actions",
    "airflow","hadoop","spark",
    "linux","windows","unix",
    "git","github","gitlab","bitbucket",
    "unit testing","pytest","junit","selenium",
    "rest api","graphql","microservices",
    "machine learning","deep learning","nlp","tensorflow","pytorch","scikit-learn",
    "communication","problem solving","teamwork","leadership","time management","adaptability",
    "data structures","algorithms","oops","operating systems","computer networks","dbms",
    "ci/cd","system design","design patterns","agile","scrum"
}

# =========================
# SKILL CATEGORIES (HYBRID AI)
# =========================
SKILL_CATEGORIES = {
    "Backend": {"python","java","flask","django","fastapi","spring","spring boot","node","express"},
    "Frontend": {"html","css","javascript","react","angular","vue"},
    "Data": {"sql","mysql","postgresql","mongodb","pandas","numpy","excel","power bi","tableau"},
    "Cloud & DevOps": {"aws","azure","gcp","docker","kubernetes","ci/cd"},
    "AI / ML": {"machine learning","deep learning","nlp","tensorflow","pytorch","scikit-learn"}
}

ACTION_WORDS = {
    "developed","built","designed","implemented",
    "optimized","deployed","created","managed"
}

# =========================
# HELPERS
# =========================
def clean(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text)

def extract_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text()
    return clean(text)

def find_skills(text):
    found = set()
    for skill in MASTER_SKILLS:
        if re.search(rf"\b{re.escape(skill)}\b", text):
            found.add(skill)
    return found

def calculate_ats(resume_text, jd_text, match_percent):
    score = 0

    # Skill match (50)
    score += int(match_percent * 0.5)

    # Keyword overlap (20)
    jd_words = set(jd_text.split())
    resume_words = set(resume_text.split())
    if jd_words:
        score += min(20, int(len(jd_words & resume_words) / len(jd_words) * 20))

    # Resume length (10)
    wc = len(resume_text.split())
    if 300 <= wc <= 900:
        score += 10
    elif 200 <= wc < 300:
        score += 5

    # Action words (20)
    action_hits = sum(1 for w in ACTION_WORDS if w in resume_text)
    score += min(20, action_hits * 4)

    return min(score, 100)

# =========================
# HYBRID AI SUGGESTIONS (0 COST)
# =========================
def generate_ai_suggestions(missing, ats, jd_skills):
    suggestions = []

    # ATS-based reasoning
    if ats < 40:
        suggestions.append(
            "Your resume has low alignment with the job description. Focus on adding core technical skills and relevant keywords."
        )
    elif ats < 70:
        suggestions.append(
            "Your resume partially matches the job role. Strengthening weak areas and adding better project descriptions can improve it."
        )
    else:
        suggestions.append(
            "Your resume aligns well with the job role. Minor refinements can further strengthen it."
        )

    # Category-level intelligence
    for category, skills in SKILL_CATEGORIES.items():
        required = skills & jd_skills
        missing_cat = required & set(missing)
        if required and missing_cat:
            suggestions.append(
                f"The job emphasizes **{category} skills**. Consider improving: {', '.join(list(missing_cat)[:3])}."
            )

    # Generic smart suggestions
    if missing:
        suggestions.append(
            "Build at least one real-world project showcasing the missing skills."
        )

    suggestions.append(
        "Use strong action verbs and quantify results (e.g., 'Improved API performance by 30%')."
    )

    return suggestions

# =========================
# ROUTE
# =========================
@app.route("/", methods=["GET", "POST"])
def index():
    match = None
    ats = None
    matched = []
    missing = []
    ai_suggestions = []

    if request.method == "POST":
        resume = request.files.get("resume")
        jd = request.form.get("job_desc", "").strip()

        if resume and jd:
            resume_text = extract_pdf(resume)
            jd_text = clean(jd)

            jd_skills = find_skills(jd_text)
            resume_skills = find_skills(resume_text)

            matched = sorted(jd_skills & resume_skills)
            missing = sorted(jd_skills - resume_skills)

            match = int(len(matched) / len(jd_skills) * 100) if jd_skills else 0
            ats = calculate_ats(resume_text, jd_text, match)

            ai_suggestions = generate_ai_suggestions(missing, ats, jd_skills)

    return render_template(
        "index.html",
        match=match,
        ats=ats,
        matched=matched,
        missing=missing,
        ai_suggestions=ai_suggestions
    )

if __name__ == "__main__":
    app.run()

