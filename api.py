from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "✅ API kjører!"

@app.route("/ping")
def ping():
    return jsonify({"status": "OK"})

# Eksempel på rute som bruker pandas
@app.route("/data", methods=["POST"])
def process_data():
    try:
        data = request.json.get("rows", [])
        df = pd.DataFrame(data)
        return jsonify({
            "rows_received": len(df),
            "columns": df.columns.tolist()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400
