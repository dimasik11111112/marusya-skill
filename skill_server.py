import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    user_text = data.get("request", {}).get("command", "")

    if not user_text:
        reply_text = "Я тебя не расслышала, повтори пожалуйста"
    else:
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": "Ты голосовой ассистент. Отвечай кратко, разговорным языком, без markdown."},
                    {"role": "user", "content": user_text}
                ],
                max_tokens=300
            )
            reply_text = response.choices[0].message.content
        except Exception as e:
            reply_text = "Извини, произошла ошибка"

    return jsonify({
        "version": data.get("version", "1.0"),
        "session": data.get("session", {}),
        "response": {
            "text": reply_text,
            "end_session": False
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)