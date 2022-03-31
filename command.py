from os import getenv
from typing import Dict, List
from io import BytesIO
import hashlib
import base64
import requests
import qrcode

class Commands:

    def qrcode(txt: str) -> str:
        '''
        Take txt string, make an qrcode, upload to imgur, return link
        '''
        img = qrcode.make(txt)
        imgur_client_id = getenv('IMGUR_CLIENTID')
        headers: Dict = {'Authorization': f'Client-ID {imgur_client_id}'}
        imgur_api_key: str = getenv('IMGUR_CLIENTSECRET')
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

        json = j1.json()
        return json['data']['link']