# Smart Career Guidance & Employment Portal

A comprehensive AI-powered career guidance platform that provides personalized job recommendations, course suggestions, and skill development resources for students.

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

## 🎯 Overview

The Smart Career Guidance & Employment Portal is an AI-driven platform that helps students make informed career decisions through:

- **Personalized Job Matching**: AI-powered job recommendations based on student profiles
- **Skill Gap Analysis**: Identifies missing skills and provides targeted learning resources
- **Career Development Resources**: Curated courses and videos for skill enhancement
- **Interactive Dashboard**: User-friendly interface for career planning and progress tracking

### 🎭 User Roles

#### **Student**
- Create and manage career profile
- View AI-powered job recommendations
- Access personalized learning resources
- Track career development progress
- Download career reports

#### **Admin**
- Manage job listings and trends
- Add/manage courses and videos
- Oversee user accounts
- Monitor platform usage

## ✨ Features

### 🤖 AI-Powered Recommendations
- **Advanced Skill Matching**: Sophisticated algorithm analyzing individual skills with ratings
- **Experience-Based Scoring**: Considers years of experience vs. job requirements
- **Skill Gap Analysis**: Detailed breakdown of missing vs. present skills
- **Realistic Confidence Scores**: Capped at 95% with skill gap considerations
- **Personalized Learning**: Recommends relevant courses and videos based on gaps
- **Career Insights**: Provides industry trends and market intelligence

### 📚 Learning Resources
- **Dynamic Course Library**: Automatically organized by skill domains from job requirements
- **Video Modules**: Three sections - Communication Training, Placement Preparation, Recommended Videos
- **Interactive Course Tabs**: Clickable sections that dynamically appear based on available courses
- **Auto-Categorization**: New course categories automatically create new sections
- **Smart Filtering**: Courses filtered based on student skills and job matches

### 📊 Career Analytics & Visual Intelligence
- **Interactive Trend Analytics**: Beautiful circular progress charts showing skill demand
- **Visual Market Intelligence**: Professional dashboard with trend cards and statistics
- **Career Reports**: Downloadable PDF reports with insights
- **Skill Match Analysis**: Detailed competency assessment with visual progress indicators
- **Job Compatibility Scores**: ATS-style matching percentages
- **Industry Trends**: Real-time market intelligence with animated visualizations

### 🔐 Security & User Management
- **Secure Authentication**: Hashed passwords and session management
- **Role-Based Access**: Separate interfaces for students and admins
- **Profile Management**: Comprehensive career profile creation
- **Data Privacy**: Secure handling of personal information

## 💻 System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, Linux (Ubuntu 18.04+)
- **Python Version**: Python 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB free space
- **Browser**: Modern web browser (Chrome, Firefox, Safari, Edge)

### Dependencies
```
Flask==2.3.3
joblib==1.3.2
scikit-learn==1.3.0
pandas==2.0.3
numpy==1.24.3
reportlab==4.0.4
sqlite3 (built-in with Python)
```

## 🚀 Installation

### Step 1: Clone or Download
```bash
# If using git
git clone <repository-url>
cd smart-career-portal

# Or download and extract the ZIP file
# Extract to your desired directory
cd extracted-folder
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install manually:
```bash
pip install flask joblib scikit-learn pandas numpy reportlab
```

### Step 4: Download ML Model
Ensure the pre-trained ML model file (`career_model.pkl`) and vectorizer (`tfidf_vectorizer.pkl`) are in the project root directory.

## 🗄️ Database Setup

The application uses SQLite database which is automatically created. To populate with sample data:

### Step 1: Run Data Population Script
```bash
python populate_data.py
```

This will:
- Create database tables
- Populate sample jobs from `jobs.csv`
- Add sample courses and videos
- Set up initial admin user

### Step 2: Verify Database
Check that `data.db` file is created in the project directory.

## ▶️ Running the Application

### Method 1: Direct Python Execution
```bash
python 1.py
```

### Method 2: Using Python Interpreter
```bash
python3 1.py
```

### Method 3: Flask Development Server
```bash
export FLASK_APP=1.py
export FLASK_ENV=development
flask run --host=127.0.0.1 --port=5007
```

### Accessing the Application
1. Open web browser
2. Navigate to: `http://127.0.0.1:5007`
3. Default admin credentials:
   - Username: `admin`
   - Password: `admin1234`

## 📖 Usage Guide

### 🔐 First Time Setup

#### **Student Registration**
1. Click "Register" on the login page
2. Fill in: Username, Email, Password
3. Login with your credentials
4. Complete your career profile (mandatory)

