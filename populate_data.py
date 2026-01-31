import sqlite3
import csv
import os
from datetime import datetime

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "data.db")
JOBS_CSV = os.path.join(APP_DIR, "jobs.csv")

def populate_jobs():
    if not os.path.exists(JOBS_CSV):
        print(f"Error: {JOBS_CSV} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Clear existing jobs to avoid duplicates for this task
    cur.execute("DELETE FROM jobs")
    cur.execute("DELETE FROM sqlite_sequence WHERE name='jobs'")
    
    with open(JOBS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get('title')
            company = row.get('company')
            description = row.get('description')
            requirements = row.get('requirements', '').replace(';', ', ')
            posted_at = row.get('posted_at', datetime.now().strftime("%Y-%m-%d"))
            
            cur.execute("""
                INSERT INTO jobs (title, description, required_skills, posted_by, created_at) 
                VALUES (?, ?, ?, ?, ?)
            """, (title, description, requirements, company, posted_at))
    
    conn.commit()
    conn.close()
    print("Jobs populated from jobs.csv")

def populate_content():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Ensure correct schema for courses if it's messed up
    cur.execute("DROP TABLE IF EXISTS courses")
    cur.execute("CREATE TABLE courses (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, category TEXT, course_link TEXT, added_by TEXT, created_at TEXT)")

    # Sample Courses with categories based on jobs.csv skills
    courses = [
        # Programming Languages (10+ courses)
        ("Python Programming Masterclass", "Complete Python programming from basics to advanced concepts.", "Programming Languages", "https://www.python.org/about/gettingstarted/"),
        ("JavaScript Fundamentals", "Master modern JavaScript, ES6+, and programming concepts.", "Programming Languages", "https://javascript.info/"),
        ("Java Programming Complete Guide", "Learn Java from basics to enterprise development.", "Programming Languages", "https://docs.oracle.com/javase/tutorial/"),
        ("C++ Programming Essentials", "Master C++ programming for system development.", "Programming Languages", "https://cplusplus.com/doc/tutorial/"),
        ("TypeScript Development", "Build robust applications with TypeScript.", "Programming Languages", "https://www.typescriptlang.org/docs/"),
        ("C# Programming Fundamentals", "Learn C# for .NET development and enterprise applications.", "Programming Languages", "https://docs.microsoft.com/en-us/dotnet/csharp/"),
        ("Go Programming Language", "Master Go for cloud-native and concurrent applications.", "Programming Languages", "https://tour.golang.org/"),
        ("Rust Programming", "Systems programming with memory safety and performance.", "Programming Languages", "https://www.rust-lang.org/learn"),
        ("PHP Web Development", "Server-side scripting for web applications.", "Programming Languages", "https://www.php.net/docs.php"),
        ("Ruby Programming", "Dynamic programming language for web development.", "Programming Languages", "https://www.ruby-lang.org/en/documentation/"),
        ("Swift Programming", "Modern programming language for iOS and macOS.", "Programming Languages", "https://docs.swift.org/swift-book/"),
        ("Kotlin Programming", "Modern language for JVM and Android development.", "Programming Languages", "https://kotlinlang.org/docs/home.html"),

        # Web Development (8 courses)
        ("React.js Complete Guide", "Professional frontend development with modern React.", "Web Development", "https://react.dev/learn"),
        ("Node.js Backend Development", "Build scalable server-side applications with Node.js.", "Web Development", "https://nodejs.org/en/docs/guides/"),
        ("Django Web Framework", "Full-stack Python web development with Django.", "Web Development", "https://docs.djangoproject.com/en/stable/"),
        ("Flask Web Development", "Lightweight Python web framework for rapid development.", "Web Development", "https://flask.palletsprojects.com/en/stable/"),
        ("CSS & HTML Mastery", "Complete guide to modern web styling and structure.", "Web Development", "https://developer.mozilla.org/en-US/docs/Web/HTML"),
        ("GraphQL API Development", "Build efficient APIs with GraphQL.", "Web Development", "https://graphql.org/learn/"),
        ("Redux State Management", "Advanced state management for React applications.", "Web Development", "https://redux.js.org/introduction/getting-started"),
        ("Vue.js Framework", "Progressive JavaScript framework for web interfaces.", "Web Development", "https://vuejs.org/guide/introduction.html"),

        # Data Science & ML (6 courses - already good)
        ("Python for Data Science", "Master Python, Pandas, and NumPy for data analysis.", "Data Science & ML", "https://www.coursera.org/specializations/python-data-science"),
        ("Machine Learning with Scikit-Learn", "Build predictive models with Python's ML library.", "Data Science & ML", "https://scikit-learn.org/stable/tutorial/index.html"),
        ("Deep Learning Specialization", "Master neural networks and advanced ML techniques.", "Data Science & ML", "https://www.coursera.org/specializations/deep-learning"),
        ("TensorFlow Developer Certificate", "Professional machine learning with TensorFlow.", "Data Science & ML", "https://www.tensorflow.org/certificate"),
        ("PyTorch Deep Learning", "Build neural networks with PyTorch framework.", "Data Science & ML", "https://pytorch.org/tutorials/"),
        ("MATLAB Programming", "Scientific computing and data analysis with MATLAB.", "Data Science & ML", "https://www.mathworks.com/products/matlab.html"),

        # Databases (6 courses)
        ("SQL Database Mastery", "Complete SQL database design and querying.", "Databases", "https://www.w3schools.com/sql/"),
        ("MongoDB Developer Course", "NoSQL database development with MongoDB.", "Databases", "https://docs.mongodb.com/manual/tutorial/"),
        ("PostgreSQL Administration", "Advanced PostgreSQL database management.", "Databases", "https://www.postgresql.org/docs/"),
        ("MySQL Database Design", "MySQL database administration and optimization.", "Databases", "https://dev.mysql.com/doc/mysql-getting-started/en/"),
        ("Redis In-Memory Database", "In-memory data structure store.", "Databases", "https://redis.io/documentation"),
        ("Firebase Database", "Cloud-hosted NoSQL database.", "Databases", "https://firebase.google.com/docs/database"),

        # DevOps & Cloud (6 courses - already good)
        ("Docker Containerization", "Master Docker for application deployment.", "DevOps & Cloud", "https://docs.docker.com/get-started/"),
        ("Kubernetes Orchestration", "Container orchestration with Kubernetes.", "DevOps & Cloud", "https://kubernetes.io/docs/tutorials/"),
        ("AWS Cloud Architecture", "Design scalable applications on AWS.", "DevOps & Cloud", "https://aws.amazon.com/training/"),
        ("Azure Cloud Services", "Microsoft Azure cloud platform development.", "DevOps & Cloud", "https://docs.microsoft.com/en-us/azure/"),
        ("Git Version Control", "Master Git for collaborative development.", "DevOps & Cloud", "https://git-scm.com/doc"),
        ("Linux System Administration", "Linux server management and automation.", "DevOps & Cloud", "https://www.linux.org/forums/linux-beginner-tutorials.123/"),

        # Mobile Development (6 courses)
        ("Flutter Mobile Development", "Cross-platform mobile apps with Flutter.", "Mobile Development", "https://flutter.dev/learn"),
        ("React Native Development", "Build mobile apps with React Native.", "Mobile Development", "https://reactnative.dev/docs/getting-started"),
        ("Android App Development", "Native Android application development.", "Mobile Development", "https://developer.android.com/courses"),
        ("iOS App Development", "Native iOS application development with Swift.", "Mobile Development", "https://developer.apple.com/swift/"),
        ("Ionic Framework", "Cross-platform mobile apps with web technologies.", "Mobile Development", "https://ionicframework.com/docs"),
        ("Xamarin Development", "Native mobile apps with C# and .NET.", "Mobile Development", "https://dotnet.microsoft.com/en-us/apps/xamarin")
    ]

    for title, desc, cat, link in courses:
        cur.execute("INSERT INTO courses (title, description, category, course_link, added_by, created_at) VALUES (?, ?, ?, ?, 'admin', ?)",
                    (title, desc, cat, link, datetime.now().strftime("%Y-%m-%d")))
    
    # Sample Videos
    cur.execute("SELECT id, title FROM courses")
    course_map = {row[1]: row[0] for row in cur.fetchall()}
    
    videos = [
        # ===== RECOMMENDED VIDEOS (Filtered based on skill gaps) =====
        # Programming Languages
        (course_map.get("Python Programming Masterclass"), "Python Tutorial for Beginners", "https://www.youtube.com/embed/rfscVS0vtbw", "Recommended Videos"),
        (course_map.get("JavaScript Fundamentals"), "JavaScript Crash Course", "https://www.youtube.com/embed/hdI2bqOjy3c", "Recommended Videos"),
        (course_map.get("Java Programming Complete Guide"), "Java Programming Tutorial", "https://www.youtube.com/embed/eIrMbAQSU34", "Recommended Videos"),
        (course_map.get("C++ Programming Essentials"), "C++ Programming Tutorial", "https://www.youtube.com/embed/vLnPwxZdW4Y", "Recommended Videos"),
        (course_map.get("TypeScript Development"), "TypeScript Crash Course", "https://www.youtube.com/embed/BwuLxPH8IDs", "Recommended Videos"),

        # Web Development
        (course_map.get("React.js Complete Guide"), "React Tutorial for Beginners", "https://www.youtube.com/embed/dpw9EHDh2bM", "Recommended Videos"),
        (course_map.get("Node.js Backend Development"), "Node.js Crash Course", "https://www.youtube.com/embed/fBNz5xF-Kx4", "Recommended Videos"),
        (course_map.get("Django Web Framework"), "Django Tutorial for Beginners", "https://www.youtube.com/embed/rHux0gMZ3Eg", "Recommended Videos"),
        (course_map.get("Flask Web Development"), "Flask Tutorial for Beginners", "https://www.youtube.com/embed/Z1RJmh_OqeA", "Recommended Videos"),
        (course_map.get("CSS & HTML Mastery"), "HTML & CSS Crash Course", "https://www.youtube.com/embed/G3e-cpL7ofc", "Recommended Videos"),

        # Data Science & ML
        (course_map.get("Python for Data Science"), "Python for Data Science", "https://www.youtube.com/embed/rfscVS0vtbw", "Recommended Videos"),
        (course_map.get("Machine Learning with Scikit-Learn"), "Machine Learning Tutorial", "https://www.youtube.com/embed/8g2V_M2k3Pg", "Recommended Videos"),
        (course_map.get("Deep Learning Specialization"), "Deep Learning Crash Course", "https://www.youtube.com/embed/6M5VXKLf4D4", "Recommended Videos"),
        (course_map.get("TensorFlow Developer Certificate"), "TensorFlow Tutorial", "https://www.youtube.com/embed/tPYj3fFJGjk", "Recommended Videos"),
        (course_map.get("PyTorch Deep Learning"), "PyTorch Tutorial", "https://www.youtube.com/embed/icjsD6QV7q0", "Recommended Videos"),
        (course_map.get("MATLAB Programming"), "MATLAB Tutorial", "https://www.youtube.com/embed/jXvgHd0W4-Y", "Recommended Videos"),

        # Databases
        (course_map.get("SQL Database Mastery"), "SQL Tutorial for Beginners", "https://www.youtube.com/embed/9yeOJ0ZMUYw", "Recommended Videos"),
        (course_map.get("MongoDB Developer Course"), "MongoDB Crash Course", "https://www.youtube.com/embed/ofme2o29ngU", "Recommended Videos"),
        (course_map.get("PostgreSQL Administration"), "PostgreSQL Tutorial", "https://www.youtube.com/embed/qw--VYLpxG4", "Recommended Videos"),

        # DevOps & Cloud
        (course_map.get("Docker Containerization"), "Docker Tutorial for Beginners", "https://www.youtube.com/embed/pTFZFxd4hOI", "Recommended Videos"),
        (course_map.get("Kubernetes Orchestration"), "Kubernetes Tutorial", "https://www.youtube.com/embed/X48VuDVv0do", "Recommended Videos"),
        (course_map.get("AWS Cloud Architecture"), "AWS Tutorial for Beginners", "https://www.youtube.com/embed/y8YH0Qbu5h4", "Recommended Videos"),
        (course_map.get("Azure Cloud Services"), "Azure Tutorial", "https://www.youtube.com/embed/3hFPk2kox7g", "Recommended Videos"),
        (course_map.get("Git Version Control"), "Git Tutorial for Beginners", "https://www.youtube.com/embed/SWYqp7iY_Tc", "Recommended Videos"),

        # Mobile Development
        (course_map.get("Flutter Mobile Development"), "Flutter Tutorial for Beginners", "https://www.youtube.com/embed/x0D_JYGj-gI", "Recommended Videos"),
        (course_map.get("React Native Development"), "React Native Tutorial", "https://www.youtube.com/embed/0-S5a0eXPoc", "Recommended Videos"),
        (course_map.get("Android App Development"), "Android Development Tutorial", "https://www.youtube.com/embed/fis26HvvDII", "Recommended Videos"),
        (course_map.get("iOS App Development"), "iOS Development Tutorial", "https://www.youtube.com/embed/8hNQF2wH7GM", "Recommended Videos"),

        # ===== CAREER GUIDANCE =====
        (None, "Building a Successful Tech Career", "https://www.youtube.com/embed/h2H9EhGJ5uI", "Career Guidance"),
        (None, "Career Planning & Goal Setting", "https://www.youtube.com/embed/LW3vT4K2EI", "Career Guidance"),
        (None, "Freelancing vs Full-time Jobs", "https://www.youtube.com/embed/8VpFxStAMnE", "Career Guidance"),
        (None, "How to Choose the Right Career Path", "https://www.youtube.com/embed/9R4Z1wBhH3A", "Career Guidance"),
        (None, "Industry Trends & Future Skills", "https://www.youtube.com/embed/9R4Z1wBhH3A", "Career Guidance"),
        (None, "Networking & Professional Development", "https://www.youtube.com/embed/9R4Z1wBhH3A", "Career Guidance"),
        (None, "Salary Negotiation for Tech Professionals", "https://www.youtube.com/embed/9R4Z1wBhH3A", "Career Guidance"),
        (None, "Work-Life Balance in Tech Careers", "https://www.youtube.com/embed/9R4Z1wBhH3A", "Career Guidance"),

        # ===== SOFT SKILLS & PLACEMENT PREP =====
        (None, "Active Listening Skills", "https://www.youtube.com/embed/9R4Z1wBhH3A", "Soft Skills & Placement Prep"),
        (None, "Behavioral Interview Preparation", "https://www.youtube.com/embed/9R4Z1wBhH3A", "Soft Skills & Placement Prep"),
        (None, "Business Communication Etiquette", "https://www.youtube.com/embed/9R4Z1wBhH3A", "Soft Skills & Placement Prep"),
        (None, "Career Planning & Goal Setting", "https://www.youtube.com/embed/9R4Z1wBhH3A", "Soft Skills & Placement Prep"),
        (None, "Effective Communication Skills", "https://www.youtube.com/embed/9R4Z1wBhH3A", "Soft Skills & Placement Prep"),
        (None, "Email Writing & Professional Communication", "https://www.youtube.com/embed/9R4Z1wBhH3A", "Soft Skills & Placement Prep"),
        (None, "Group Discussion Techniques", "https://www.youtube.com/embed/9R4Z1wBhH3A", "Soft Skills & Placement Prep"),
        (None, "HR Interview Questions & Answers", "https://www.youtube.com/embed/9R4Z1wBhH3A", "Soft Skills & Placement Prep"),
        (None, "Presentation Skills Masterclass", "https://www.youtube.com/embed/9R4Z1wBhH3A", "Soft Skills & Placement Prep"),
        (None, "Public Speaking & Confidence Building", "https://www.youtube.com/embed/9R4Z1wBhH3A", "Soft Skills & Placement Prep"),
        (None, "Resume Writing Masterclass", "https://www.youtube.com/embed/9R4Z1wBhH3A", "Soft Skills & Placement Prep"),
        (None, "Salary Negotiation Skills", "https://www.youtube.com/embed/9R4Z1wBhH3A", "Soft Skills & Placement Prep"),
        (None, "Technical Interview Preparation", "https://www.youtube.com/embed/9R4Z1wBhH3A", "Soft Skills & Placement Prep"),
        (None, "Acing Your Next Interview", "https://www.youtube.com/embed/9R4Z1wBhH3A", "Soft Skills & Placement Prep")
    ]
    
    # Only populate videos if the videos table is empty (to avoid overwriting existing categorized videos)
    cur.execute("SELECT COUNT(*) FROM course_videos")
    video_count = cur.fetchone()[0]

    if video_count == 0:
        for c_id, title, url, cat in videos:
            cur.execute("INSERT INTO course_videos (course_id, video_title, video_url, category) VALUES (?, ?, ?, ?)",
                        (c_id, title, url, cat))
        print("Videos populated")
    else:
        print("Videos already exist, skipping video population")
    
    conn.commit()
    conn.close()
    print("Courses and Videos populated")

if __name__ == "__main__":
    populate_jobs()
    populate_content()
