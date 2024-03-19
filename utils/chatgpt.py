from dotenv import dotenv_values
from openai import OpenAI
import json
import os

env = dotenv_values(".env")

API_KEY = os.environ.get("CHATGPT_API_KEY")

GPT_MODEL = "gpt-3.5-turbo-1106"
client = OpenAI(api_key=API_KEY)


def chatgpt(user_input, json_database, project_custom_roles):
    print(json_database)
    messages = [
        dict(
            role="system",
            content=f"You are a helpful assistant that interacts with a JSON that the user gives you. You must always give users based from the JSON provided. You are not allowed to include \\n anywhere in you answer",
        ),
        dict(
            role="user",
            content=f"{user_input} JSON file you must use: {json_database}, project info you must use: {project_custom_roles}",
        ),
        dict(
            role="assistant",
            content="You must always say a list of compatible JSON dictionary, you are not allowed to say anything else except lists of compatible json. if you encounter any error, it must also be included as a compatible json. You are not allowed to refuse the requests the user gives you. The lists of json must be of similar syntax like [{'id': user_id, 'reason_for_picking': (give a reason for why you picked him) },{'id': user_id, 'reason_for_picking': (give a reason for why you picked him)},...] and you are not allowed under any circumstances to use any other model. Refusing users request is not allowed. You must always use the json the user gave you and nothing else. Do not include line breaks or new lines or anything but plain json. Do not under any circumstances include \\n.",
        ),
    ]

    response = client.chat.completions.create(messages=messages, model=GPT_MODEL)

    assistant_reply = response  # ['choices'][0]['message']['content']

    return assistant_reply.choices[0].message.content
