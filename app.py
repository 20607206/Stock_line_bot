from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from stock_parser import line_text
from stock_job import StockJobManager
import json

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
    response_text = line_text(User_message)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response_text))


if __name__ == "__main__":
    with open("stock_bidirectional_map.json", "r", encoding="utf-8") as stock:
        maps = json.load(stock)
        stock_list = maps['user_subscribe']
    app.run()
    manager = StockJobManager(stock_list)
    manager.start_schedule()


