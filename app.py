from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import get_price
#from dotenv import load_dotenv

#load_dotenv()

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("LINE_CHANNEL_SECRET"))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    User_message = event.message.text
    User_Id = event.source.user_id
    print(f"user_id: {User_Id}, 使用者輸入: {User_message}")
    response_text = get_price.get_twstock_price(User_message)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response_text))


if __name__ == "__main__":
    app.run()