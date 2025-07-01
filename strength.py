import tkinter as tk
import re

def check_strength(password):
    score = 0
    length = len(password)
    feedback = []

    # Count types
    upper = len(re.findall(r"[A-Z]", password))
    lower = len(re.findall(r"[a-z]", password))
    digits = len(re.findall(r"\d", password))
    symbols = len(re.findall(r"[!@#$%^&*(),.?\":{}|<>]", password))
    middle = len(re.findall(r"(?<=\w)[\d!@#$%^&*()](?=\w)", password))  # digits/symbols in middle

    requirements = 0
    if length >= 8: requirements += 1
    if upper > 0: requirements += 1
    if lower > 0: requirements += 1
    if digits > 0: requirements += 1
    if symbols > 0: requirements += 1

    # Positive scoring
    score += length * 4
    if upper: score += (length - upper) * 2
    if lower: score += (length - lower) * 2
    if digits: score += digits * 4
    if symbols: score += symbols * 6
    if middle: score += middle * 2
    if requirements >= 4: score += requirements * 2

    # Negative scoring
    if password.isalpha():  # only letters
        score -= length
        feedback.append("Contains only letters")

    if password.isdigit():  # only numbers
        score -= length
        feedback.append("Contains only numbers")

    # Repeated characters penalty
    repeat_penalty = len(password) - len(set(password))
    if repeat_penalty > 0:
        score -= repeat_penalty * 2
        feedback.append("Repeated characters")

    # Limit score between 0 and 100
    score = max(0, min(score, 100))

    return score, feedback

def evaluate():
    pwd = entry.get()
    score, issues = check_strength(pwd)

    # Feedback summary
    if score >= 90:
        summary = "Excellent – Secure password"
    elif score >= 70:
        summary = "Strong – Good password"
    elif score >= 50:
        summary = "Moderate – Improve further"
    else:
        summary = "Weak – Needs improvement"

    result.set(f"Strength: {score}%")
    tips.set(f"Feedback: {summary}")
    details.set("Suggestions: " + (", ".join(issues) if issues else "Well-balanced password!"))

# GUI setup
root = tk.Tk()
root.title("Advanced Password Strength Checker")
root.geometry("440x260")

tk.Label(root, text="Enter Password:").pack(pady=5)
entry = tk.Entry(root, width=35, show="")
entry.pack()

tk.Button(root, text="Check Strength", command=evaluate).pack(pady=10)

result = tk.StringVar()
tk.Label(root, textvariable=result, font=("Arial", 12)).pack()

tips = tk.StringVar()
tk.Label(root, textvariable=tips, font=("Arial", 10), fg="red").pack()

details = tk.StringVar()
tk.Label(root, textvariable=details, wraplength=400, fg="gray").pack()

root.mainloop()
