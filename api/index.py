from flask import Flask, request, jsonify
from flask_cors import CORS
import os, random, re

app = Flask(__name__)
CORS(app)

BASE_DIR = "text-files"  # Change this to your actual directory
selected_file = None

def censor_filename(text, filename):
    filename_base = os.path.splitext(filename)[0]
    censored_text = re.sub(re.escape(filename_base), 'X' * len(filename_base), text, flags=re.IGNORECASE)
    return censored_text

@app.route("/random-file")
def random_file():
    global selected_file

    subdir = random.choice([chr(i) for i in range(65, 91)])
    path = os.path.join(BASE_DIR, subdir)

    if not os.path.exists(path):
        return "No such directory.", 404

    files = [f for f in os.listdir(path) if f.endswith(".txt")]
    if not files:
        return "No text files found.", 404

    selected_file = random.choice(files)
    file_path = os.path.join(path, selected_file)

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    censored_content = censor_filename(content, selected_file)
    return jsonify({"content": censored_content})

@app.route("/guess", methods=["POST"])
def guess_filename():
    global selected_file
    if not selected_file:
        return jsonify({"message": "No file has been selected yet."}), 400

    data = request.json
    user_guess = data.get("guess", "").strip().lower()
    actual_filename = os.path.splitext(selected_file)[0].lower()

    if user_guess == actual_filename:
        return jsonify({"message": "Correct! You guessed the filename."})
    else:
        return jsonify({"message": "Incorrect. Try again!"})

# Vercel requires this for serverless functions
def handler(event, context):
    return app(event, context)
