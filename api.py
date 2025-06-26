from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health_check():
    return "Bot API kjører OK!", 200

@app.route("/api/messages", methods=["POST"])
def messages():
    body = request.get_json()
    user_message = body.get("text", "") or body.get("value", "")

    if not user_message:
        return jsonify({"error": "Ingen melding mottatt"}), 400

    reply = f"Echo: {user_message}"
    return jsonify({
        "type": "message",
        "text": reply
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
