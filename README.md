# Task 6 – Password Strength Evaluation

## 🎯 Objective
To understand and evaluate password strength using a custom-built Python GUI tool inspired by PasswordMeter.com.

## 🛠 Tool Used
- Python GUI Password Strength Checker (built using `tkinter` and `re`)
- Mimics PasswordMeter’s scoring logic with positive and negative weights

## 🔐 Passwords Tested

| Password           | Strength (%) | Feedback                         | Suggestions                               |
|--------------------|--------------|----------------------------------|-------------------------------------------|
| akshat             | 16%          | Weak – Needs improvement         | Contains only letters, Repeated characters|
| 12345              | 41%          | Weak – Needs improvement         | Contains only numbers                     |
| #########          | 74%          | Strong – Good password           | Repeated characters                        |
| Akshat20           | 70%          | Strong – Good password           | Well-balanced password!                   |
| Akshat@@2025@      | 100%         | Excellent – Secure password      | Repeated characters                        |

## 📸 Screenshots
Screenshots of all tested passwords are stored in the `result/` folder.

## 📚 Learnings
- Passwords must be long (12+ characters) and include all character types.
- Middle characters and symbols boost strength.
- Avoid repeated characters and dictionary words.

## 🛡️ Common Attacks
- **Brute Force Attack**: Tries all combinations.
- **Dictionary Attack**: Uses common words.
- **Hybrid Attack**: Mix of both techniques.

## ✅ Best Practices
- Use mixed characters (A-Z, a-z, 0-9, symbols).
- Avoid real words, names, or repeated patterns.
- Prefer passphrases or use a password manager.

## 📁 Folder Structure

```
Password-Strength-Task6/
│
├── README.md
├── strength.py
├── result/
│   ├── result 1.png
│   ├── result 2.png
│   ├── result 3.png
│   ├── result 4.png
│   └── result 5.png
│   └── GUI.png
```
