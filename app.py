from flask import Flask, render_template, request, jsonify
import os
import requests

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "nuwa-ai-tool-2026")

# DeepSeek API配置
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
API_MODEL = "deepseek-chat"


def call_deepseek(messages, temperature=0.7, max_tokens=2000):
    """调用DeepSeek API"""
    if not DEEPSEEK_API_KEY:
        return "API Key未配置，请在环境变量中设置 DEEPSEEK_API_KEY"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": API_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    try:
        resp = requests.post(
            f"{DEEPSEEK_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"【调用失败】{str(e)}"


# ========== 页面路由 ==========

@app.route("/")
def index():
    """首页 — 卡片式品牌页 + 功能入口"""
    return render_template("index.html")


# ========== API：文案生成 ==========

@app.route("/api/copywriting/generate", methods=["POST"])
def copywriting_generate():
    body = request.get_json()
    product_name = body.get("product_name", "")
    scene = body.get("scene", "morning")

    scene_names = {"morning": "早安问候+产品推荐", "lunch": "午间促销", "evening": "晚间温馨推荐"}
    scene_prompt = scene_names.get(scene, "早安问候")

    system_prompt = f"""你是一家实体轻食店的运营学姐。请为今天的{scene_prompt}写一条朋友圈文案。

要求：
- 亲切自然的口吻，像学姐跟学弟学妹说话
- 突出产品"{product_name}"的卖点
- 控制在80字以内
- 符合健康轻食的调性
- 不要网络梗，不要长辈式说教
- 直接输出文案内容，不要加标题和说明"""

    text = call_deepseek([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"今天店里主推【{product_name}】，帮我写一条{scene_prompt}的文案。"}
    ], temperature=0.8, max_tokens=500)

    return jsonify({"ok": True, "text": text})


# ========== API：海报Slogan生成 ==========

@app.route("/api/poster/slogan", methods=["POST"])
def poster_slogan():
    """AI生成海报slogan"""
    body = request.get_json()
    product_name = body.get("product_name", "")
    price = body.get("price", "")

    prompt = f"""为轻食产品【{product_name}】、价格【{price}元】写一句促销slogan。
要求：简短有力，10个字以内，突出健康好吃不易胖。
直接输出slogan，不要加引号和其他内容。"""

    slogan = call_deepseek([
        {"role": "system", "content": "你是一个轻食品牌的文案策划。"},
        {"role": "user", "content": prompt}
    ], temperature=0.8, max_tokens=100)

    slogan = slogan.strip().strip('"').strip("'").strip("「").strip("」")
    return jsonify({"ok": True, "slogan": slogan})


# ========== API：智能问答 ==========

@app.route("/api/qa/ask", methods=["POST"])
def qa_ask():
    body = request.get_json()
    question = body.get("question", "")
    qa_data = body.get("qa_data", [])

    # 精确匹配
    for item in qa_data:
        if item.get("q", "").strip() == question.strip():
            return jsonify({"ok": True, "answer": item["a"]})

    # AI回答
    import json
    system_prompt = f"""你是这家店的AI客服助手。请用亲切自然的语气回答顾客的问题。

店铺信息参考：
{json.dumps(qa_data, ensure_ascii=False, indent=2)}

请根据以上知识库回答。如果问题在知识库里找不到准确答案，就根据已有信息合理回答，不要编造。
回复要简短亲切，50字以内。"""

    answer = call_deepseek([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ], temperature=0.3, max_tokens=300)

    return jsonify({"ok": True, "answer": answer})


# ========== 启动 ==========

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 女娲智媒 · 实体店AI运营工具包 started on port {port}")
    app.run(host="0.0.0.0", port=port)
