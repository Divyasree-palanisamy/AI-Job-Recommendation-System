import sqlite3

# Connect to database
conn = sqlite3.connect('data.db')
cur = conn.cursor()

# Video URL updates with the provided YouTube links
video_updates = {
    # Technical videos
    'MATLAB Tutorial': 'https://www.youtube.com/embed/1XiIZczRyAQ',
    'Deep Learning Crash Course': 'https://www.youtube.com/embed/VyWAvY2CF9c',
    'Firebase Database Guide': 'https://www.youtube.com/embed/fgdpvwEWJ9M',
    'Redis In-Memory Database': 'https://www.youtube.com/embed/Vx2zPMPvmug',
    'Cloud Architecture Patterns': 'https://www.youtube.com/embed/8uaWoKkyIWk',
    'Azure Tutorial': 'https://www.youtube.com/embed/10jm7Waan8M',
    'Ionic Framework Tutorial': 'https://www.youtube.com/embed/5Gj4Y8zvl-s',
    'GraphQL API Development': 'https://www.youtube.com/embed/5199E50O7SI',
    'Angular Framework Guide': 'https://www.youtube.com/embed/XVCAaV-hSe4',
    'HTML & CSS Crash Course': 'https://www.youtube.com/embed/hu-q2zYwEYs',

    # Soft skills videos
    'Work-Life Balance in Tech Careers': 'https://www.youtube.com/embed/V2u2Lgr2Yfw',
    'Salary Negotiation for Tech Professionals': 'https://www.youtube.com/embed/4uIj-5uHWnE',
    'How to Choose the Right Career Path': 'https://www.youtube.com/embed/LQKYpfgq6MQ',
    'Freelancing vs Full-time Jobs': 'https://www.youtube.com/embed/oBVD0eFx3fA',
    'Building a Successful Tech Career': 'https://www.youtube.com/embed/MN7yfV4UuCI',
    'Acing Your Next Interview': 'https://www.youtube.com/embed/fYHR0KgnGHU',
    'Technical Interview Preparation': 'https://www.youtube.com/embed/7UlslIXHNsw',
    'Salary Negotiation Skills': 'https://www.youtube.com/embed/kPscK6RQPSw',
    'Resume Writing Masterclass': 'https://www.youtube.com/embed/z9oEbG1GhqM',
    'Public Speaking & Confidence Building': 'https://www.youtube.com/embed/IitIl2C3Iy8',
    'Presentation Skills Masterclass': 'https://www.youtube.com/embed/dHAbmoFHqgA',
    'HR Interview Questions & Answers': 'https://www.youtube.com/embed/zIm_k9j0C50',
    'Group Discussion Techniques': 'https://www.youtube.com/embed/HAnw168huqA',
    'Email Writing & Professional Communication': 'https://www.youtube.com/embed/pIHRGFN-mXI',
    'Effective Communication Skills': 'https://www.youtube.com/embed/lg48Bi9DA54',
    'Business Communication Etiquette': 'https://www.youtube.com/embed/WESGDi_ajUU',
    'Behavioral Interview Preparation': 'https://www.youtube.com/embed/2uM7gYuOvr4',
    'Active Listening Skills': 'https://www.youtube.com/embed/Yq5pJ0q3xuc'
}

print("Updating video URLs with provided YouTube links...")

# Update each video URL
for video_title, new_url in video_updates.items():
    cur.execute('UPDATE course_videos SET video_url = ? WHERE video_title = ?',
               (new_url, video_title))
    print(f"Updated: {video_title}")

conn.commit()

# Verification
print("\n" + "="*50)
print("VERIFICATION:")
cur.execute('SELECT COUNT(*) FROM course_videos WHERE video_url LIKE ?', ('https://www.youtube.com/embed/%',))
youtube_count = cur.fetchone()[0]
print(f"Videos with YouTube embed URLs: {youtube_count}")

cur.execute('SELECT COUNT(*) FROM course_videos')
total_count = cur.fetchone()[0]
print(f"Total videos in database: {total_count}")

# Show a few sample updates
print("\nSample updated videos:")
cur.execute('SELECT video_title, video_url FROM course_videos LIMIT 5')
samples = cur.fetchall()
for title, url in samples:
    print(f"{title}: {url}")

conn.close()
print("Video URL updates completed!")