import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import string
from zxcvbn import zxcvbn
from itertools import product
import random

# Regex patterns
RE_UPPER = re.compile(r"[A-Z]")
RE_LOWER = re.compile(r"[a-z]")
RE_DIGITS = re.compile(r"\d")
RE_SYMBOLS = re.compile(r"[" + re.escape(string.punctuation) + "]")
RE_MIDDLE_NUM_SYM = re.compile(r"(?<=\w)[\d" + re.escape(string.punctuation) + r"](?=\w)")

# Common passwords list
COMMON_PASSWORDS = {
    "password", "123456", "qwerty", "admin", "12345678", "dragon",
    "abcde", "test", "hello", "111111", "football"
}

def contains_consecutive_numbers(s):
    """Checks if a string contains three or more consecutive ascending or descending digits."""
    for i in range(len(s) - 2):
        if s[i].isdigit() and s[i+1].isdigit() and s[i+2].isdigit():
            val1, val2, val3 = int(s[i]), int(s[i+1]), int(s[i+2])
            if (val2 - val1 == 1 and val3 - val2 == 1) or \
               (val1 - val2 == 1 and val2 - val3 == 1):
                return True
    return False

def check_strength(password):
    """Evaluates password strength using zxcvbn and custom rules."""
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

    length = len(password)
    num_upper = len(RE_UPPER.findall(password))
    num_lower = len(RE_LOWER.findall(password))
    num_digits = len(RE_DIGITS.findall(password))
    num_symbols = len(RE_SYMBOLS.findall(password))

    has_min_length = length >= 8
    has_upper = num_upper > 0
    has_lower = num_lower > 0
    has_digit = num_digits > 0
    has_symbol = num_symbols > 0

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

    if password.lower() in COMMON_PASSWORDS:
        feedback.append("Password is too common. Choose a unique one.")
        zxcvbn_score = min(zxcvbn_score, 1)

    if password.isalpha() and length > 0:
        feedback.append("Avoid using only letters")
        zxcvbn_score = min(zxcvbn_score, 1)
    if password.isdigit() and length > 0:
        feedback.append("Avoid using only numbers")
        zxcvbn_score = min(zxcvbn_score, 0)

    # Re-using the standalone function for consistency
    if contains_consecutive_numbers(password):
        if "Consecutive numbers" not in feedback:
            feedback.append("Avoid consecutive numbers (e.g., 123, 321)")
            zxcvbn_score = min(zxcvbn_score, 1)


    if zxcvbn_score > 1:
        unique_chars = set(password)
        if length > 0 and (length - len(unique_chars)) / length > 0.3:
            if "Too many repeated characters" not in feedback:
                feedback.append("Too many repeated characters")
                zxcvbn_score = min(zxcvbn_score, 2)

    if not feedback:
        feedback = zxcvbn_feedback if zxcvbn_feedback else ["Password looks good!"]
    else:
        for suggestion in zxcvbn_feedback:
            if suggestion not in feedback:
                feedback.append(suggestion)

    mapped_score = zxcvbn_score * 25
    if has_min_length and has_upper and has_lower and has_digit and has_symbol and zxcvbn_score == 4:
        mapped_score = 100

    return mapped_score, feedback, (has_min_length, has_upper, has_lower, has_digit, has_symbol), score_messages[zxcvbn_score]


def evaluate(*args):
    """Updates the strength evaluation display."""
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
    """Toggles password visibility."""
    if entry.cget('show') == '':
        entry.config(show='*')
        toggle_btn.config(text='Show')
    else:
        entry.config(show='')
        toggle_btn.config(text='Hide')

def copy_password():
    """Copies the password to the clipboard."""
    root.clipboard_clear()
    root.clipboard_append(entry.get())
    copy_btn.config(text="Copied!", fg="green")
    root.after(1500, lambda: copy_btn.config(text="Copy", fg="black"))

