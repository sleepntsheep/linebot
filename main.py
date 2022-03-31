import random
import sys
import math
import base64
import hashlib
import hmac
from io import StringIO, BytesIO
from typing import List, Dict
from os import getenv

from command import Commands

import requests
import qrcode
from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage

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
        command: str = event.message.text.split()[0]
        params: List[str] = event.message.text.split()[1:]
        match command:
            case 'e':
                replytext: str = 'default'
                old_stdout = sys.stdout
                sys.stdout = mystdout = StringIO()
                evalres: str = eval(' '.join(params))

                sys.stdout = old_stdout
                replytext = f'Stdout: {mystdout.getvalue()}\nReturn: {evalres}'
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=replytext))
            case 'q':
                link: str = Commands.qrcode(' '.join(params))
                line_bot_api.reply_message(event.reply_token, ImageSendMessage(
                    original_content_url = link,
                    preview_image_url = link
                ))
                
    except Exception as error:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=repr(error)))

if __name__ == '__main__':
    app.run(int(getenv('PORT')))
