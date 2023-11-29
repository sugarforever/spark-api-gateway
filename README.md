# Spark API Gateway

星火大模型通过API提供访问。您可以点击[官方链接](https://dub.sh/xinghuo)申请API访问。

Spark API Gateway - 讯飞星火认知大模型API网管，提供OpenAI接口协议兼容的API。该网管目前支持如下API：

- POST /v1/chat/completions

OpenAI在聊天补全上支持文本补全与图片理解。Spark API Gateway已经集成星火认知大模型的图片理解API，从而在/v1/chat/completions上支持OpenAI gpt-4-vision-preview模型的API schema，并提供同级别的图片理解能力。

OpenAI的图片理解 `curl` 示例：

```shell
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4-vision-preview",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "image_url",
            "image_url": {
                "url": "https://pbs.twimg.com/media/F_c_hrGWcAA3w0p?format=jpg&name=medium"
            }
          },
          {
            "type": "text",
            "text": "这张图里的标志是什么？"
          }
        ]
      }
    ],
    "max_tokens": 300
  }'
```

Spark API Gateway的图片理解 `curl` 示例：

```shell
curl --location 'http://localhost:8000/v1/chat/completions' \
  -H 'X_APP_ID: 123456' \
  -H 'X_API_SECRET: 123456' \
  -H 'X_API_KEY: 123456' \
  -H "Content-Type: application/json" \
  -d '{
    "model": "vision",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "image_url",
            "image_url": {
                "url": "https://pbs.twimg.com/media/F_c_hrGWcAA3w0p?format=jpg&name=medium"
            }
          },
          {
            "type": "text",
            "text": "这张图里的标志是什么？"
          }
        ]
      }
    ],
    "max_tokens": 300
  }'
```

您应该期望类似如下输出：

```json
{
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "这张图里的标志是宝马的logo。"
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "question_tokens": 11,
        "prompt_tokens": 51,
        "completion_tokens": 10,
        "total_tokens": 61
    },
    "version": "v1.1",
    "domain": "general"
}
```

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
4. 请求消息体中的 `model` 参数支持 `spark-api`, `vision`。

    `spark-api` 支持文本补全，`vision` 支持图片理解。

## 云端部署

该项目已部署在Vercel平台。大家可以通过[https://sparkai-gateway.vercel.app/v1/chat/completions](https://sparkai-gateway.vercel.app/v1/chat/completions)免费使用。

测试命令如下：

**文本补全** 

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

**图片理解** 

```shell
curl --location 'https://sparkai-gateway.vercel.app/v1/chat/completions' \
--header 'X_APP_ID: 123456' \
--header 'X_API_SECRET: 123456' \
--header 'X_API_KEY: 123456' \
--header 'Content-Type: application/json' \
--data '{
    {
        "model": "vision",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://pbs.twimg.com/media/F_c_hrGWcAA3w0p?format=jpg&name=medium"
                        }
                    },
                    {
                        "type": "text",
                        "text": "这张图里的标志是什么？"
                    }
                ]
            }
        ],
        "max_tokens": 4096
    }
}'
```

