import asyncio
import datetime
import json
import os
import re
import time

import discord
from discord.ext import tasks
from dotenv import load_dotenv

from methods import get_date_format, get_task_from_date
from moodle_scraping import GetTask

load_dotenv()
CHANNEL_ID=os.getenv('CHANNEL_ID')
MENTION_ID = os.getenv('MENTION_USER_ID')
Intents = discord.Intents.all()
Intents.members = True
client = discord.Client(intents=Intents)
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    alert_near_task.start()



@client.event
async def on_message(message):
    if message.author == client.user:
        return
    try:
        if "get_task" in message.content:
            await message.channel.send(generate_message(get_task_from_date(get_date_format(message.content))))
        if "get_today" in message.content:
            await message.channel.send(generate_message(get_task_from_date(get_date_format("today"))))
        if "get_tomorrow" in message.content:
            await message.channel.send(generate_message(get_task_from_date(get_date_format("tomorrow"))))
        if "add" in message.content:
            generate_alert(message.content)
        if "delete" in message.content:
            delete_alert(message.content)
        if "show" in message.content:
            await message.channel.send(generate_alert(show_user_task))
    except Exception as e:
        await message.channel.send(str(e))


def generate_message(tasks):
    send_message=""
    if len(tasks) == 0:
        send_message="現在表示できる課題はありません"
    else:
        for task in tasks:
            send_message+=f"```{task['date']} {task['time']}\n{task['class']}\n{task['task']}```{task['url']}\n\n"
    return send_message

def generate_alert(generate_message):
    try:
        with open('user_alert.json',"r")as f:
            user_alert = json.load(f)
    except:
        user_alert = {}
    split_message = generate_message.split(' ')
    for day in split_message[2].split(','):
        add_task = {"date":f"毎週{day}","time":split_message[3],"task":split_message[4],"class":"","url":""}
        if user_alert.get(day) is  None:
            user_alert[day] = {split_message[3]:[add_task]}
        elif  user_alert.get(day).get(split_message[3]) is None:
            user_alert[day][split_message[3]]=[add_task]
        else:
            user_alert[day][split_message[3]].append(add_task)
    with open('user_alert.json',"w")as f:
            json.dump(user_alert,f, ensure_ascii=False)
def delete_alert(delete_message):
    try:
        with open('user_alert.json',"r")as f:
            user_alert = json.load(f)
    except:
        user_alert = {}
    if "clear" in delete_message:
        user_alert.clear()
    else:
        split_message = delete_message.split(' ')
        for day in split_message[2].split(','):
            del user_alert[day][split_message[3]]

    with open('user_alert.json',"w")as f:
            json.dump(user_alert,f, ensure_ascii=False)

def show_user_task():
    with open('./user_alert.json', 'r') as f:
        user_alert = json.load(f)
    task =[]
    for day in ['月', '火', '水', '木', '金', '土', '日']:
        if user_alert.get(day) is not None:
            for task in user_alert.get(day).values():
                task.extend(task)
    return task
def alert_user_task():
    now = datetime.datetime.now()
    with open('./user_alert.json', 'r') as f:
        user_alert = json.load(f)
    w_list = ['月', '火', '水', '木', '金', '土', '日']
    if user_alert.get(w_list[now.weekday()]) is None:
        return []
    elif user_alert.get(w_list[now.weekday()]).get(str(now.hour)+":00") is None:
        return []
    else:
        return user_alert.get(w_list[now.weekday()]).get(str(now.hour)+":00")

@tasks.loop(seconds=10)
async def alert_near_task():
    now = datetime.datetime.now()
    channel = client.get_channel(int(CHANNEL_ID))
    if now.minute == 00:
        with open('./near_tasks.json', 'r') as f:
            near_tasks = json.load(f)
        if len(near_tasks) != 0:
            await channel.send(generate_message(near_tasks))
        tasks = alert_user_task()
        if len(tasks)!=0:
            await channel.send(generate_message(tasks))

    if (now.hour == 6 or now.hour == 12 or now.hour == 18) and now.minute == 0:
        channel = client.get_channel(int(CHANNEL_ID))
        await channel.send(f'<@{MENTION_ID}>{generate_message(get_task_from_date(get_date_format("today")))}')
    if (now.hour == 12 or now.hour == 18) and now.minute == 0:
        message = generate_message(get_task_from_date(get_date_format("today")))
        if message !="現在表示できる課題はありません":
            await channel.send(f'<@{MENTION_ID}>{message}')




if __name__=="__main__":

    client.run(os.getenv('TOKEN'))
