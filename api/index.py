from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import random
import re

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.join(os.getcwd(), "text-files")  # Correct path to the text-files directory
selected_file = None

def censor_filename(text, filename):
    filename_base = os.path.splitext(filename)[0]
    censored_text = re.sub(re.escape(filename_base), 'X' * len(filename_base), text, flags=re.IGNORECASE)
    return censored_text

@app.route("/random-file")
def random_file():
    global selected_file

    all_files = []
    for subdir in os.listdir(BASE_DIR):
        path = os.path.join(BASE_DIR, subdir)
        if os.path.isdir(path):  # Ensure it's a directory
            txt_files = [f for f in os.listdir(path) if f.endswith(".txt")]
            for file in txt_files:
                all_files.append((subdir, file))  # Store both subdir and filename

    if not all_files:
        return "No text files found.", 404

    selected_subdir, selected_file = random.choice(all_files)
    file_path = os.path.join(BASE_DIR, selected_subdir, selected_file)

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    censored_content = censor_filename(content, selected_file)
    return jsonify({"censored": censored_content, "uncensored": content})

@app.route("/guess", methods=["POST"])
def guess_filename():
    global selected_file
    if not selected_file:
        return jsonify({"message": "No file has been selected yet."}), 400

    data = request.json
    user_guess = data.get("guess", "").strip().lower()
    actual_filename = os.path.splitext(selected_file)[0].lower()

    if user_guess == actual_filename:
        return jsonify({"message": "Correct! You guessed the soil name."})
    else:
        return jsonify({"message": "Incorrect. Try again!"})

# For Vercel, Flask should be wrapped with a function to work as a serverless function.
# Vercel Python runtime should automatically detect it
if __name__ == "__main__":
    app.run()

