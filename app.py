import os, json, requests
from flask import Flask, request, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "nuwa-ai-tool-2026")
KEY = "sk-3be3d1c4d1a244e3ad8526b12167b663"

def call_ds(messages, temp=0.7, maxT=2000):
    if not KEY: return "DeepSeek API Key 未配置"
    try:
        r = requests.post("https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat", "messages": messages, "temperature": temp, "max_tokens": maxT}, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"调用失败: {str(e)[:100]}"

@app.route("/")
def index():
    return open("index.html", encoding="utf-8").read()

@app.route("/api/copywriting/generate", methods=["POST"])
def generate_copywriting():
    try:
        b=request.get_json()
        t=call_ds([{"role":"system","content":f"轻食店学姐写{b.get('scene','morning')}朋友圈文案，80字内亲切，突出{b.get('product_name','')}"},{"role":"user","content":f"帮写{b.get('product_name','')}文案"}],0.8,500)
        return jsonify({"ok":True,"text":t})
    except Exception as e: return jsonify({"ok":False,"text":f"出错:{str(e)[:80]}"})

@app.route("/api/poster/slogan", methods=["POST"])
def generate_slogan():
    try:
        b=request.get_json()
        s=call_ds([{"role":"system","content":"轻食品牌文案输出10字内标语直接输出"},{"role":"user","content":f"为{b.get('product_name','')}写标语"}],0.8,100)
        s=s.strip().strip("\"'「」""''")
        return jsonify({"ok":True,"slogan":s or "今日推荐"})
    except: return jsonify({"ok":False,"slogan":"今日推荐"})

@app.route("/api/qa/ask", methods=["POST"])
def answer_question():
    try:
        b=request.get_json();q=b.get("question","");qa=b.get("qa_data",[])
        for i in qa:
            if i.get("q","").strip()==q.strip(): return jsonify({"ok":True,"answer":i["a"]})
        a=call_ds([{"role":"system","content":f"轻食店客服信息:{json.dumps(qa,ensure_ascii=False)}"},{"role":"user","content":q}],0.3,300)
        return jsonify({"ok":True,"answer":a})
    except: return jsonify({"ok":False,"answer":f"出错"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
