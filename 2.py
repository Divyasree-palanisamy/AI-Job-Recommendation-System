import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import joblib
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
import docx2txt
import re
from datetime import datetime

# ------------------- CONFIG -------------------
APP_DIR = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(APP_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB_PATH = os.path.join(APP_DIR, "data.db")
MODEL_PATH = os.path.join(APP_DIR, "models", "job_recommendation_type_knn.pkl")

app = Flask(__name__)
app.secret_key = "change_this_secret"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"pdf", "docx"}

# ------------------- MODEL -------------------
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
model = joblib.load(MODEL_PATH)

try:
    vectorizer = model.named_steps.get("tfidf", None)
except Exception:
    vectorizer = None

# ------------------- DB INIT -------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            full_name TEXT,
            register_number TEXT,
            college TEXT,
            batch_year TEXT,
            semester TEXT,
            skills TEXT,
            skill_ratings TEXT,
            experience TEXT,
            interests TEXT,
            tech_stack TEXT,
            location TEXT,
            created_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            required_skills TEXT,
            posted_by TEXT,
            created_at TEXT
        )
    """)
    try:
        cur.execute("ALTER TABLE jobs ADD COLUMN application_link TEXT")
    except:
    # Column already exists, ignore the error
        pass

    cur.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT,
            platform TEXT,
            link TEXT,
            recommended_for TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()


from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_ats_report(student, predicted_job_type, recs, courses, resume_filename):
    report_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{student[1]}_ATS_Report.pdf")
    c = canvas.Canvas(report_path, pagesize=letter)
    width, height = letter
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Smart Career Portal - ATS Resume Analysis")
    y -= 40

    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Student Name: {student[3]}")
    y -= 20
    c.drawString(50, y, f"Username: {student[1]}")
    y -= 20
    c.drawString(50, y, f"Predicted Career Path: {predicted_job_type.capitalize()}")
    y -= 40

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Top Job Recommendations:")
    y -= 20
    c.setFont("Helvetica", 12)
    for item in recs[:5]:
        c.drawString(60, y, f"• {item['job'][1]} ({item['score']}%)")
        y -= 15
        if y < 100:  # new page if needed
            c.showPage()
            y = height - 50

    y -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Recommended Courses:")
    y -= 20
    c.setFont("Helvetica", 12)
    for cdata in courses[:5]:
        c.drawString(60, y, f"• {cdata[1]} ({cdata[2]})")
        y -= 15
        if y < 100:
            c.showPage()
            y = height - 50

    y -= 30
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Generated from resume: {resume_filename}")
    c.showPage()
    c.save()
    return report_path



# ------------------- HELPERS -------------------
def db_fetchall(query, params=()):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()

def db_execute(query, params=()):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur.lastrowid

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_resume(file_path):
    text = ""
    if file_path.endswith(".pdf"):
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + " "
    elif file_path.endswith(".docx"):
        text = docx2txt.process(file_path)
    return text

def clean_text(text):
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.lower().strip()

# ------------------- ML HELPERS -------------------
def build_student_text(student_row):
    keys = ["id","username","password","full_name","register_number","college","batch_year","semester",
            "skills","skill_ratings","experience","interests","tech_stack","location","created_at"]
    r = dict(zip(keys, student_row))
    parts = [r.get("skills",""), r.get("skill_ratings",""), r.get("interests",""),
             r.get("tech_stack",""), r.get("experience","")]
    return " ".join([p for p in parts if p])

def job_text(job_row):
    j = dict(zip(["id","title","description","required_skills","posted_by","created_at"], job_row))
    return " ".join([j.get("title",""), j.get("description",""), j.get("required_skills","")])

def recommend_jobs(student_row, all_jobs, top_k=5):
    profile_text = build_student_text(student_row)
    recs = []
    try:
        predicted_label = str(model.predict([profile_text])[0]).strip().lower()
    except Exception:
        predicted_label = None

    if vectorizer and len(all_jobs) > 0:
        try:
            texts = [profile_text] + [job_text(j) for j in all_jobs]
            tfidf = vectorizer.transform(texts)
            sim_scores = cosine_similarity(tfidf[0:1], tfidf[1:])[0]
            for idx, job in enumerate(all_jobs):
                recs.append({
                    "job": job,
                    "score": round(float(sim_scores[idx])*100, 2)
                })
        except Exception:
            pass
    recs_sorted = sorted(recs, key=lambda x: x["score"], reverse=True)
    return predicted_label, recs_sorted[:top_k]

def recommend_courses(predicted_job_type):
    if not predicted_job_type:
        return []

    # convert predicted job type into keywords
    keywords = predicted_job_type.replace("-", " ").split()

    q = "SELECT * FROM courses WHERE " + " OR ".join(
        ["LOWER(recommended_for) LIKE LOWER(?)"] * len(keywords)
    )

    params = [f"%{k}%" for k in keywords]

    return db_fetchall(q, params)



# ------------------- ROUTES -------------------

@app.route("/")
def index():
    if session.get("role") == "student":
        return redirect(url_for("dashboard"))
    elif session.get("role") == "admin":
        return redirect(url_for("admin_dashboard"))

    return redirect(url_for("login"))

# --- Register ---
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    data = [request.form.get(f, "").strip() for f in [
        "username","password","full_name","register_number","college","batch_year","semester",
        "skills","skill_ratings","experience","interests","tech_stack","location"]]
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        db_execute("""
            INSERT INTO students (username,password,full_name,register_number,college,batch_year,
            semester,skills,skill_ratings,experience,interests,tech_stack,location,created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (*data, created_at))
        flash("Registered successfully! Please login.", "success")
        return redirect(url_for("login"))
    except Exception as e:
        flash(f"Registration failed: {e}", "danger")
        return redirect(url_for("register"))

