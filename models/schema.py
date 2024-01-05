from pydantic import BaseModel, validator
from typing import Annotated, List, Union, Optional
from llms.spark import SparkModels

spark_model_versions = SparkModels.values()

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
    model: Optional[str] = SparkModels.SPARK_COMPLETION_V3.value
    n: Optional[int] = 1

    @validator('max_tokens', pre=True, always=True)
    def set_max_tokens(cls, value):
        if value is None:
            return 2048
        return value

    @validator('model', pre=True, always=True)
    def set_model(cls, value):
        if value not in spark_model_versions or value is None:
            return SparkModels.SPARK_COMPLETION_V3.value
        return value
    
