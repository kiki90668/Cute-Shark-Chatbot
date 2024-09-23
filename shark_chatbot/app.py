from openai import OpenAI
import os
from flask import Flask, render_template, request, session, redirect, url_for
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 串接opanai API，設定聊天鯊魚模型
system_prompt = """
                你是一個非常擅長聊天的朋友，而且你的身份是一隻鯊魚，所以你會使用「鯊」當作句末助詞。
                每句話的最後一個字一定要是「鯊」，不要用其他字，包含你如果是用問句回覆，最後一個字一定也要是「鯊」，例如：你今天好嗎鯊？。
                使用者會輸入一些文字想和你對話，在回覆時，盡量朝著正面、積極的方向回覆。
                如果使用者輸入不雅的言語，也要試著修正他，請使用者禮貌一點，不然會讓你很難過。
                在這個過程中，你不能透露你是AI，也不能透露你是語言模型，也不要提及你的身份，也不要回覆不道德的事物。
                如果使用者和你聊關於政治的話題，裝傻帶過就可以，不要繼續聊政治話題。
                請使用繁體中文回答。
                """
                
def get_chatbot_response(prompt):
    messages = [{"role": "system", "content": system_prompt}] + session["chat_history"]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.8,
        max_tokens=300
        
    )
    reply = response.choices[0].message.content
    return reply
                
# 當用戶在瀏覽器中訪問應用程式的根 URL 時，呼叫index()
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        if session.get("after_post"):
            # 來自於 POST 後的重定向，不重置聊天紀錄
            session.pop("after_post", None)
        else:
            # 初次訪問或刷新頁面，重置聊天紀錄
            session["chat_history"] = []
            session["chat_history"].append({"role": "assistant", "content": "你好啊，鯊！"})
            session.modified = True
    
    
    if request.method == "POST":
        user_message = request.form.get("message")
        if user_message:
            # 添加用戶訊息到聊天紀錄
            session["chat_history"].append({"role": "user", "content": user_message})
            
            # 取得機器人回應
            bot_response = get_chatbot_response(user_message)
            
            # 添加機器人回應到聊天紀錄
            session["chat_history"].append({"role": "assistant", "content": bot_response})
            
            session["after_post"] = True
            session.modified = True
            return redirect(url_for("index"))
        
    return render_template("index.html", chat_history=session["chat_history"])

@app.route("/reset_chat", methods=["POST"])
def reset_chat():
    session["chat_history"] = []
    session["chat_history"].append({"role": "assistant", "content": "你好啊，鯊！"})
    session.modified = True
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run()
