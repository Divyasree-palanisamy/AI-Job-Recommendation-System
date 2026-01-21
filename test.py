import tkinter as tk
from tkinter import messagebox
import joblib
import os

# --- Load the trained model ---
model_path = "models/job_recommendation_type_knn.pkl"

if not os.path.exists(model_path):
    messagebox.showerror("Error", f"Model file not found: {model_path}")
    exit()

model = joblib.load(model_path)

# --- Prediction function ---
def predict_job_type():
    skills = entry_skills.get("1.0", "end-1c").strip()
    degree = entry_degree.get().strip()
    resume_text = entry_resume.get("1.0", "end-1c").strip()
    requirements = entry_requirements.get("1.0", "end-1c").strip()

    if not skills or not degree:
        messagebox.showwarning("Missing Input", "Please fill all required fields!")
        return

    # Combine text same as training phase
    combined_text = f"{skills} {degree} {resume_text} {requirements}"

    try:
        prediction = model.predict([combined_text])[0]
        result_label.config(
            text=f"🎯 Recommended Job Type: {prediction}",
            fg="#27ae60"
        )
    except Exception as e:
        messagebox.showerror("Error", f"Prediction failed: {str(e)}")

# --- GUI Setup ---
root = tk.Tk()
root.title("Smart Career Recommendation System")
root.geometry("750x650")
root.configure(bg="#f5f7fa")

# --- Heading ---
tk.Label(
    root, text="Smart Career Recommendation System",
    font=("Arial", 20, "bold"), bg="#f5f7fa", fg="#2c3e50"
).pack(pady=20)

# --- Degree ---
tk.Label(root, text="Degree / Education:", bg="#f5f7fa", font=("Arial", 12, "bold")).pack(anchor="w", padx=30)
entry_degree = tk.Entry(root, width=80)
entry_degree.pack(padx=30, pady=5)

# --- Skills ---
tk.Label(root, text="Skills:", bg="#f5f7fa", font=("Arial", 12, "bold")).pack(anchor="w", padx=30)
entry_skills = tk.Text(root, height=3, width=80)
entry_skills.pack(padx=30, pady=5)

# --- Resume Summary ---
tk.Label(root, text="Resume Summary:", bg="#f5f7fa", font=("Arial", 12, "bold")).pack(anchor="w", padx=30)
entry_resume = tk.Text(root, height=5, width=80)
entry_resume.pack(padx=30, pady=5)

# --- Job Requirements / Interest ---
tk.Label(root, text="Job Requirements / Interest:", bg="#f5f7fa", font=("Arial", 12, "bold")).pack(anchor="w", padx=30)
entry_requirements = tk.Text(root, height=3, width=80)
entry_requirements.pack(padx=30, pady=5)

# --- Predict Button ---
tk.Button(
    root, text="🔍 Recommend Suitable Job",
    font=("Arial", 14, "bold"), bg="#2ecc71", fg="white",
    padx=15, pady=5, command=predict_job_type
).pack(pady=25)

# --- Result Label ---
result_label = tk.Label(
    root, text="", font=("Arial", 16, "bold"), bg="#f5f7fa", fg="#27ae60"
)
result_label.pack(pady=10)

# --- Footer ---
tk.Label(
    root, text="AI-Powered Career Guidance Portal © 2025",
    bg="#f5f7fa", fg="#7f8c8d", font=("Arial", 10)
).pack(side="bottom", pady=10)

# --- Run GUI ---
root.mainloop()
