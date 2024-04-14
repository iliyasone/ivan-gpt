import json


def parse_message_text(__object: str | dict | list, /) -> str:
    if isinstance(__object, str):
        return __object
    if isinstance(__object, list):
        return ''.join(parse_message_text(text) for text in __object)
    if isinstance(__object, dict):
        if __object['type'] == 'text_link':
            return __object['href']
        return __object['text']
        
with open('channel/result.json', mode='r', encoding='utf-8') as file:
    data = json.load(file)

with open('channels_text.txt', mode='w',  encoding='utf-8') as file:
    for message in data['messages']:
        if message['text'] != '':
            file.write(parse_message_text(message['text']))
    