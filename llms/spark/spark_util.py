from pydantic import BaseModel
from enum import Enum


class SparkApiSpec(BaseModel):
    domain: str
    api_version: str
    model: str


class SparkModels(Enum):
    SPARK_COMPLETION_V15 = "spark-chat-v1.5"
    SPARK_COMPLETION_V2 = "spark-chat-v2"
    SPARK_COMPLETION_V3 = "spark-chat-v3"
    SPARK_COMPLETION_VISON = "spark-chat-vision"

    @classmethod
    def of(cls, model):
        return next((member for member in cls if member.value == model), None)
    
    @classmethod
    def values(cls):
        return [member.value for member in cls]


SPARK_MODELS_MAP = {
    SparkModels.SPARK_COMPLETION_V15: SparkApiSpec(domain="general", api_version="v1.1", model=SparkModels.SPARK_COMPLETION_V15.value),
    SparkModels.SPARK_COMPLETION_V2: SparkApiSpec(domain="generalv2", api_version="v2.1", model=SparkModels.SPARK_COMPLETION_V2.value),
    SparkModels.SPARK_COMPLETION_V3: SparkApiSpec(domain="generalv3", api_version="v3.1", model=SparkModels.SPARK_COMPLETION_V3.value),
    SparkModels.SPARK_COMPLETION_VISON: SparkApiSpec(
        domain="general", api_version="v2.1", model=SparkModels.SPARK_COMPLETION_VISON.value)
}


class SparkUtil:

    @classmethod
    def get_api_spec(cls, model):
        spec = None

        model_enum = SparkModels.of(model)

        if model_enum in SPARK_MODELS_MAP:
            spec = SPARK_MODELS_MAP[model_enum]

        return spec
