import datetime
import json
import os
import re
import time

import discord
from discord.ext import tasks
from dotenv import load_dotenv

from moodle_scraping import GetTask

load_dotenv()
CHANNEL_ID=os.getenv('CHANNEL_ID')

if __name__=="__main__":
    while(1):
        now = datetime.datetime.now()
        if 1:
        # if now.minute==0 or now.minute == 30:
            Intents = discord.Intents.all()
            Intents.members = True
            client = discord.Client(intents=Intents)
            break
        time.sleep(5)
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    task_update_loop.start()
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

def get_task_from_date(detect_dates):
    with open('./task.json', 'r') as f:
        task = json.load(f)
    return_task = []
    for detect_key in detect_dates:
        task_exist = task.get(detect_key)
        if task_exist:
            # task_exist.append
            return_task.extend(task_exist)
    return return_task

def get_date_format(detect_date):
    now = datetime.date.today()
    w_list = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
    if detect_date =="today":
        return [
            f"{now.year}年 {now.month}月 {now.day}日({w_list[now.weekday()]})"
            ]
    elif detect_date =="tomorrow":
        return  [
            f"{now.year}年 {now.month}月 {now.day+1}日({w_list[now.weekday()+1]})"
            ]
    elif  re.match(".*?(\d+)", detect_date):
        print([f"{(now+datetime.timedelta(days=i)).year}年 {(now+datetime.timedelta(days=i)).month}月 {(now+datetime.timedelta(days=i)).day}日({w_list[(now+datetime.timedelta(days=i)).weekday()]})" for i in range(int(re.sub("[^\d]","", detect_date)))])
        return [f"{(now+datetime.timedelta(days=i)).year}年 {(now+datetime.timedelta(days=i)).month}月 {(now+datetime.timedelta(days=i)).day}日({w_list[(now+datetime.timedelta(days=i)).weekday()]})" for i in range(int(re.sub("[^\d]","", detect_date)))]

def task_update():
    GetTask.get_moodle_task()
    today = get_date_format("today")
    todays_tasks = get_task_from_date(today)
    near_tasks = []
    if len(todays_tasks) !=0:
        now = datetime.datetime.now()
        for todays_task in todays_tasks:
            time_limit =datetime.datetime(year = now.year,month = now.month,day = now.day,hour = int(todays_task["time"].split(':')[0]),minute = int(todays_task["time"].split(':')[1]))
            if (time_limit-now).seconds<7200:
                near_tasks.append(todays_task)
    with open('./near_tasks.json', 'w') as f:
        json.dump(near_tasks, f, ensure_ascii=False)




def generate_message(tasks):
    send_message=""
    if len(tasks) == 0:
        send_message="現在表示できる課題はありません"
    else:
        for task in tasks:
            send_message+=f"```{task['date']} {task['time']}\n{task['class']}\n{task['task']}\n\n```"
    return send_message

@tasks.loop(seconds=60*60)
async def alert_near_task():
    with open('./near_tasks.json', 'r') as f:
        near_tasks = json.load(f)
    if len(near_tasks) != 0:
        channel = client.get_channel(int(CHANNEL_ID))
        await channel.send(generate_message(near_tasks))

@tasks.loop(seconds=60*60)
async def task_update_loop():
    task_update()

client.run(os.getenv('TOKEN'))
