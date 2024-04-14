import json
import datetime

from system_prompt import parse_message_text


first_date = datetime.datetime(2022, 2, 1, 0, 0, 0)

with open('result.json', mode='r', encoding= 'utf-8') as file:
    dialog = json.load(file)

with open('prompt.txt', mode='r', encoding='utf') as file:
    prompt = file.read()    

SYSTEM_MESSAGE = {
    "role": "system",
    "content": prompt
    }

count = 0
training_examples = 0

data = []
messages = [SYSTEM_MESSAGE,]
last_time = last_time_example = 0
last_role = 'none'
user_count = assistant_count = 0
for message in dialog['messages']:
    message_time = int(message['date_unixtime'])
    if message_time < first_date.timestamp():
        continue
    
    
    # each day new example
    
    flag = False
    if message['type'] == 'message':
        if any(word in parse_message_text(message['text']).lower() for word in ('привет', 'салют')):
            if message_time - last_time_example > datetime.timedelta(hours=6).total_seconds() \
                and len(messages) > 5\
                and assistant_count > 0 and user_count > 0:
                flag = True
    
    if (message_time - last_time > datetime.timedelta(hours=12).total_seconds() or flag) and assistant_count > 0 and user_count > 0:
        data.append({"messages" : messages.copy()})
        messages.clear()
        assistant_count = user_count = 0
        last_role = 'system'
        
        messages.append(
            SYSTEM_MESSAGE
        )
        
        last_time_example = message_time
    
    if message['type'] == 'message':    
        if message['from'] == 'Even':    
            role = 'assistant'
        else:
            role = 'user'

        text = parse_message_text(message['text'])

        if 'media_type' in message and 'message' in message['media_type']:
            text = message['media_type']
        
        if text:
            if message_time - last_time  < 360 and role == last_role:
                messages[-1]["content"] += '\n' + text
            else:
                count += 1
                messages.append(
                    {"role" : role,
                    "content": text}
                )
                
                if role == 'assistant':
                    assistant_count += 1
                else:
                    user_count += 1
                    
                                
            last_time = message_time
            last_role = role
    elif message['type'] == 'service' and message['action'] == 'phone_call':
        if message['actor'] != 'Even':    
            role = 'user'
            messages.append(
                {"role" : role,
                 "content": 'call'}
            )
            
            user_count += 1
        role = 'assistant'
        
        if message['discard_reason'] == 'missed':
            messages.append(
                {
                    "role": role,
                    "content": "🚫 📞 missed phone call"
                }
        )
            
        elif message['discard_reason'] == 'hangup':
            text = "📞 phone call"
            if 'duration_seconds' in message:
                text += f" for {message['duration_seconds']} s"
            
            
            messages.append(
                {
                    "role": role,
                    "content": text
                }
            ) 
            
            assistant_count += 1

    
with open('data.json', mode='w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False)

with open('data.jsonl', mode='w', encoding='utf-8') as file:
    for entry in data:
        json_str = json.dumps(entry, ensure_ascii=False)
        file.write(json_str + '\n')

print(count)
print(len(data))