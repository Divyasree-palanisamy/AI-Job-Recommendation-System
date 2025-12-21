import os
import sqlite3
import logging
import io
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import joblib
from sklearn.metrics.pairwise import cosine_similarity
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# --- Logging Configuration ---
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

APP_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(APP_DIR, "data.db")
MODEL_PATH = os.path.join(APP_DIR, "models", "job_recommendation_type_knn.pkl")

app = Flask(__name__)
app.secret_key = "kkit_secret_key_123" # Use a stable secret key

# --- Load Model ---
model = None
vectorizer = None
try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        logger.info("AI Model loaded successfully")
        try:
            vectorizer = model.named_steps.get("tfidf", None)
        except:
            vectorizer = None
    else:
        logger.error(f"Model file not found at {MODEL_PATH}")
except Exception as e:
    logger.error(f"Error loading model: {e}")

# --- DB Initialization ---
def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Users Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'student',
                created_at TEXT
            )
        """)
        
        # Student Profile Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS student_profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                full_name TEXT,
                register_number TEXT,
                college_name TEXT,
                batch_year TEXT,
                current_semester TEXT,
                skills TEXT,
                skill_ratings TEXT,
                experience TEXT,
                interests TEXT,
                tech_stack TEXT,
                location TEXT,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Jobs Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                required_skills TEXT,
                posted_by TEXT,
                application_link TEXT,
                created_at TEXT
            )
        """)

        # Job Recommendations Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS job_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                job_id INTEGER NOT NULL,
                match_score REAL,
                match_reason TEXT,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (job_id) REFERENCES jobs(id)
            )
        """)

        # Courses Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                category TEXT,
                added_by TEXT,
                created_at TEXT
            )
        """)

        # Course Videos Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS course_videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER,
                video_title TEXT,
                video_url TEXT,
                category TEXT,
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        """)

        # Job Trends Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS job_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_role TEXT,
                industry TEXT,
                trending_skills TEXT,
                year TEXT,
                added_by TEXT,
                created_at TEXT
            )
        """)

        conn.commit()
        conn.close()
        logger.info("Database checked/initialized")
    except Exception as e:
        logger.error(f"DB Init Error: {e}")

init_db()

# --- DB Helpers ---
def db_fetchall(query, params=()):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.fetchall()
    except Exception as e:
        logger.error(f"DB Fetch Error: {e} | Query: {query}")
        return []

def db_execute(query, params=()):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            return cur.lastrowid
    except Exception as e:
        logger.error(f"DB Execute Error: {e} | Query: {query}")
        raise e

# --- ML Logic ---
def build_student_text(profile_row):
    # (id, user_id, name, reg, coll, batch, sem, skills, ratings, exp, ints, stack, loc, date)
    if not profile_row: return ""
    parts = [str(profile_row[7]), str(profile_row[8]), str(profile_row[10]), str(profile_row[11]), str(profile_row[9])]
    return " ".join([p for p in parts if p and p != 'None'])

def job_text(job_row):
    # (id, title, desc, skills, posted, link, date)
    if not job_row: return ""
    parts = [str(job_row[1]), str(job_row[2]), str(job_row[3])]
    return " ".join([p for p in parts if p and p != 'None'])

def recommend_jobs_logic(profile_row, all_jobs, top_k=10):
    profile_text = build_student_text(profile_row)
    recs = []
    predicted_label = None

    if model:
        try:
            predicted_label = str(model.predict([profile_text])[0]).strip().lower()
        except:
            pass

    tfidf_profile, tfidf_jobs = None, None
    if vectorizer and all_jobs:
        try:
            texts = [profile_text] + [job_text(j) for j in all_jobs]
            tfidf = vectorizer.transform(texts)
            tfidf_profile = tfidf[0:1]
            tfidf_jobs = tfidf[1:]
        except:
            pass

    for idx, job in enumerate(all_jobs):
        jtxt = job_text(job)
        eligible, reason, score = False, "", 0.0
        job_title = (job[1] or "").lower()

        if predicted_label and (predicted_label in job_title or job_title in predicted_label):
            eligible, reason, score = True, f"AI Match: {predicted_label}", 1.0

        if not eligible and tfidf_profile is not None and tfidf_jobs is not None:
            sim = float(cosine_similarity(tfidf_profile, tfidf_jobs[idx:idx+1])[0][0])
            if sim >= 0.2:
                eligible, reason, score = True, f"Similarity: {sim:.2f}", sim

        if eligible:
            recs.append({"job_id": job[0], "score": round(score, 3), "reason": reason})

    return predicted_label, sorted(recs, key=lambda x: x["score"], reverse=True)[:top_k]

