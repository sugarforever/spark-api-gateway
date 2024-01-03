from typing import Annotated, List, Union, Optional
from fastapi import FastAPI, Header, Request, HTTPException, WebSocket
from fastapi.openapi.models import OpenAPI, Server
from starlette.responses import HTMLResponse, StreamingResponse
from pathlib import Path
from dotenv import load_dotenv
from llms.spark import SparkChat, SparkImage, SparkUtil
from services import ImageService, load_logging_config
from models.schema import ChatCompletion
from models.config import load_config_dict

load_dotenv()
config_dict = load_config_dict()

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
    domain = SparkUtil.get_domain(version)

    spark_client = None

    if chatCompletion.model == 'vision':
        secrets = config_dict['vision']

        spark_client = SparkImage(
            X_APP_ID or secrets["app_id"],
            X_API_KEY or secrets["api_key"],
            X_API_SECRET or secrets["api_secret"]
        )
    else:
        secrets = config_dict['spark-ai']
        spark_client = SparkChat(
            X_APP_ID or secrets["app_id"],
            X_API_KEY or secrets["api_key"],
            X_API_SECRET or secrets["api_secret"],
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
                        "content": ImageService.get_image_base64(item.image_url.url),
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
