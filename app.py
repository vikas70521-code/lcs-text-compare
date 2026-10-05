"""
app.py - Flask web front end for the Text Comparison System.

Run:   python app.py        then open http://127.0.0.1:5000
"""
from flask import Flask, jsonify, render_template, request

from lcs import compare

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024      # reject requests > 2 MB

MAX_TOKENS = 6000          # per document; keeps the O(m*n) work responsive


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/compare", methods=["POST"])
def api_compare():
    data = request.get_json(silent=True) or {}
    text_a = str(data.get("text_a", ""))
    text_b = str(data.get("text_b", ""))
    mode = data.get("mode", "word")
    algorithm = data.get("algorithm", "auto")

    if mode not in ("word", "line", "char"):
        return jsonify(error="Mode must be word, line or char."), 400
    if algorithm not in ("auto", "dp", "hirschberg"):
        return jsonify(error="Unknown algorithm."), 400
    if not text_a.strip() and not text_b.strip():
        return jsonify(error="Paste or upload text in at least one document."), 400

    # Guard against huge inputs (character mode creates one token per letter).
    longest = max(len(text_a), len(text_b)) if mode == "char" else max(
        len(text_a.split()) if mode == "word" else len(text_a.splitlines()),
        len(text_b.split()) if mode == "word" else len(text_b.splitlines()))
    if longest > MAX_TOKENS:
        return jsonify(error=f"Documents are too long for {mode} mode "
                             f"(limit {MAX_TOKENS} {mode}s each). Try line mode."), 413

    result = compare(text_a, text_b, mode=mode,
                     ignore_case=bool(data.get("ignore_case", True)),
                     ignore_punct=bool(data.get("ignore_punct", True)),
                     algorithm=algorithm)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