# --- Error Handlers ---
@app.errorhandler(404)
def page_not_found(e):
    logger.error(f"404 Error: {request.url} not found")
    return "Page Not Found (404). Please check the URL.", 404

# --- Routes ---
@app.route("/favicon.ico")
def favicon():
    return "", 204

@app.route("/test")
def test():
    return "Flask server is active!"

@app.route("/")
def index():
    if session.get("username"):
        if session.get("role") == "admin":
            return redirect(url_for("admin"))
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role")
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if role == "admin":
            if username == "admin" and password == "admin1234":
                session["username"] = "admin"
                session["role"] = "admin"
                session["user_id"] = -1 # Admin has id -1
                return redirect(url_for("admin"))
            flash("Invalid Admin Credentials", "danger")
            return redirect(url_for("login"))

        user = db_fetchall("SELECT * FROM users WHERE username=? AND role='student'", (username,))
        if user and user[0][3] == password:
            session["user_id"] = user[0][0]
            session["username"] = user[0][1]
            session["role"] = "student"
            return redirect(url_for("dashboard"))
        
        flash("Invalid Username or Password", "danger")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        
        if not (username and email and password):
            flash("Please fill all fields", "danger")
            return redirect(url_for("register"))

        try:
            db_execute("INSERT INTO users (username, email, password, created_at) VALUES (?, ?, ?, ?)",
                       (username, email, password, datetime.now().strftime("%Y-%m-%d %H:%M")))
            flash("Account created! Please login.", "success")
            return redirect(url_for("login"))
        except:
            flash("Username or Email already exists", "danger")
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if session.get("role") != "student":
        return redirect(url_for("login"))
    
    user_id = session.get("user_id")
    profile = db_fetchall("SELECT * FROM student_profile WHERE user_id=?", (user_id,))
    
    if not profile:
        return render_template("dashboard.html", student=None, needs_profile=True)

    recs = db_fetchall("""
        SELECT j.*, r.match_score, r.match_reason FROM job_recommendations r
        JOIN jobs j ON r.job_id = j.id WHERE r.user_id = ? ORDER BY r.match_score DESC
    """, (user_id,))

    # Calculate ATS compatibility insights
    profile_completeness = 0
    ats_insights = []

    if profile and profile[0]:
        p = profile[0]
        # Check profile completeness
        fields = [p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9], p[10], p[11], p[12]]
        filled_fields = sum(1 for f in fields if f and str(f).strip() and str(f) != 'None')
        profile_completeness = int((filled_fields / len(fields)) * 100)

        # Generate insights based on profile
        if p[7] and len(str(p[7]).split(',')) >= 3:  # Skills
            ats_insights.append("✓ Strong skills profile with multiple technologies")
        elif p[7]:
            ats_insights.append("⚠ Add more skills to improve ATS matching")

        if p[11] and len(str(p[11]).split(',')) >= 2:  # Tech stack
            ats_insights.append("✓ Diverse tech stack increases job opportunities")
        elif p[11]:
            ats_insights.append("⚠ Expand your tech stack for better matches")

        if p[9] and len(str(p[9]).split()) >= 10:  # Experience
            ats_insights.append("✓ Detailed experience description helps ATS parsing")
        elif p[9]:
            ats_insights.append("⚠ Add more details to your experience section")

        if recs and len(recs) >= 5:
            ats_insights.append("✓ Multiple job matches found - good profile strength")
        elif recs and len(recs) >= 2:
            ats_insights.append("✓ Some job matches generated")
        elif recs:
            ats_insights.append("⚠ Limited job matches - consider broadening skills")

        # Default insights if profile is incomplete
        if not ats_insights:
            ats_insights = [
                "Complete your profile for better recommendations",
                "Add skills, experience, and tech stack details",
                "Include specific technologies and tools you know"
            ]

    else:
        profile_completeness = 0
        ats_insights = ["Complete your profile to get personalized insights"]

    # Get unique course categories
    all_courses = db_fetchall("SELECT * FROM courses ORDER BY id DESC")
    course_categories = []
    seen_categories = set()
    for course in all_courses:
        category = course[3]  # category is at index 3 (id, title, description, category, added_by, created_at)
        if category and category not in seen_categories:
            seen_categories.add(category)
            course_categories.append((category,))

    return render_template("dashboard.html", student=profile[0], recommendations=recs,
                           trends=db_fetchall("SELECT * FROM job_trends ORDER BY id DESC"),
                           courses=all_courses,
                           course_categories=course_categories,
                           videos=db_fetchall("SELECT * FROM course_videos ORDER BY id DESC"),
                           profile_completeness=profile_completeness, ats_insights=ats_insights,
                           needs_profile=False)

