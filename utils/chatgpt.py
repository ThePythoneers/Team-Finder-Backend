from dotenv import dotenv_values
from openai import OpenAI
import json
import os

env = dotenv_values(".env")

# API_KEY = os.environ.get("CHATGPT_API_KEY")

# GPT_MODEL = "gpt-3.5-turbo-1106"
# client = OpenAI(api_key=API_KEY)


def chatgpt(user_input, json_database):
    print(json_database)
    messages = [
        dict(role="system",
             content=f"You are a helpful assistant that interacts with this {json_database} JSON database."),

        dict(role="user", content=user_input),
        dict(role="assistant", content="Executing users request and returning only the json with compatible database users")
    ]

    response = client.chat.completions.create(messages=messages, model=GPT_MODEL)

    assistant_reply = response#['choices'][0]['message']['content']

    return assistant_reply.choices[0].message.content