def generate_complex_variations(word):
    """Generates complex variations of a single word, excluding consecutive numbers."""
    variations = set()
    word_lower = word.lower()
    word_capitalize = word.capitalize()
    word_upper = word.upper()

    # Base variations - check immediately
    if not contains_consecutive_numbers(word):
        variations.add(word)
    if not contains_consecutive_numbers(word_lower):
        variations.add(word_lower)
    if not contains_consecutive_numbers(word_capitalize):
        variations.add(word_capitalize)
    if not contains_consecutive_numbers(word_upper):
        variations.add(word_upper)

    # Leet speak simple replacements
    leet_map = {'a': '@', 's': '$', 'i': '!', 'o': '0', 'e': '3', 'l': '1', 't': '7', 'g': '9', 'b': '8'}
    
    # Helper for applying leet, defined here to use within this scope
    def apply_leet_local(w):
        new_word_list = []
        for char in w:
            if char.lower() in leet_map and random.random() < 0.7: # Randomly apply leet
                new_word_list.append(leet_map[char.lower()])
            else:
                new_word_list.append(char)
        return "".join(new_word_list)

    temp_leet_variations = {apply_leet_local(word), apply_leet_local(word_lower), apply_leet_local(word_capitalize)}
    for v_leet in temp_leet_variations:
        if not contains_consecutive_numbers(v_leet):
            variations.add(v_leet)

    # Add common numbers and symbols
    common_suffixes = ["1!", "2025@", "!", "#", "$", "123", "789", "@$", "!!", "@@"]
    # Iterate over a copy because we're adding to the set
    for v in list(variations):
        for suffix in common_suffixes:
            new_v_suffix = v + suffix
            if not contains_consecutive_numbers(new_v_suffix):
                variations.add(new_v_suffix)
            
            new_suffix_v = suffix + v
            if not contains_consecutive_numbers(new_suffix_v):
                variations.add(new_suffix_v)
            
            if len(v) > 3: # Add some in the middle
                mid_point = len(v) // 2
                new_mid_v = v[:mid_point] + suffix + v[mid_point:]
                if not contains_consecutive_numbers(new_mid_v):
                    variations.add(new_mid_v)

    # Reverse
    for v in list(variations): # Iterate over a copy
        if len(v) > 3:
            reversed_v = v[::-1]
            if not contains_consecutive_numbers(reversed_v):
                variations.add(reversed_v)

    # Capitalize random letters
    def randomize_caps(w):
        return "".join(random.choice([char.lower(), char.upper()]) for char in w)

    for v in list(variations): # Iterate over a copy
        if len(v) > 3:
            random_caps_v = randomize_caps(v)
            if not contains_consecutive_numbers(random_caps_v):
                variations.add(random_caps_v)

    return list(variations)


def generate_wordlist():
    """Generates a wordlist of 25 complex passwords based on user inputs and saves it to a file."""
    # Access Entry widgets using the global 'entries' dictionary
    name = entries["entry_name"].get().strip()
    birthdate = entries["entry_birthdate"].get().strip()
    pet_name = entries["entry_pet_name"].get().strip()
    city = entries["entry_city"].get().strip()
    fav_word = entries["entry_fav_word"].get().strip()

    input_words = [item for item in [name, birthdate, pet_name, city, fav_word] if item]

    if not input_words:
        messagebox.showwarning("No Input", "Please enter some information to generate a wordlist.")
        return

    potential_passwords = set()

    # Generate variations for each individual input
    for word in input_words:
        potential_passwords.update(generate_complex_variations(word))

    # Combinations of inputs with separators
    separators = ["_", "-", ".", "!", "@", "$"]
    common_nums_syms = ["1!", "007", "2024", "!!", "#", "$"] # Moved here to be accessible

    for i in range(len(input_words)):
        for j in range(i + 1, len(input_words)):
            word1 = input_words[i]
            word2 = input_words[j]
            
            # Helper for applying leet, defined here to use within this scope
            def apply_leet_local(w):
                leet_map = {'a': '@', 's': '$', 'i': '!', 'o': '0', 'e': '3', 'l': '1', 't': '7', 'g': '9', 'b': '8'}
                new_word_list = []
                for char in w:
                    if char.lower() in leet_map:
                        new_word_list.append(leet_map[char.lower()])
                    else:
                        new_word_list.append(char)
                return "".join(new_word_list)

            for sep in separators:
                pwds_to_add = [
                    word1.lower() + sep + word2.lower(),
                    word1.capitalize() + sep + word2.capitalize(),
                    word1.lower() + sep + word2.capitalize(),
                    word1.capitalize() + sep + word2.lower(),
                    apply_leet_local(word1) + sep + apply_leet_local(word2),
                    word2.lower() + sep + word1.lower()
                ]
                for pwd in pwds_to_add:
                    if not contains_consecutive_numbers(pwd):
                        potential_passwords.add(pwd)

            # Add numbers and symbols around combinations
            for num_sym in common_nums_syms:
                pwds_to_add = [
                    word1.lower() + num_sym + word2.lower(),
                    num_sym + word1.lower() + word2.lower(),
                    word1.lower() + word2.lower() + num_sym
                ]
                for pwd in pwds_to_add:
                    if not contains_consecutive_numbers(pwd):
                        potential_passwords.add(pwd)


    # Filter for length and basic complexity (at least 8 chars, some variety)
    filtered_passwords = []
    for pwd in potential_passwords:
        if len(pwd) >= 8: # Minimum length for a strong password
            # Further checks for diversity (optional, but good for "complexity")
            has_upper = bool(RE_UPPER.search(pwd))
            has_lower = bool(RE_LOWER.search(pwd))
            has_digit = bool(RE_DIGITS.search(pwd))
            has_symbol = bool(RE_SYMBOLS.search(pwd))

            if (has_upper + has_lower + has_digit + has_symbol) >= 3: # At least 3 character types
                 filtered_passwords.append(pwd)


    passwords_with_scores = []
    for pwd in filtered_passwords:

        if not contains_consecutive_numbers(pwd):
            score, _, _, _ = check_strength(pwd)
            passwords_with_scores.append((score, len(pwd), pwd))


    passwords_with_scores.sort(key=lambda x: (x[0], x[1]), reverse=True)


    final_passwords = []
    seen_passwords = set()
    for _, _, pwd in passwords_with_scores:
        if pwd not in seen_passwords:
            final_passwords.append(pwd)
            seen_passwords.add(pwd)
            if len(final_passwords) >= 25:
                break
    

    while len(final_passwords) < 25:
        chars_for_random = string.ascii_letters + string.digits + string.punctuation

        length = random.randint(12, 18) 
        temp_random_pwd = ''.join(random.choice(chars_for_random) for _ in range(length))
        

        attempts = 0
        while contains_consecutive_numbers(temp_random_pwd) or temp_random_pwd in seen_passwords:
            temp_random_pwd = ''.join(random.choice(chars_for_random) for _ in range(length))
            attempts += 1
            if attempts > 100: 
                print("Warning: Difficult to generate a random password without consecutive numbers and unique.")
                break 
        
        if not contains_consecutive_numbers(temp_random_pwd) and temp_random_pwd not in seen_passwords:
            final_passwords.append(temp_random_pwd)
            seen_passwords.add(temp_random_pwd)


    if not final_passwords:
        messagebox.showwarning("Generation Failed", "Could not generate complex passwords with the provided inputs and restrictions. Please try more diverse inputs.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        title="Save Complex Wordlist As"
    )

    if file_path:
        try:
            with open(file_path, "w") as f:
                for word in final_passwords:
                    f.write(word + "\n")
            messagebox.showinfo("Success", f"Generated {len(final_passwords)} complex passwords and saved to:\n{file_path}")
            
            # Clear input fields after successful generation
            for entry_widget in entries.values():
                entry_widget.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save wordlist: {e}")