@app.route("/save_profile", methods=["POST"])
def save_profile():
    if session.get("role") != "student": return redirect(url_for("login"))
    uid = session.get("user_id")
    f = request.form

    # Debug logging
    logger.info(f"Profile update request for user {uid}")
    logger.info(f"Skills: {f.get('skills')}")
    logger.info(f"Skill Ratings: {f.get('skill_ratings')}")
    logger.info(f"Tech Stack: {f.get('tech_stack')}")

    data = (uid, f.get("full_name"), f.get("register_number"), f.get("college_name"), f.get("batch_year"),
            f.get("current_semester"), f.get("skills"), f.get("skill_ratings"), f.get("experience"),
            f.get("interests"), f.get("tech_stack"), f.get("location"), datetime.now().strftime("%Y-%m-%d %H:%M"))

    existing = db_fetchall("SELECT id FROM student_profile WHERE user_id=?", (uid,))
    if existing:
        db_execute("""UPDATE student_profile SET full_name=?, register_number=?, college_name=?, batch_year=?, 
                   current_semester=?, skills=?, skill_ratings=?, experience=?, interests=?, tech_stack=?, 
                   location=?, created_at=? WHERE user_id=?""", data[1:] + (uid,))
        db_execute("DELETE FROM job_recommendations WHERE user_id=?", (uid,))
    else:
        db_execute("""INSERT INTO student_profile (user_id, full_name, register_number, college_name, batch_year, 
                   current_semester, skills, skill_ratings, experience, interests, tech_stack, location, created_at) 
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""", data)

    # Trigger Recs
    try:
        prof = db_fetchall("SELECT * FROM student_profile WHERE user_id=?", (uid,))[0]
        jobs = db_fetchall("SELECT * FROM jobs")
        logger.info(f"Generating recommendations for user {uid} with {len(jobs)} jobs")

        # Build student text for debugging
        from app import build_student_text
        student_text = build_student_text(prof)
        logger.info(f"Student text for user {uid}: '{student_text}'")

        label, results = recommend_jobs_logic(prof, jobs)
        logger.info(f"Generated {len(results)} recommendations for user {uid}")

        # Delete old recommendations
        db_execute("DELETE FROM job_recommendations WHERE user_id=?", (uid,))

        # Insert new recommendations
        inserted_count = 0
        for r in results:
            try:
                db_execute("INSERT INTO job_recommendations (user_id, job_id, match_score, match_reason, created_at) VALUES (?,?,?,?,?)",
                           (uid, r["job_id"], r["score"], r["reason"], datetime.now().strftime("%Y-%m-%d")))
                inserted_count += 1
            except Exception as e:
                logger.error(f"Error inserting recommendation for user {uid}: {e}")

        logger.info(f"Successfully inserted {inserted_count} new recommendations for user {uid}")

    except Exception as e:
        logger.error(f"Error generating recommendations for user {uid}: {e}")
        # Don't fail the profile update if recommendations fail
        flash("Profile updated! (Note: Recommendations may take a moment to update)", "warning")
        return redirect(url_for("dashboard"))

    flash("Profile updated and recommendations refreshed!", "success")
    return redirect(url_for("dashboard"))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if session.get("role") != "admin": return redirect(url_for("login"))
    if request.method == "POST":
        act = request.form.get("action")
        f = request.form
        if act == "add_job":
            db_execute("INSERT INTO jobs (title, application_link, required_skills, description, posted_by, created_at) VALUES (?,?,?,?,'admin',?)",
                       (f.get("title"), f.get("application_link"), f.get("required_skills"), f.get("description"), datetime.now().strftime("%Y-%m-%d")))
        elif act == "add_course":
            db_execute("INSERT INTO courses (title, category, description, added_by, created_at) VALUES (?,?,?,'admin',?)",
                       (f.get("title"), f.get("category"), f.get("description"), datetime.now().strftime("%Y-%m-%d")))
        elif act == "add_video":
            db_execute("INSERT INTO course_videos (course_id, video_title, video_url, category) VALUES (?,?,?,?)",
                       (f.get("course_id"), f.get("video_title"), f.get("video_url"), f.get("category")))
        elif act == "add_trend":
            db_execute("INSERT INTO job_trends (job_role, industry, trending_skills, year, added_by, created_at) VALUES (?,?,?,?,'admin',?)",
                       (f.get("job_role"), f.get("industry"), f.get("trending_skills"), f.get("year"), datetime.now().strftime("%Y-%m-%d")))
        return redirect(url_for("admin"))

    return render_template("admin_dashboard.html", 
                           jobs=db_fetchall("SELECT * FROM jobs ORDER BY id DESC"),
                           courses=db_fetchall("SELECT * FROM courses ORDER BY id DESC"),
                           videos=db_fetchall("SELECT v.*, c.title FROM course_videos v LEFT JOIN courses c ON v.course_id = c.id ORDER BY v.id DESC"),
                           trends=db_fetchall("SELECT * FROM job_trends ORDER BY id DESC"),
                           students=db_fetchall("SELECT * FROM student_profile ORDER BY id DESC"),
                           users=db_fetchall("SELECT * FROM users WHERE role='student' ORDER BY id DESC"))

