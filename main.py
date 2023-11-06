from typing import Annotated, List, Union, Optional
from fastapi import FastAPI, Header
from pydantic import BaseModel, validator
from dotenv import load_dotenv
from spark_chat import SparkChat
import os

load_dotenv()

app = FastAPI()

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

class Message(BaseModel):
    role: str
    content: str

class ChatCompletion(BaseModel):
    temperature: float = 0.7
    max_tokens: Optional[Union[int, None]] = 2048
    stream: bool = False
    messages: List[Message] = []
    model: str
    n: int
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

@app.post("/v1/chat/completions")
def chat_completion(
    chatCompletion: ChatCompletion,
    X_APP_ID: Annotated[Union[str, None], Header(convert_underscores=False)] = None,
    X_API_KEY: Annotated[Union[str, None], Header(convert_underscores=False)] = None,
    X_API_SECRET: Annotated[Union[str, None], Header(convert_underscores=False)] = None
):
    version = chatCompletion.version
    domain = get_domain(version)

    spark_chat = SparkChat(
        X_APP_ID or os.environ["APP_ID"],
        X_API_KEY or os.environ["API_KEY"],
        X_API_SECRET or os.environ["API_SECRET"],
        f"ws://spark-api.xf-yun.com/{version}/chat",
        domain
    )

    message_dicts = [{"role": msg.role, "content": msg.content} for msg in chatCompletion.messages]
    completion = spark_chat.chatCompletion(message_dicts, chatCompletion.temperature, chatCompletion.max_tokens)
    completion["version"] = version
    completion["domain"] = domain
    return completion
