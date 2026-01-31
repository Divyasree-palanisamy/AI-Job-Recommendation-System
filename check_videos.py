import sqlite3

conn = sqlite3.connect('data.db')
cur = conn.cursor()

# Check sample videos
print("Sample Programming Languages videos:")
cur.execute("SELECT video_title, video_url FROM course_videos WHERE category = 'Programming Languages' LIMIT 3")
videos = cur.fetchall()
for title, url in videos:
    print(f"{title}: {url}")

# Check placeholder count
print("\nChecking for placeholder URLs...")
cur.execute("SELECT COUNT(*) FROM course_videos WHERE video_url = 'https://www.youtube.com/embed/9R4Z1wBhH3A'")
count = cur.fetchone()[0]
print(f"Placeholder URLs remaining: {count}")

# Check total videos
cur.execute("SELECT COUNT(*) FROM course_videos")
total = cur.fetchone()[0]
print(f"Total videos in database: {total}")

conn.close()