@app.route("/delete/<kind>/<int:oid>")
def delete(kind, oid):
    if session.get("role") != "admin": return redirect(url_for("login"))
    tables = {"job":"jobs", "student":"student_profile", "user":"users", "course":"courses", "video":"course_videos", "trend":"job_trends"}
    if kind in tables:
        db_execute(f"DELETE FROM {tables[kind]} WHERE id=?", (oid,))
        if kind == "user": 
            db_execute("DELETE FROM student_profile WHERE user_id=?", (oid,))
            db_execute("DELETE FROM job_recommendations WHERE user_id=?", (oid,))
    return redirect(url_for("admin"))

@app.route("/download_report")
def download_report():
    if session.get("role") != "student": return redirect(url_for("login"))
    uid = session.get("user_id")
    profile = db_fetchall("SELECT * FROM student_profile WHERE user_id=?", (uid,))
    if not profile: return redirect(url_for("dashboard"))
    p = profile[0]

    # Calculate ATS compatibility insights (same logic as dashboard)
    profile_completeness = 0
    ats_insights = []

    if profile and profile[0]:
        p = profile[0]
        # Check profile completeness
        fields = [p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9], p[10], p[11], p[12]]
        filled_fields = sum(1 for f in fields if f and str(f).strip() and str(f) != 'None')
        profile_completeness = int((filled_fields / len(fields)) * 100)

        # Generate insights based on profile
        if p[7] and len(str(p[7]).split(',')) >= 3:  # Skills
            ats_insights.append("Strong skills profile with multiple technologies")
        elif p[7]:
            ats_insights.append("Add more skills to improve ATS matching")

        if p[11] and len(str(p[11]).split(',')) >= 2:  # Tech stack
            ats_insights.append("Diverse tech stack increases job opportunities")
        elif p[11]:
            ats_insights.append("Expand your tech stack for better matches")

        if p[9] and len(str(p[9]).split()) >= 10:  # Experience
            ats_insights.append("Detailed experience description helps ATS parsing")
        elif p[9]:
            ats_insights.append("Add more details to your experience section")

        recs = db_fetchall("""
            SELECT j.*, r.match_score, r.match_reason FROM job_recommendations r
            JOIN jobs j ON r.job_id = j.id WHERE r.user_id = ? ORDER BY r.match_score DESC
        """, (uid,))

        if recs and len(recs) >= 5:
            ats_insights.append("Multiple job matches found - good profile strength")
        elif recs and len(recs) >= 2:
            ats_insights.append("Some job matches generated")
        elif recs:
            ats_insights.append("Limited job matches - consider broadening skills")

        # Default insights if profile is incomplete
        if not ats_insights:
            ats_insights = [
                "Complete your profile for better recommendations",
                "Add skills, experience, and tech stack details",
                "Include specific technologies and tools you know"
            ]

    else:
        profile_completeness = 0
        ats_insights = ["Complete your profile to get personalized insights"]
        recs = []

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(300, 750, "AI CAREER REPORT")

    # Profile Summary Section
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 700, "PROFILE SUMMARY")
    c.setFont("Helvetica", 12)
    c.drawString(50, 675, f"Name: {p[2] or 'N/A'}")
    c.drawString(50, 655, f"Register Number: {p[3] or 'N/A'}")
    c.drawString(50, 635, f"College: {p[4] or 'N/A'}")
    c.drawString(50, 615, f"Batch Year: {p[5] or 'N/A'}")
    c.drawString(50, 595, f"Current Semester: {p[6] or 'N/A'}")
    c.drawString(50, 575, f"Skills: {p[7] or 'N/A'}")
    c.drawString(50, 555, f"Tech Stack: {p[11] or 'N/A'}")
    c.drawString(50, 535, f"Interests: {p[10] or 'N/A'}")
    c.drawString(50, 515, f"Location: {p[12] or 'N/A'}")

    # ATS Compatibility Insights
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 480, "ATS COMPATIBILITY INSIGHTS")
    c.setFont("Helvetica", 12)
    c.drawString(50, 460, f"Profile Completeness: {profile_completeness}%")
    y_pos = 440
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y_pos, "Optimization Tips:")
    y_pos -= 20
    c.setFont("Helvetica", 10)
    for i, insight in enumerate(ats_insights[:4]):  # Show top 4 insights
        c.drawString(50, y_pos, f"• {insight}")
        y_pos -= 15

    # Skill Analysis
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 400, "SKILL ANALYSIS")
    c.setFont("Helvetica", 12)
    recs = db_fetchall("SELECT j.title, r.match_score FROM job_recommendations r JOIN jobs j ON r.job_id = j.id WHERE r.user_id = ? ORDER BY r.match_score DESC LIMIT 1", (uid,))
    if recs:
        skill_confidence = int(recs[0][1] * 100)
        c.drawString(50, 380, f"Skill Match Confidence: {skill_confidence}%")
        c.drawString(50, 360, "Analysis: Generated by comparing your profile with job descriptions")
    else:
        c.drawString(50, 380, "Skill Match Confidence: 0%")
        c.drawString(50, 360, "Analysis: No job matches found yet")

    # Job Recommendations
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 320, "TOP JOB RECOMMENDATIONS")
    c.setFont("Helvetica", 12)
    recs = db_fetchall("SELECT j.title, r.match_score FROM job_recommendations r JOIN jobs j ON r.job_id = j.id WHERE r.user_id = ? ORDER BY r.match_score DESC LIMIT 5", (uid,))
    y = 295
    if recs:
        for i, r in enumerate(recs, 1):
            c.drawString(50, y, f"{i}. {r[0]}")
            c.drawString(400, y, f"{int(r[1]*100)}% match")
            y -= 20
    else:
        c.drawString(50, y, "No job recommendations available yet.")
        c.drawString(50, y-20, "Complete your profile and skills to get personalized recommendations.")
    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 50, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(50, 35, "KKIT Career Portal - AI-Powered Career Guidance")

    c.showPage()
    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"AI_Career_Report_{p[2] or 'Student'}.pdf", mimetype='application/pdf')

@app.route("/chat", methods=["POST"])
def chat():
    msg = request.json.get("message", "").lower()
    resp = "I can help with jobs, skills, or courses! Try asking 'What jobs are recommended?'"
    if "job" in msg: resp = "Check the 'Job Recommendations' tab for AI-matched roles!"
    elif "skill" in msg: resp = "Updating your profile with new skills will improve your matches!"
    elif "course" in msg: resp = "We have courses tailored to your profile in the 'Courses' section."
    return {"response": resp}

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5007)
