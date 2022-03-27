import random
import sys
from io import StringIO
from typing import List
from os import getenv
from flask import Flask, request, abort
import math
import base64
import hashlib
import hmac

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

line_bot_api = LineBotApi(getenv('CHANNEL_TOKEN'))
handler = WebhookHandler(getenv('CHANNEL_SECRET'))

@app.route('/callback', methods=('POST',))
def callback():
    signature = request.headers['X-Line-Signature']
    body: str = request.get_data(as_text=True)
    app.logger.info(f'Request body: {body}')
    print(body)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print('Invalid signature, check your channel access token')
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        replytext: str = 'default'
        command: str = event.message.text.split()[0]
        params: List[str] = event.message.text.split()[1:]
        if (command == 'e'):
            old_stdout = sys.stdout
            sys.stdout = mystdout = StringIO()
            replytext: str = eval(' '.join(params))
            sys.stdout = old_stdout
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f'Stdout: {mystdout.getvalue()}\nReturn: {replytext}'))
    except Exception as error:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=repr(error)))

if __name__ == '__main__':
    app.run(int(getenv('PORT')))