# --- Login ---
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role", "student")
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if role == "admin":
            if username == "admin" and password == "admin1234":
                session["username"] = username
                session["role"] = "admin"
                return redirect(url_for("admin_dashboard"))

            flash("Invalid admin credentials", "danger")
            return redirect(url_for("login"))

        user = db_fetchall("SELECT * FROM students WHERE username=?", (username,))
        if not user or user[0][2] != password:
            flash("Invalid username or password", "danger")
            return redirect(url_for("login"))
        session["username"] = username
        session["role"] = "student"
        session["student_id"] = user[0][0]
        return redirect(url_for("dashboard"))
    return render_template("login.html")

# --- Logout ---
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))
    

# --- Upload Resume (Student) ---
@app.route("/upload_resume", methods=["GET","POST"])
def upload_resume():
    if session.get("role") != "student":
        return redirect(url_for("login"))

    if request.method == "POST":
        file = request.files.get("resume")
        if not file or file.filename == "":
            flash("No file uploaded.", "danger")
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash("Only PDF/DOCX allowed.", "danger")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)
        resume_text = clean_text(extract_text_from_resume(path))

        student = db_fetchall("SELECT * FROM students WHERE id=?", (session.get("student_id"),))[0]
        jobs = db_fetchall("SELECT * FROM jobs ORDER BY id DESC")
        predicted_job_type, recs = recommend_jobs(student, jobs, top_k=10)
        courses = recommend_courses(predicted_job_type)

        # Get Recommended Courses
        courses = db_fetchall("SELECT * FROM courses WHERE recommended_for LIKE ?", (f"%{predicted_job_type}%",))

        # ✅ Generate ATS Report PDF
        report_path = generate_ats_report(student, predicted_job_type, recs, courses, filename)

        # ✅ Return results + download link
        return render_template("ats_results.html",
                               predicted_job_type=predicted_job_type,
                               matches=recs,
                               courses=courses,
                               resume_filename=filename,
                               ats_report=os.path.basename(report_path))


    return render_template("upload_resume.html")

