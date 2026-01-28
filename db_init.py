# db_init.py
import sqlite3

conn = sqlite3.connect("questions.db")
c = conn.cursor()

# questions: id, topic, question, a,b,c,d, correct (a/b/c/d), explanation
c.execute("""
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT,
    question TEXT,
    a TEXT,
    b TEXT,
    c TEXT,
    d TEXT,
    correct TEXT,
    explanation TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS user_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    question_id INTEGER,
    chosen TEXT,
    correct INTEGER,
    ts DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Примеры вопросов (можешь добавить свои)
sample = [
    ("Grammar: Present Simple",
     "I ____ to school every day.",
     "go", "goes", "going", "gone", "a",
     "Правильный ответ: 'go' — I (я) + глагол без -s."),
    ("Grammar: Past Simple",
     "She ____ a book yesterday.",
     "reads", "read", "has read", "reading", "b",
     "Правильный ответ: 'read' (past) произносится как /red/."),
    ("Vocabulary: Food",
     "Choose the word meaning 'яблоко'.",
     "pear", "apple", "banana", "orange", "b",
     "Apple — яблоко."),
    ("Grammar: Articles",
     "I saw ____ elephant at the zoo.",
     "a", "the", "an", "Ø", "c",
     "Перед словом, начинающимся с гласного звука — 'an'."),
    ("Grammar: Passive",
     "The cake ____ by my mom yesterday.",
     "was baked", "baked", "is baked", "will be baked", "a",
     "Прошедшее простое пассив: was/were + V3."),
    ("Reading: Comprehension",
     "If it rains, we ____ at home.",
     "stay", "stayed", "will stay", "staying", "a",
     "If (present) -> result in present/future: 'stay' в условии общего значения."),
    ("Prepositions",
     "He is good ____ maths.",
     "in", "at", "on", "for", "b",
     "Устойчивое выражение 'good at'."),
    ("Vocabulary: Jobs",
     "Who fixes cars?",
     "teacher", "doctor", "mechanic", "driver", "c",
     "Mechanic — механик, ремонтирует машины.")
]

for item in sample:
    c.execute("INSERT INTO questions (topic,question,a,b,c,d,correct,explanation) VALUES (?,?,?,?,?,?,?,?)", item)

conn.commit()
conn.close()
print("DB created and sample questions added (questions.db)")
