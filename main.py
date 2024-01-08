from dotenv import load_dotenv
load_dotenv()

from models.config import load_config_dict, ConfigDict
from models.schema import ChatCompletion
from services import ImageService, load_logging_config
from llms.spark import SparkChat, SparkImage, SparkUtil, SparkModels
from pathlib import Path
from starlette.responses import HTMLResponse, StreamingResponse
from fastapi.openapi.models import OpenAPI, Server
from fastapi import FastAPI, Header, Request, HTTPException, WebSocket
from typing import Annotated, List, Union, Optional


config_dict: ConfigDict = load_config_dict()

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


@app.get("/v1/models")
def get_models():
    return {
        "object": "list",
        "data": [
            {"id": model, "object": "model", "created": None, "owned_by": None} for model in SparkModels.values()
        ]
    }


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
    model_name = chatCompletion.model
    spark_client = None
    api_spec = SparkUtil.get_api_spec(model_name)

    if api_spec.model == SparkModels.SPARK_COMPLETION_VISON.value:
        spark_client = SparkImage(
            X_APP_ID or config_dict.get(api_spec.model, "app_id"),
            X_API_KEY or config_dict.get(api_spec.model, "api_key"),
            X_API_SECRET or config_dict.get(api_spec.model, "api_secret"),
            api_spec.api_version,
            api_spec.domain
        )
    else:
        spark_client = SparkChat(
            X_APP_ID or config_dict.get(api_spec.model, "app_id"),
            X_API_KEY or config_dict.get(api_spec.model, "api_key"),
            X_API_SECRET or config_dict.get(api_spec.model, "api_secret"),
            f"ws://spark-api.xf-yun.com/{api_spec.api_version}/chat",
            api_spec.domain
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
        completion["model"] = api_spec.model
        completion["domain"] = api_spec.domain
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
