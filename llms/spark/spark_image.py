import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
from urllib.parse import urlparse
import ssl
from datetime import datetime
from time import mktime, time
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
from websockets.sync.client import connect
from websockets.exceptions import ConnectionClosed
import websocket
import secrets
import string


class SparkImage(object):
    answer = ""
    usage = None

    def __init__(self, app_id, api_key, api_secret, api_version, domain):
        spark_image_url_format = "wss://spark-api.cn-huabei-1.xf-yun.com/{}/image"

        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.spark_image_url = spark_image_url_format.format(api_version)
        self.host = urlparse(self.spark_image_url).netloc
        self.path = urlparse(self.spark_image_url).path
        self.api_version = api_version
        self.domain = domain

    def generate_random_id(self):
        characters = string.ascii_letters + string.digits
        string_length = 28
        return ''.join(secrets.choice(characters) for _ in range(string_length))

    def create_url(self):
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        print(signature_origin)
        signature_sha = hmac.new(self.api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(
            signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(
            authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }

        return self.spark_image_url + '?' + urlencode(v)

    def on_error(self, ws, error):
        print("### Websocket error:", error)

    def on_close(self, ws, one, two):
        print(" ")

    def on_open(self, ws):
        thread.start_new_thread(self.run, (ws,))

    def run(self, ws, *args):
        params = self.generate_params(
            messages=ws.messages,
            temperature=ws.temperature,
            max_tokens=ws.max_tokens
        )
        data = json.dumps(params)
        ws.send(data)

    def on_message(self, ws, message):
        data = json.loads(message)
        code = data['header']['code']
        if code != 0:
            print(f'请求错误: {code}, {data}')
            ws.close()
        else:
            choices = data["payload"]["choices"]
            status = choices["status"]
            content = choices["text"][0]["content"]
            self.answer += content
            self.usage = data["payload"]["usage"]
            if status == 2:
                ws.close()

    def generate_params(self, messages, temperature=0.7, max_tokens=2048):
        data = {
            "header": {
                "app_id": self.app_id,
                "uid": "verysmallwoods"
            },
            "parameter": {
                "chat": {
                    "domain": self.domain,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "auditing": "default"
                }
            },
            "payload": {
                "message": {
                    "text": messages
                }
            }
        }
        return data

    def chatCompletionStream(self, messages, temperature=0.7, max_tokens=2048):
        with connect(self.create_url()) as ws:
            params = self.generate_params(messages, temperature, max_tokens)
            ws.send(json.dumps(params))

            thread_id = self.generate_random_id()
            while True:
                try:
                    message = ws.recv()
                    data = json.loads(message)
                    code = data['header']['code']
                    if code != 0:
                        print(f'请求错误: {code}, {data}')
                        ws.close()
                        break
                    else:
                        payload = data["payload"]
                        choices = payload["choices"]
                        status = choices["status"]
                        content = choices["text"][0]["content"]

                        chunk = {
                            "id": f"chatcmpl-{thread_id}",
                            "object": "chat.completion.chunk",
                            "created": int(time()),
                            "model": "spark-ai",
                            "choices": [
                                {
                                    "index": 0,
                                    "delta": {
                                        "role": "assistant",
                                        "content": content
                                    },
                                    "finish_reason": None
                                }
                            ]
                        }
                        
                        if len(content) > 0:
                            yield f"data: {json.dumps(chunk)}\n\n"

                        if status == 2:
                            # Completed with status 2 
                            yield f"data: [DONE]\n\n"
                            break
                except (ConnectionClosed):
                    print("Connection closed")
                    yield f"data: [DONE]\n\n"
                    break
        return

    def chatCompletion(self, messages, temperature=0.7, max_tokens=2048):
        url = self.create_url()
        print(f"API URL: {url}")
        websocket.enableTrace(False)

        ws = websocket.WebSocketApp(
            url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )
        ws.messages = messages
        ws.temperature = temperature
        ws.max_tokens = max_tokens
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

        completion = {
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": self.answer
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": self.usage["text"]
        }
        
        return completion
