from pydantic import BaseModel
from enum import Enum


class SparkApiSpec(BaseModel):
    domain: str
    api_version: str
    model_version: str


class SparkModels(Enum):
    SPARK_CHAT_COMPLETION_V15 = "spark-chat-completion-v1.5"
    SPARK_CHAT_COMPLETION_V2 = "spark-chat-completion-v2"
    SPARK_CHAT_COMPLETION_V3 = "spark-chat-completion-v3"
    SPARK_CHAT_COMPLETION_VISON = "spark-chat-completion-vision"


SPARK_MODELS_MAP = {
    SparkModels.SPARK_CHAT_COMPLETION_V15: SparkApiSpec("general", "v1.1", "v1.5"),
    SparkModels.SPARK_CHAT_COMPLETION_V2: SparkApiSpec("generalv2", "v2.1", "v2"),
    SparkModels.SPARK_CHAT_COMPLETION_V3: SparkApiSpec("generalv3", "v3.1", "v3"),
    SparkModels.SPARK_CHAT_COMPLETION_VISON: SparkApiSpec(
        "general", "v2.1", "vision")
}


class SparkUtil:

    @classmethod
    def get_api_spec(cls, model):
        spec = None

        if model in SPARK_MODELS_MAP:
            spec = SPARK_MODELS_MAP[model]

        return spec