# GUI Setup
root = tk.Tk()
root.title("Password Security Suite")
root.geometry("480x750")
root.resizable(False, False)

style = ttk.Style()
style.configure("Check.TLabel", font=("Arial", 10))

# --- Password Strength Evaluator Section ---
strength_frame = ttk.LabelFrame(root, text="Password Strength Evaluator", padding="10 10 10 10")
strength_frame.pack(pady=10, padx=10, fill='x')

tk.Label(strength_frame, text="Enter Password:", font=("Arial", 11)).pack(pady=5)
entry = tk.Entry(strength_frame, width=35, show='*', font=("Arial", 11))
entry.pack()
entry.bind("<KeyRelease>", evaluate)

frame = tk.Frame(strength_frame)
frame.pack(pady=5)
toggle_btn = tk.Button(frame, text="Show", command=toggle_password, width=10)
toggle_btn.pack(side='left', padx=5)
copy_btn = tk.Button(frame, text="Copy", command=copy_password, width=10)
copy_btn.pack(side='left')

tk.Button(strength_frame, text="Check Strength", command=evaluate).pack(pady=5)

progress = ttk.Progressbar(strength_frame, length=300, maximum=100)
progress.pack(pady=5)

result = tk.StringVar()
strength_label = tk.Label(strength_frame, textvariable=result, font=("Arial", 12, "bold"))
strength_label.pack()

details = tk.StringVar()
tk.Label(strength_frame, textvariable=details, wraplength=400, fg="gray", justify='left').pack(pady=(5,0))

checklist_frame = tk.Frame(strength_frame)
checklist_frame.pack(pady=5, anchor='w', padx=20)

checklist_vars = [tk.StringVar() for _ in range(5)]
checklist_labels = []
for i in range(5):
    label = tk.Label(checklist_frame, textvariable=checklist_vars[i], font=("Arial", 10), anchor='w')
    label.pack(fill='x')
    checklist_labels.append(label)

# --- Wordlist Generator Section ---
wordlist_frame = ttk.LabelFrame(root, text="Custom Wordlist Generator", padding="10 10 10 10")
wordlist_frame.pack(pady=10, padx=10, fill='x')


entries = {}

# Input fields for wordlist generator
input_fields = [
    ("Name:", "entry_name"),
    ("Birthdate (YYYYMMDD):", "entry_birthdate"),
    ("Pet's Name:", "entry_pet_name"),
    ("City:", "entry_city"),
    ("Favorite Word:", "entry_fav_word")
]

for label_text, var_name in input_fields:
    row_frame = tk.Frame(wordlist_frame)
    row_frame.pack(fill='x', pady=2)
    tk.Label(row_frame, text=label_text, width=18, anchor='w').pack(side='left')
    entry_widget = tk.Entry(row_frame, width=30)
    entry_widget.pack(side='right', expand=True, fill='x')
    entries[var_name] = entry_widget 

tk.Button(wordlist_frame, text="Generate Wordlist", command=generate_wordlist).pack(pady=10)

root.mainloop()