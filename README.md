# Spark API Gateway

Spark API Gateway - 讯飞星火认知大模型API网管，提供OpenAI接口协议兼容的API。该网管目前支持如下API：

- POST /v1/chat/completions

## 使用方式

### Docker

### docker-compose

1. 克隆本代码仓库

2. (可选步骤) 复制.env.example为.env，并根据您的星火应用配置，设置APP_ID，API_SECRET，API_KEY。

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
        --header 'X_APP_ID: 123456' \
        --header 'X_API_SECRET: 123456' \
        --header 'X_API_KEY: 123456' \
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
            "temperature": 0.7,
            "version": "v2.1"
        }'
    ```

提示：

1. 请求消息体中通过 `version` 参数指定期望使用的认知大模型版本。当前支持v1.1，v2.1，v3.1。
2. HTTP头 `X_APP_ID`，`X_API_SECRET`， `X_API_KEY` 用于指定请求中期望使用的讯飞应用的密钥信息。
3. 对于 `X_APP_ID`，`X_API_SECRET`， `X_API_KEY` ，在HTTP头中未指定时，将使用环境变量中的值。

## 云端部署

该项目已部署在Vercel平台。大家可以通过[https://sparkai-gateway.vercel.app/v1/chat/completions](https://sparkai-gateway.vercel.app/v1/chat/completions)免费使用。

测试命令如下：

```shell
curl --location 'https://sparkai-gateway.vercel.app/v1/chat/completions' \
--header 'X_APP_ID: 123456' \
--header 'X_API_SECRET: 123456' \
--header 'X_API_KEY: 123456' \
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
    "temperature": 0.7,
    "version": "v2.1"
}'
```

