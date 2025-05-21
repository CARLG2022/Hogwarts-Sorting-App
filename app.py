from flask import Flask, request, render_template
import json
import sqlite3

app = Flask(__name__)

# ---------- Initialize Database ----------
def init_db():
    conn = sqlite3.connect('hogwarts.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sorted_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    answers TEXT NOT NULL,
                    house TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

init_db()

# ---------- Routes ----------

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/quiz", methods=["GET"])
def quiz():
    username = request.args.get("username", "Wizard")
    return render_template("new_quiz.html", username=username)

@app.route("/submit", methods=["POST"])
def submit():
    answers_raw = request.form.get('answers')
    username = request.form.get('username', 'Anonymous')

    # Parse answers JSON
    answers = json.loads(answers_raw) if answers_raw else []

    # Scoring algorithm
    house_scores = {"Gryffindor": 0, "Hufflepuff": 0, "Ravenclaw": 0, "Slytherin": 0}
    for answer in answers:
        if answer in house_scores:
            house_scores[answer] += 1

    # Determine top house
    sorted_house = max(house_scores, key=house_scores.get)

    # Save to database
    conn = sqlite3.connect('hogwarts.db')
    c = conn.cursor()
    c.execute("INSERT INTO sorted_users (username, answers, house) VALUES (?, ?, ?)",
              (username, json.dumps(answers), sorted_house))
    conn.commit()
    conn.close()

    return render_template("results.html", house=sorted_house, username=username)

@app.route("/sorted_users", methods=["GET"])
def sorted_users():
    conn = sqlite3.connect('hogwarts.db')
    c = conn.cursor()
    c.execute("SELECT username, house FROM sorted_users")
    rows = c.fetchall()
    conn.close()

    # Group users by house
    grouped = {"Gryffindor": [], "Hufflepuff": [], "Ravenclaw": [], "Slytherin": []}
    for username, house in rows:
        if house in grouped:
            grouped[house].append(username)

    return render_template("sorted_users.html", grouped=grouped)

if __name__ == "__main__":
    app.run(debug=True)
