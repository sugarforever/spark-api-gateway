# Spark API Gateway

Spark API Gateway - 讯飞星火认知大模型API网管，提供OpenAI接口协议兼容的API。该网管目前支持如下API：

- POST /v1/chat/completions

## 使用方式

### Docker

### docker-compose

1. 克隆本代码仓库

2. 复制.env.example为.env，并根据您的星火应用配置，设置APP_ID，API_SECRET，API_KEY。

3. 通过 `docker-compose up` 启动服务。您将看到类似如下输出：

    ```shell
    [+] Running 1/0
    ✔ Container spark-api-gateway-spark-api-gateway-1  Created                                                                                                 0.0s 
    Attaching to spark-api-gateway-spark-api-gateway-1
    spark-api-gateway-spark-api-gateway-1  | INFO:     Started server process [1]
    spark-api-gateway-spark-api-gateway-1  | INFO:     Waiting for application startup.
    spark-api-gateway-spark-api-gateway-1  | INFO:     Application startup complete.
    spark-api-gateway-spark-api-gateway-1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
    ```
4. 通过 `curl` 命令测试

    ```shell
    curl --location 'http://localhost:8000/v1/chat/completions' \
        --header 'Content-Type: application/json' \
        --data '{
            "messages": [
                {
                    "role": "user",
                    "content": "大语言模型的理论基础是什么？"
                }
            ],
            "model": "spark-api",
            "max_tokens": null,
            "stream": false,
            "n": 1,
            "temperature": 0.7
        }'
    ```
