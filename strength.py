import tkinter as tk
from tkinter import ttk
import re
import string
from zxcvbn import zxcvbn 


RE_UPPER = re.compile(r"[A-Z]")
RE_LOWER = re.compile(r"[a-z]")
RE_DIGITS = re.compile(r"\d")
RE_SYMBOLS = re.compile(r"[" + re.escape(string.punctuation) + "]") 
RE_MIDDLE_NUM_SYM = re.compile(r"(?<=\w)[\d" + re.escape(string.punctuation) + r"](?=\w)") 


COMMON_PASSWORDS = {
    "password", "123456", "qwerty", "admin", "12345678", "dragon",
    "abcde", "test", "hello", "111111", "football"
}

def check_strength(password):
    # Use zxcvbn for comprehensive evaluation
    zxcvbn_result = zxcvbn(password)
    zxcvbn_score = zxcvbn_result['score'] 
    zxcvbn_feedback = zxcvbn_result['feedback']['suggestions']

    score_messages = {
        0: "Very Weak",
        1: "Weak",
        2: "Fair",
        3: "Good",
        4: "Excellent"
    }


    feedback = []
    
    # Pre-calculate counts once for efficiency
    length = len(password)
    num_upper = len(RE_UPPER.findall(password))
    num_lower = len(RE_LOWER.findall(password))
    num_digits = len(RE_DIGITS.findall(password))
    num_symbols = len(RE_SYMBOLS.findall(password))

    # Determine individual checks for GUI
    has_min_length = length >= 8
    has_upper = num_upper > 0
    has_lower = num_lower > 0
    has_digit = num_digits > 0
    has_symbol = num_symbols > 0

    # Custom Rule-based Feedback (enhances zxcvbn's feedback)
    if not has_min_length:
        feedback.append("Increase length (min. 8 characters recommended)")
    if not has_upper:
        feedback.append("Add uppercase letters")
    if not has_lower:
        feedback.append("Add lowercase letters")
    if not has_digit:
        feedback.append("Add digits")
    if not has_symbol:
        feedback.append("Add special characters")

    # Check for common passwords (highly reliable check)
    if password.lower() in COMMON_PASSWORDS:
        feedback.append("Password is too common. Choose a unique one.")
        # If it's a common password, it should automatically be very weak regardless of zxcvbn score
        zxcvbn_score = min(zxcvbn_score, 1) # Cap score at 'Weak' if common

    # Check for simple character type only passwords (efficiency: using built-in methods)
    if password.isalpha() and length > 0: # Check length to avoid empty string issues
        feedback.append("Avoid using only letters")
        zxcvbn_score = min(zxcvbn_score, 1)
    if password.isdigit() and length > 0:
        feedback.append("Avoid using only numbers")
        zxcvbn_score = min(zxcvbn_score, 0) # Even weaker if only digits

    # Penalize consecutive numbers/alphabets (e.g., 123, abc, def)
    # Using a single loop for efficiency
    for i in range(length - 2):
        if password[i].isdigit() and password[i+1].isdigit() and password[i+2].isdigit():
            val1, val2, val3 = int(password[i]), int(password[i+1]), int(password[i+2])
            if (val2 - val1 == 1 and val3 - val2 == 1) or \
               (val1 - val2 == 1 and val2 - val3 == 1):
                if "Consecutive numbers" not in feedback:
                    feedback.append("Avoid consecutive numbers (e.g., 123, 321)")
                    zxcvbn_score = min(zxcvbn_score, 1) # Reduce score
                    break # Only add message once


    if zxcvbn_score > 1:
        unique_chars = set(password)
        if length > 0 and (length - len(unique_chars)) / length > 0.3: # More than 30% repeated characters
            if "Too many repeated characters" not in feedback:
                feedback.append("Too many repeated characters")
                zxcvbn_score = min(zxcvbn_score, 2) # Mild penalty


    if not feedback: 
        feedback = zxcvbn_feedback if zxcvbn_feedback else ["Password looks good!"]
    else:

        for suggestion in zxcvbn_feedback:
            if suggestion not in feedback:
                feedback.append(suggestion)



    mapped_score = zxcvbn_score * 25
    if has_min_length and has_upper and has_lower and has_digit and has_symbol and zxcvbn_score == 4:
        mapped_score = 100 # Ensure 100% for excellent passwords

    return mapped_score, feedback, (has_min_length, has_upper, has_lower, has_digit, has_symbol), score_messages[zxcvbn_score]


def evaluate(*args):
    pwd = entry.get()
    score, issues, checks, summary_text = check_strength(pwd)


    if score >= 90:
        color = "green"
    elif score >= 70:
        color = "blue"
    elif score >= 50:
        color = "orange"
    else:
        color = "red"

    result.set(f"{score}% - {summary_text}")
    progress['value'] = score
    strength_label.config(fg=color)
    details.set("\n".join(issues) if issues else "Well-balanced password!")

    checklist_vars[0].set(f" {'✔' if checks[0] else '✖'} Min. 8 chars")
    checklist_vars[1].set(f" {'✔' if checks[1] else '✖'} Uppercase")
    checklist_vars[2].set(f" {'✔' if checks[2] else '✖'} Lowercase")
    checklist_vars[3].set(f" {'✔' if checks[3] else '✖'} Digit")
    checklist_vars[4].set(f" {'✔' if checks[4] else '✖'} Symbol")

def toggle_password():
    if entry.cget('show') == '':
        entry.config(show='*')
        toggle_btn.config(text='Show')
    else:
        entry.config(show='')
        toggle_btn.config(text='Hide')

def copy_password():
    root.clipboard_clear()
    root.clipboard_append(entry.get())
    copy_btn.config(text="Copied!", fg="green")
    root.after(1500, lambda: copy_btn.config(text="Copy", fg="black"))

# GUI Setup
root = tk.Tk()
root.title("Password Strength Evaluator")
root.geometry("480x450") 
root.resizable(False, False)


style = ttk.Style()
style.configure("Check.TLabel", font=("Arial", 10))

tk.Label(root, text="Enter Password:", font=("Arial", 11)).pack(pady=5)
entry = tk.Entry(root, width=35, show='*', font=("Arial", 11))
entry.pack()
entry.bind("<KeyRelease>", evaluate)

frame = tk.Frame(root)
frame.pack(pady=5)
toggle_btn = tk.Button(frame, text="Show", command=toggle_password, width=10)
toggle_btn.pack(side='left', padx=5)
copy_btn = tk.Button(frame, text="Copy", command=copy_password, width=10)
copy_btn.pack(side='left')

tk.Button(root, text="Check Strength", command=evaluate).pack(pady=5)

progress = ttk.Progressbar(root, length=300, maximum=100)
progress.pack(pady=5)

result = tk.StringVar()
strength_label = tk.Label(root, textvariable=result, font=("Arial", 12, "bold"))
strength_label.pack()

details = tk.StringVar()
tk.Label(root, textvariable=details, wraplength=440, fg="gray", justify='left').pack(pady=(5,0)) 


checklist_frame = tk.Frame(root)
checklist_frame.pack(pady=5, anchor='w', padx=60) 

checklist_vars = [tk.StringVar() for _ in range(5)]
checklist_labels = []
for i in range(5):
    label = tk.Label(checklist_frame, textvariable=checklist_vars[i], font=("Arial", 10), anchor='w')
    label.pack(fill='x')
    checklist_labels.append(label)


root.mainloop()