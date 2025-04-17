from flask import Flask, render_template, request, redirect, session, send_file
import pyrebase
import random
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)
app.secret_key = "supersecret"

# Firebase config
firebaseConfig = {
  "apiKey": "AIzaSyCkWIrzktG1M6WueFabz6UqdX68GK52jKk",
  "authDomain": "awesome-dzetagram.firebaseapp.com",
  "databaseURL": "https://awesome-dzetagram-default-rtdb.europe-west1.firebasedatabase.app",
  "projectId": "awesome-dzetagram",
  "storageBucket": "awesome-dzetagram.appspot.com",
  "messagingSenderId": "646335445264",
  "appId": "1:646335445264:web:29dfde4e518f7e652acd95",
  "measurementId": "G-RZHSJTXXGV"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

# Убедись, что папка cards/ существует
os.makedirs("cards", exist_ok=True)

def generate_card_number():
    return " ".join(["".join([str(random.randint(0, 9)) for _ in range(4)]) for _ in range(4)])

def generate_card_image(card_number, name="USER NAME"):
    template = Image.open("static/card_template.png").convert("RGBA")
    draw = ImageDraw.Draw(template)
    font = ImageFont.truetype("fonts/Arial.ttf", 36)

    draw.text((60, 120), card_number, font=font, fill="white")
    draw.text((60, 180), name, font=font, fill="white")

    path = f"cards/{card_number.replace(' ', '')}.png"
    template.save(path)
    return path

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            user = auth.create_user_with_email_and_password(email, password)
            session["user"] = user["localId"]
            session["email"] = email
            return redirect("/dashboard")
        except:
            return "Ошибка регистрации или аккаунт уже существует."

    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return f'''
        Добро пожаловать, {session["email"]}!<br>
        <a href="/create_card">Создать карту</a><br>
        <a href="/logout">Выйти</a>
    '''

@app.route("/create_card")
def create_card():
    if "user" not in session:
        return redirect("/")

    card_number = generate_card_number()
    card_image_path = generate_card_image(card_number, session["email"])

    card_data = {
        "owner": session["email"],
        "card_number": card_number,
        "balance": 0,
        "card_image": card_image_path
    }

    db.child("users").child(session["user"]).child("card").set(card_data)

    return send_file(card_image_path, mimetype='image/png')

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
