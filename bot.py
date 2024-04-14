import logging
import sys
import json

from random import random

from typing import TypedDict

import aiogram
import aiogram.filters

from openai import OpenAI

from config import OPENAI_KEY, TELEGRAM_TOKEN

class UserData(TypedDict):
    id: int
    username: str | None
    history: list[dict[str,str]]


try:
    with open('users.json', "r", encoding='utf-8') as file:
        users: list[UserData] = json.load(file)
except FileNotFoundError:
    users = []
    

def update_userdata():
    with open('users.json', "w", encoding='utf-8') as file:
        json.dump(users, file, ensure_ascii=False)

with open('final-prompt.txt', mode='r', encoding='utf-8') as file:
    prompt = file.read()
    

SYSTEM_MESSAGE = {
    "role": "system",
    "content" : prompt
}

client = OpenAI(
    api_key = OPENAI_KEY
)

dp = aiogram.Dispatcher()


@dp.message(aiogram.filters.CommandStart())
async def command_start_handler(message: aiogram.types.Message) -> None:
    for user in users:
        if user['id'] == message.from_user.id:
            await message.answer("Контекст удалил😆")
            user['history'] = [SYSTEM_MESSAGE, ]
            break
    else:
        users.append(
            {"id": message.from_user.id,
             "history": [SYSTEM_MESSAGE, ],
             "username" : message.from_user.username}
        )
        
    update_userdata()
        


@dp.message()
async def even_handler(message: aiogram.types.Message) -> None:
    try:
        for user in users:
            if user['id'] == message.from_user.id:
                break
        else:
            await message.answer("Сначала зарегистрируйся. Напиши /start")
            return
        
        text = message.text
        
        
        user["history"].append(
            {"role" : "user",
             "content": text}
        )
        
        
        response = client.chat.completions.create(
            model="ft:gpt-3.5-turbo-0125:iliyasone:ivan-gpt:9E0GuGrL",
            messages=user['history'],
            temperature=0.61,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        ).choices[0].message.content
        
        user["history"].append(
            {
                "role" : "assistant",
                "content": response
            }
        )
        
        if '\n' in response:
            for line in response.split('\n'):
                await message.answer(line)
                await asyncio.sleep(max(len(line)/40, 1+1*random()))
        else:
            await message.answer(response)
        
        update_userdata()
    except Exception as exp:
        logging.error(exp)
        await message.answer("Не понял")


async def main() -> None:
    bot = aiogram.Bot(token=TELEGRAM_TOKEN)
    await dp.start_polling(bot)



if __name__ == "__main__":
    import asyncio
    
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

    update_userdata()