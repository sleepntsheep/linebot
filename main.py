from os import getenv
from flask import Flask, request, abort
import base64
import hashlib
import hmac

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

line_bot_api = LineBotApi(getenv('CHANNEL_TOKEN'))
handler = WebhookHandler(getenv('CHANNEL_SECRET'))

@app.route('/callback', methos=('POST',))
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info(f'Request body: {body}')
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print('Invalid signature, check your channel access token')
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))

if __name__ == '__main__':
    app.run(int(getenv('PORT')))
