import datetime
import json
import re


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
            f"{now.year}年 {f'0{now.month}'[-2:]}月 {now.day}日({w_list[now.weekday()]})"
            ]
    elif detect_date =="tomorrow":
        return  [
            f"{now.year}年 {f'0{now.month}'[-2:]}月 {now.day+1}日({w_list[now.weekday()+1]})"
            ]
    elif  re.match(".*?(\d+)", detect_date):
        print([f"{(now+datetime.timedelta(days=i)).year}年 {(now+datetime.timedelta(days=i)).month}月 {(now+datetime.timedelta(days=i)).day}日({w_list[(now+datetime.timedelta(days=i)).weekday()]})" for i in range(int(re.sub("[^\d]","", detect_date)))])
        return [f"{(now+datetime.timedelta(days=i)).year}年 {f'0{(now+datetime.timedelta(days=i)).month}'[-2:]}月 {(now+datetime.timedelta(days=i)).day}日({w_list[(now+datetime.timedelta(days=i)).weekday()]})" for i in range(int(re.sub("[^\d]","", detect_date)))]

