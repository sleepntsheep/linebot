import random
import sys
import math
import base64
import hashlib
import hmac
from io import StringIO, BytesIO
from typing import List
from os import getenv

import requests
import qrcode
from flask import Flask, request, abort

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
        match command:
            case 'e':
                old_stdout = sys.stdout
                sys.stdout = mystdout = StringIO()
                evalres: str = eval(' '.join(params))

                sys.stdout = old_stdout
                replytext = f'Stdout: {mystdout.getvalue()}\nReturn: {evalres}'
            case 'q':
                img = qrcode.make(' '.join(params))
                imgur_client_id = getenv('IMGUR_CLIENTID')
                headers = {'Authorization': f'Client-ID ' {imgur_client_id}}
                imgur_api_key = getenv('IMGUR_CLIENTSECRET')
                url = 'https://api.imgur.com/3/upload.json'
                buffer = BytesIO()
                img.save(buffer)
                md = hashlib.md5()
                md.update(buffer.getvalue())
                encoded_img = base64.b64encode(buffer.getvalue())
                
                j1 = requests.post(
                    url,
                    headers = headers,
                    data = {
                        'key': imgur_api_key,
                        'image': encoded_img,
                        'type': 'base64',
                        'name': md,
                        'title': md
                    }
                )
                

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=replytext))
    except Exception as error:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=repr(error)))

if __name__ == '__main__':
    app.run(int(getenv('PORT')))
