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
    except Exception as e:
        await message.channel.send(str(e))






def generate_message(tasks):
    send_message=""
    if len(tasks) == 0:
        send_message="現在表示できる課題はありません"
    else:
        for task in tasks:
            send_message+=f"```{task['date']} {task['time']}\n{task['class']}\n{task['task']}\n\n```"
    return send_message

@tasks.loop(seconds=3600)
async def alert_near_task():
    with open('./near_tasks.json', 'r') as f:
        near_tasks = json.load(f)
    if len(near_tasks) != 0:
        channel = client.get_channel(int(CHANNEL_ID))
        await channel.send(generate_message(near_tasks))


if __name__=="__main__":
    client.run(os.getenv('TOKEN'))