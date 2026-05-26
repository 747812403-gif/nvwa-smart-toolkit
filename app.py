import os, json, requests
from flask import Flask, request, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "nuwa-ai-tool-2026")
KEY = os.environ.get("DEEPSEEK_API_KEY", "")

@app.route("/")
def home():
    return open("index.html", encoding="utf-8").read()

def ds(messages, temp=0.7, maxT=2000):
    if not KEY:
        return "DeepSeek API Key 未配置"
    try:
        r = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat", "messages": messages, "temperature": temp, "max_tokens": maxT},
            timeout=30
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"调用失败: {str(e)[:100]}"

@app.route("/api/copywriting/generate", methods=["POST"])
def cw():
    try:
        b = request.get_json()
        t = ds([
            {"role": "system", "content": f"轻食店学姐写{b.get('scene','morning')}朋友圈文案，80字内亲切自然，突出{b.get('product_name','')}"},
            {"role": "user", "content": f"帮写{b.get('product_name','')}文案"}
        ], 0.8, 500)
        return jsonify({"ok": True, "text": t})
    except Exception as e:
        return jsonify({"ok": False, "text": f"出错: {str(e)[:100]}"})

@app.route("/api/poster/slogan", methods=["POST"])
def ps():
    try:
        b = request.get_json()
        s = ds([
            {"role": "system", "content": "轻食品牌文案，输出一句10字内促销标语，直接输出不要解释"},
            {"role": "user", "content": f"为{b.get('product_name','')}写标语"}
        ], 0.8, 100)
        s = s.strip()
        for c in "\"'「」""''":
            s = s.strip(c)
        return jsonify({"ok": True, "slogan": s or "今日推荐"})
    except Exception as e:
        return jsonify({"ok": False, "slogan": "今日推荐"})

@app.route("/api/qa/ask", methods=["POST"])
def qa():
    try:
        b = request.get_json()
        q = b.get("question", "")
        qa_data = b.get("qa_data", [])
        for i in qa_data:
            if i.get("q", "").strip() == q.strip():
                return jsonify({"ok": True, "answer": i["a"]})
        a = ds([
            {"role": "system", "content": f"轻食店客服。信息：{json.dumps(qa_data, ensure_ascii=False)}"},
            {"role": "user", "content": q}
        ], 0.3, 300)
        return jsonify({"ok": True, "answer": a})
    except Exception as e:
        return jsonify({"ok": False, "answer": f"出错: {str(e)[:60]}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