# --- Student Dashboard ---
@app.route("/dashboard")
def dashboard():
    if session.get("role") != "student":
        return redirect(url_for("login"))
    student = db_fetchall("SELECT * FROM students WHERE id=?", (session.get("student_id"),))[0]
    jobs = db_fetchall("SELECT * FROM jobs ORDER BY id DESC")
    predicted_job_type, recs = recommend_jobs(student, jobs, top_k=5)
    courses = recommend_courses(predicted_job_type)
    return render_template("dashboard.html",
                           student=student,
                           recommendations=recs,
                           predicted_job_type=predicted_job_type,
                           courses=courses)

# --- Admin Dashboard with Student Management ---
# --- Admin Dashboard with Student Management ---
@app.route("/admin", methods=["GET", "POST"])
def admin_dashboard():
    if session.get("role") != "admin":
        flash("Unauthorized access!")
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Add Job
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        required_skills = request.form.get("required_skills")
        course_name = request.form.get("course_name")
        application_link = request.form.get("application_link")

        # Job posting
        if title and required_skills:
            c.execute("""
            INSERT INTO jobs (title, description, required_skills, application_link, posted_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (title, description, required_skills, application_link, session.get("username"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            flash("Job opportunity added successfully!", "success")

        # Course addition
        if course_name:
            platform = request.form.get("platform")
            link = request.form.get("link")
            recommended_for = request.form.get("recommended_for")
            c.execute("INSERT INTO courses (course_name, platform, link, recommended_for) VALUES (?, ?, ?, ?)",
                      (course_name, platform, link, recommended_for))
            conn.commit()
            flash("Course added successfully!", "success")

    # Fetch all data
    c.execute("SELECT * FROM jobs ORDER BY id DESC")
    jobs = c.fetchall()
    c.execute("SELECT * FROM courses ORDER BY id DESC")
    courses = c.fetchall()
    c.execute("SELECT * FROM students ORDER BY id DESC")
    students = c.fetchall()

    conn.close()
    return render_template("admin_dashboard.html", jobs=jobs, courses=courses, students=students)



# --- Delete Job ---
@app.route("/delete/job/<int:job_id>")
def delete_job(job_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM jobs WHERE id=?", (job_id,))
    conn.commit()
    conn.close()
    flash("Job deleted successfully!", "info")
    return redirect(url_for("admin_dashboard"))


# --- Delete Course ---
@app.route("/delete/course/<int:course_id>")
def delete_course(course_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM courses WHERE id=?", (course_id,))
    conn.commit()
    conn.close()
    flash("Course deleted successfully!", "info")
    return redirect(url_for("admin_dashboard"))


# --- Delete Student ---
@app.route("/delete/student/<int:student_id>")
def delete_student(student_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()
    flash("Student profile deleted successfully!", "info")
    return redirect(url_for("admin_dashboard"))


# --- Delete ---
@app.route("/delete/<kind>/<int:obj_id>")
def delete(kind, obj_id):
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    if kind == "job":
        db_execute("DELETE FROM jobs WHERE id=?", (obj_id,))
    elif kind == "student":
        db_execute("DELETE FROM students WHERE id=?", (obj_id,))
    elif kind == "course":
        db_execute("DELETE FROM courses WHERE id=?", (obj_id,))
    flash(f"{kind.capitalize()} deleted.", "info")
    return redirect(url_for("admin_dashboard"))

# --- Delete Student Profile ---
@app.route("/delete_profile", methods=["POST"])
def delete_profile():
    if session.get("role") != "student":
        return redirect(url_for("login"))
    sid = session.get("student_id")
    db_execute("DELETE FROM students WHERE id=?", (sid,))
    session.clear()
    flash("Profile deleted successfully.", "info")
    return redirect(url_for("register"))



@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

# ------------------- MAIN -------------------
if __name__ == "__main__":
    app.run(debug=True)
