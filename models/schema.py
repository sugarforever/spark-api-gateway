from pydantic import BaseModel, validator
from typing import Annotated, List, Union, Optional

spark_model_versions = ['v1.1', 'v2.1', 'v3.1']

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
    
