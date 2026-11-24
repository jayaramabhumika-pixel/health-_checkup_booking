
from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import date

app = Flask(__name__)

# Create database
def create_database():
    conn = sqlite3.connect("health.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        phone TEXT NOT NULL,
        hospital TEXT NOT NULL,
        checkup TEXT NOT NULL,
        appointment_date TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Book appointment
@app.route("/book", methods=["POST"])
def book():
    data = request.get_json()

    required = ["name", "age", "phone",
                "hospital", "checkup", "date"]

    if not data or any(not str(data.get(k, "")).strip() for k in required):
        return jsonify({"message": "Please fill all details."}), 400

    try:
        age = int(data["age"])
    except (ValueError, TypeError):
        return jsonify({"message": "Invalid age."}), 400

    if not 1 <= age <= 120:
        return jsonify({"message": "Enter a valid age."}), 400

    phone = str(data["phone"])

    if not phone.isdigit() or len(phone) != 10:
        return jsonify({"message": "Enter a valid phone number."}), 400

    try:
        appointment_date = date.fromisoformat(data["date"])
    except ValueError:
        return jsonify({"message": "Invalid date."}), 400

    if appointment_date < date.today():
        return jsonify({"message": "Select a future date."}), 400

    conn = sqlite3.connect("health.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO appointments
    (name, age, phone, hospital, checkup, appointment_date)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data["name"],
        age,
        phone,
        data["hospital"],
        data["checkup"],
        data["date"]
    ))

    conn.commit()
    booking_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "message": "Appointment booked successfully! Booking ID: "
                   + str(booking_id)
    })


if __name__ == "__main__":
    create_database()
    app.run(debug=True)
