from typing import Annotated, List, Union, Optional
from fastapi import FastAPI, Header, Request, HTTPException, WebSocket
from fastapi.openapi.models import OpenAPI, Server
from starlette.responses import HTMLResponse, StreamingResponse
from pathlib import Path
from pydantic import BaseModel, validator
from dotenv import load_dotenv
from spark_chat import SparkChat
from spark_image import SparkImage
import os
import base64
import requests

load_dotenv()
spark_model_versions = ['v1.1', 'v2.1', 'v3.1']

servers = [
    {
        "url": "https://sparkai-gateway.vercel.app",
        "description": "Spark AI Gateway - Staging"
    },
]

app = FastAPI(servers=servers)

"""
{ 
    "messages": [ 
      { "role": "user", "content": "What is Large Language Model?" }
    ], 
    "temperature": 0.7, 
    "max_tokens": -1,
    "stream": false
  }
"""


class MessageContentTextItem(BaseModel):
    type: str
    text: str


class ImageUrl(BaseModel):
    url: str


class MessageContentImageItem(BaseModel):
    type: str
    image_url: ImageUrl


class Message(BaseModel):
    role: str
    content: Union[str, List[Union[MessageContentTextItem,
                                   MessageContentImageItem]]] = None


class ChatCompletion(BaseModel):
    temperature: Optional[float] = 0.7
    max_tokens: Optional[Union[int, None]] = 2048
    stream: Optional[bool] = False
    messages: List[Message] = []
    model: Optional[str] = 'spark-api'
    n: Optional[int] = 1
    version: Optional[Union[str, None]] = 'v1.1'

    @validator('max_tokens', pre=True, always=True)
    def set_max_tokens(cls, value):
        if value is None:
            return 2048
        return value

    @validator('version', pre=True, always=True)
    def set_version(cls, value):
        if value is None:
            return 'v1.1'

        if value not in spark_model_versions:
            return 'v1.1'

        return value


def get_domain(version):
    domain = None
    if version == 'v1.1':
        domain = "general"
    elif version == 'v2.1':
        domain = "generalv2"
    elif version == 'v3.1':
        domain = "generalv3"

    return domain


def get_image_base64(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            image_data = response.content
            base64_data = base64.b64encode(image_data).decode('utf-8')

            return base64_data
        else:
            print(
                f"Failed to fetch image. Status code: {response.status_code}")
            raise Exception(f"Failed to fetch image: {url}")
    except Exception as e:
        raise e

@app.post("/v1/chat/completions")
def chat_completion(
    chatCompletion: ChatCompletion,
    X_APP_ID: Annotated[Union[str, None], Header(
        convert_underscores=False)] = None,
    X_API_KEY: Annotated[Union[str, None], Header(
        convert_underscores=False)] = None,
    X_API_SECRET: Annotated[Union[str, None],
                            Header(convert_underscores=False)] = None
):
    version = chatCompletion.version
    domain = get_domain(version)

    spark_client = None

    if chatCompletion.model == 'vision':
        spark_client = SparkImage(
            X_APP_ID or os.environ["APP_ID"],
            X_API_KEY or os.environ["API_KEY"],
            X_API_SECRET or os.environ["API_SECRET"]
        )
    else:
        spark_client = SparkChat(
            X_APP_ID or os.environ["APP_ID"],
            X_API_KEY or os.environ["API_KEY"],
            X_API_SECRET or os.environ["API_SECRET"],
            f"ws://spark-api.xf-yun.com/{version}/chat",
            domain
        )

    message_list = []
    for message in chatCompletion.messages:
        role = message.role
        content = message.content
        if isinstance(content, str):
            message_list.append({"role": role, "content": content})
        elif isinstance(content, List):
            for item in content:
                if item.type == 'text':
                    message_list.append({
                        "role": role,
                        "content": item.text
                    })
                elif item.type == 'image_url':
                    message_list.append({
                        "role": role,
                        "content": get_image_base64(item.image_url.url),
                        "content_type": "image"
                    })

    print("stream: ",  chatCompletion.stream)
    if (chatCompletion.stream):
        return StreamingResponse(spark_client.chatCompletionStream(
            message_list,
            chatCompletion.temperature,
            chatCompletion.max_tokens
        ), media_type="text/event-stream")
    else:
        completion = spark_client.chatCompletion(
            message_list,
            chatCompletion.temperature,
            chatCompletion.max_tokens
        )
        completion["version"] = version
        completion["domain"] = domain
        return completion


@app.get("/", response_class=HTMLResponse)
async def serve_readme(request: Request):
    index_path = Path("web/index.html")  # Adjust the path as needed
    if index_path.is_file():
        with open(index_path, "r", encoding="utf-8") as html_file:
            return html_file.read()
    else:
        raise HTTPException(status_code=404, detail="NOT FOUND")


@app.get("/privacy", response_class=HTMLResponse)
async def serve_privacy_policy():
    with open("web/privacy_policy.html", "r", encoding="utf-8") as privacy_policy_file:
        privacy_policy_content = privacy_policy_file.read()
        return privacy_policy_content


@app.get("/openapi.json", response_model=OpenAPI)
async def get_openapi_schema():
    openapi_schema = app.openapi()
    return openapi_schema
