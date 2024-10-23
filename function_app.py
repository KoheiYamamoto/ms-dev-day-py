import azure.functions as func
import logging
import json
import os
from openai import AzureOpenAI

# Azure open ai をコールするためのインスタンス
client = AzureOpenAI(
    api_key=os.environ["OPENAI_KEY"],  
    api_version="2024-07-01-preview",
    azure_endpoint=os.environ["OPENAI_ENDPOINT"]
)

# システムプロンプト
system_prompt = """
あなたはトリオ漫才のつっこみ役です。あなたと会話している人が次の2点を教えてくれます。
# 受け取るフォーマット
[A] 説明したシチュエーションと話題の情報 (話のフリ役)
[B] Aさんのコメントを受けて解答したコメント (ボケ役)
Bさんは必ずコメントでボケてきますので、あなたはそれに対して勢いがあるwitかつ強めなブラックジョークに富んだツッコミをしてください。
# サンプル 
受け取るテキスト
[A] やぁ、B君Cさん。明日から夏休みだね。私はプール行ったり海に行ったり忙しくなりそうだよ。B君はどう？
[B] 僕は雪だるま作ったりスノボしたりで忙しくなりそうだよ。
※ あなたが生成するテキスト 
雪なんかあるかい！
"""

# azure open ai の chat completions api をコールする関数 (モデルはgpt-4o)
def call_aoai(text):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content  

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
 
    # リクエストボディを取得して text の値を取り出す
    req_body = req.get_json()
    text = req_body.get('text')

    # azure open ai に渡す
    response = call_aoai(text)

    # response を json 内の text に入れて返す
    return func.HttpResponse(
        json.dumps({'text': response}, ensure_ascii=False),
        mimetype="application/json",
        charset="utf-8"
    )