#### **Admin Access**
- Use default credentials: `admin` / `admin1234`
- Change password after first login

### 👨‍🎓 Student Dashboard

#### **Complete Career Profile**
1. Go to "Career Profile" section
2. Fill in all required fields:
   - Personal Information (Name, Register Number, College, etc.)
   - Skills with proficiency ratings (1-5 scale)
   - Career interests and preferences
3. Click "View Results" to generate recommendations

#### **Navigate Dashboard Sections**
- **🏠 Home**: Introduction and AI Career Chatbot
- **👤 Career Profile**: Manage your profile and skills
- **💼 Career Path & Jobs**: AI-recommended job opportunities
- **📈 Job Trends**: Industry insights and market trends
- **📚 Courses**: Categorized learning paths (click tabs to explore)
- **🎥 Video Modules**: Three sections of educational content
- **📄 Career Report**: Download detailed career analysis

#### **Video Learning Sections**
- **💬 Communication Training**: Professional communication skills (always available)
- **🎯 Placement Preparation**: Interview and career preparation (always available)
- **🎓 Recommended Videos**: Skill-specific videos based on your gaps

#### **Course Exploration**
- Click on category tabs (Programming, Web Dev, Data Science, etc.)
- View relevant courses for your skill development
- Enroll in courses directly via provided links

### 👨‍💼 Admin Dashboard

#### **Managing Jobs**
1. Go to "Manage Jobs" section
2. Add new jobs with title, description, required skills, and application links
3. Edit or delete existing jobs
4. Jobs are automatically matched to student profiles

#### **Managing Courses**
1. Go to "Manage Courses" section
2. Add courses with category, title, description, and enrollment links
3. Assign courses to appropriate skill domains
4. Students see filtered courses based on their profiles

#### **Managing Videos**
1. Go to "Manage Videos" section
2. Add videos to three categories:
   - **Communication Training**: General career communication skills
   - **Placement Preparation**: Interview and job search skills
   - **Recommended Videos**: Skill-specific learning content
3. Videos are filtered on student side based on category rules

#### **Managing Job Trends**
1. Add industry trends and insights
2. Include trending skills and market data
3. Students see trends matching their interests

## 🔗 API Endpoints

### Authentication
- `GET /` - Home/Login page
- `POST /login` - User authentication
- `POST /register` - New user registration
- `GET /logout` - User logout

### Student Dashboard
- `GET /dashboard` - Main dashboard (requires authentication)
- `POST /save_profile` - Save/update career profile
- `GET /download_report` - Generate PDF career report

### Admin Functions
- `GET /admin` - Admin dashboard
- `POST /admin` - Handle admin actions (add/edit/delete content)

### Utility
- `GET /delete/<kind>/<id>` - Delete content (admin only)

## 📁 Project Structure

```
smart-career-portal/
├── 1.py                    # Main Flask application
├── populate_data.py        # Database initialization script
├── jobs.csv               # Sample job data
├── data.db               # SQLite database (auto-generated)
├── career_model.pkl      # Pre-trained ML model
├── tfidf_vectorizer.pkl  # Text vectorizer
├── templates/            # HTML templates
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── admin_dashboard.html
├── static/               # CSS, JS, images (if any)
└── README.md            # This documentation
```

## 🔧 Troubleshooting

### Common Issues

#### **Port Already in Use**
```bash
# Kill process using port 5007
# Windows
netstat -ano | findstr :5007
taskkill /PID <PID> /F

# Linux/macOS
lsof -ti:5007 | xargs kill -9
```

#### **Database Errors**
```bash
# Delete and recreate database
rm data.db
python populate_data.py
```

#### **ML Model Not Found**
- Ensure `career_model.pkl` and `tfidf_vectorizer.pkl` are in project root
- Check file permissions

#### **Import Errors**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Performance Tips
- Use virtual environment to avoid dependency conflicts
- Close browser tabs when not in use to free memory
- Restart server periodically for optimal performance

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Commit changes: `git commit -am 'Add feature'`
5. Push to branch: `git push origin feature-name`
6. Create Pull Request

### Code Standards
- Follow PEP 8 Python style guide
- Add comments for complex logic
- Test all new features thoroughly
- Update documentation for API changes

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For technical support or questions:
- Check the troubleshooting section above
- Review the usage guide for common scenarios
- Ensure all system requirements are met

---

**🎓 Happy Career Planning!**

This platform empowers students to make informed career decisions through AI-driven insights and personalized learning recommendations.</content>
</xai:function_call">Writing to README.md
