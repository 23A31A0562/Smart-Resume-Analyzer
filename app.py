from flask import Flask, render_template, request
import pdfplumber
import re

app = Flask(__name__)

# 🔒 MASTER SKILLS (ONLY THESE AFFECT MATCH %)
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

def clean(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text)

def extract_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            if p.extract_text():
                text += p.extract_text()
    return clean(text)

def find_skills(text):
    found = set()
    for skill in MASTER_SKILLS:
        if re.search(r"\b" + re.escape(skill) + r"\b", text):
            found.add(skill)
    return found

@app.route("/", methods=["GET","POST"])
def index():
    match = None
    missing = []
    matched = []
    error = None

    if request.method == "POST":
        resume = request.files.get("resume")
        jd = request.form.get("job_desc","").strip()

        if not resume or resume.filename == "":
            error = "Upload resume PDF"
            return render_template("index.html", error=error)

        if not jd:
            error = "Paste job description"
            return render_template("index.html", error=error)

        resume_text = extract_pdf(resume)
        jd_text = clean(jd)

        jd_skills = find_skills(jd_text)
        resume_skills = find_skills(resume_text)

        matched = sorted(jd_skills & resume_skills)
        missing = sorted(jd_skills - resume_skills)

        match = int((len(matched) / len(jd_skills)) * 100) if jd_skills else 0

    return render_template(
        "index.html",
        match=match,
        matched=matched,
        missing=missing,
        error=error
    )

if __name__ == "__main__":
    app.run(debug=True)
