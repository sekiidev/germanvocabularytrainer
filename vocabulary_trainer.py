import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import random
from datetime import datetime

# ------------------------------
# Dateien
# ------------------------------
USERS_FILE = "users.json"
VOC_FILE = "vokabeln.json"
LOG_FILE = "admin_log.json"
ADMIN_SECRET = "ADMIN123"


# ------------------------------
# Hilfsfunktionen User
# ------------------------------
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


# ------------------------------
# Logging für Admins
# ------------------------------
def log_action(user, action):
    log_entry = {
        "user": user,
        "action": action,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
    logs.append(log_entry)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)


# ------------------------------
# Vokabeltrainer
# ------------------------------
class VocabularyTrainer:
    def __init__(self, filename=VOC_FILE, current_user="", is_admin=False):
        self.words = {}
        self.filename = filename
        self.current_user = current_user
        self.is_admin = is_admin
        self.load_words()

    def add_word(self, word, meaning):
        self.words[word] = meaning
        self.save_words()
        if self.is_admin:
            log_action(self.current_user, f"Vokabel hinzugefügt: {word} -> {meaning}")

    def save_words(self):
        with open(self.filename, 'w', encoding="utf-8") as f:
            json.dump(self.words, f, indent=4, ensure_ascii=False)

    def load_words(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding="utf-8") as f:
                try:
                    self.words = json.load(f)
                except json.JSONDecodeError:
                    self.words = {}

    def start_test(self, overlay):
        if not self.words:
            overlay.update_text("Keine Vokabeln vorhanden.")
            return
        score = 0
        for word, meaning in self.words.items():
            user_answer = simpledialog.askstring("Test", f"Was bedeutet '{word}'?")
            if user_answer and user_answer.strip().lower() == meaning.strip().lower():
                score += 1
        overlay.update_text(f"Dein Ergebnis: {score}/{len(self.words)}")
        if self.is_admin:
            log_action(self.current_user, "Test durchgeführt")

    def word_scramble(self, overlay):
        if not self.words:
            overlay.update_text("Keine Vokabeln zum Spielen vorhanden.")
            return
        word = random.choice(list(self.words.keys()))
        scrambled = ''.join(random.sample(word, len(word)))
        guess = simpledialog.askstring("Buchstabensalat", f"Entwirre das Wort: {scrambled}")
        if guess and guess.lower() == word.lower():
            overlay.update_text("Richtig!")
        else:
            overlay.update_text(f"Falsch! Das Wort war: {word}")
        if self.is_admin:
            log_action(self.current_user, f"Buchstabensalat gespielt (Wort: {word})")


# ------------------------------
# GUI Overlay
# ------------------------------
class Overlay:
    def __init__(self, root, trainer):
        self.root = root
        self.trainer = trainer

        self.root.title("Vokabeltrainer")
        self.root.geometry("400x450")
        self.root.configure(bg="black")

        self.label = tk.Label(root, text=f"Willkommen, {self.trainer.current_user}!",
                              fg="white", bg="black", font=("Arial", 14))
        self.label.pack(pady=10)

        # Eingabefelder
        self.word_entry = tk.Entry(root, font=("Arial", 12),
                                   fg="white", bg="#222222", insertbackground="white")
        self.word_entry.insert(0, "Vokabel eingeben")
        self.word_entry.pack(pady=5)

        self.meaning_entry = tk.Entry(root, font=("Arial", 12),
                                      fg="white", bg="#222222", insertbackground="white")
        self.meaning_entry.insert(0, "Bedeutung eingeben")
        self.meaning_entry.pack(pady=5)

        tk.Button(root, text="Vokabel hinzufügen", command=self.add_word,
                  bg="#333333", fg="white").pack(pady=5)

        tk.Button(root, text="Test starten", command=self.start_test,
                  bg="#333333", fg="white").pack(pady=5)
        tk.Button(root, text="Buchstabensalat spielen", command=self.word_scramble,
                  bg="#333333", fg="white").pack(pady=5)

        self.result_label = tk.Label(root, text="", fg="white", bg="black", font=("Arial", 12))
        self.result_label.pack(pady=10)

    def add_word(self):
        word = self.word_entry.get().strip()
        meaning = self.meaning_entry.get().strip()
        if word and meaning:
            self.trainer.add_word(word, meaning)
            self.update_text(f"'{word}' gespeichert!")
            self.word_entry.delete(0, tk.END)
            self.meaning_entry.delete(0, tk.END)

    def start_test(self):
        self.trainer.start_test(self)

    def word_scramble(self):
        self.trainer.word_scramble(self)

    def update_text(self, text):
        self.result_label.config(text=text)


# ------------------------------
# Login Fenster
# ------------------------------
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("380x280")
        self.root.configure(bg="black")

        tk.Label(root, text="Vokabeltrainer Login", fg="white", bg="black", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Label(root, text="E-Mail:", fg="white", bg="black", font=("Arial", 12)).pack()
        self.email_entry = tk.Entry(root, font=("Arial", 12), fg="white", bg="#222222", insertbackground="white")
        self.email_entry.pack(pady=2)

        tk.Label(root, text="Passwort:", fg="white", bg="black", font=("Arial", 12)).pack()
        self.password_entry = tk.Entry(root, font=("Arial", 12), fg="white", bg="#222222",
                                       insertbackground="white", show="*")
        self.password_entry.pack(pady=2)

        tk.Button(root, text="Login", command=self.login, bg="#333333", fg="white").pack(pady=5)
        tk.Button(root, text="Registrieren", command=self.register, bg="#444444", fg="white").pack(pady=5)
        tk.Button(root, text="Admin-Login", command=self.admin_login, bg="#555555", fg="white").pack(pady=5)

    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        users = load_users()
        if email in users and users[email] == password:
            self.root.destroy()
            main_window(current_user=email, is_admin=False)
        else:
            messagebox.showerror("Fehler", "E-Mail oder Passwort falsch.")

    def register(self):
        email = simpledialog.askstring("Registrierung", "E-Mail eingeben:")
        if not email:
            return
        password = simpledialog.askstring("Registrierung", "Passwort eingeben:", show="*")
        if not password:
            return
        users = load_users()
        if email in users:
            messagebox.showerror("Fehler", "Benutzer existiert bereits.")
            return
        users[email] = password
        save_users(users)
        messagebox.showinfo("OK", "Registrierung erfolgreich.")

    def admin_login(self):
        code = simpledialog.askstring("Admin", "Admin-Schlüsselwort eingeben:")
        if code == ADMIN_SECRET:
            email = "ADMIN"
            self.root.destroy()
            main_window(current_user=email, is_admin=True)
        else:
            messagebox.showerror("Fehler", "Falscher Admin-Code.")


# ------------------------------
# Start Hauptfenster
# ------------------------------
def main_window(current_user="", is_admin=False):
    root = tk.Tk()
    trainer = VocabularyTrainer(current_user=current_user, is_admin=is_admin)
    Overlay(root, trainer)
    root.mainloop()


# ------------------------------
# Startprogramm
# ------------------------------
if __name__ == "__main__":
    login_root = tk.Tk()
    LoginWindow(login_root)
    login_root.mainloop()
