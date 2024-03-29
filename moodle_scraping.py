import csv
import datetime
import json
import os
import time

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from methods import get_date_format, get_task_from_date


class GetTask:
    @classmethod
    def get_moodle_task(cls) -> list:
        load_dotenv()
        url = "https://ict-i.el.kyutech.ac.jp/my/"
        driver = cls.open_url_link(url)
        cls.scraping_task(driver)
        driver.quit()

    def open_url_link(url: str):
        option = webdriver.ChromeOptions()
        option.add_argument("--headless")
        option.add_argument("--disable-dev-shm-usage")
        driver =webdriver.Chrome(ChromeDriverManager().install())
        driver.get(url)
        driver.find_element(By.ID,"username").send_keys(str(os.getenv('MOODLE_ID')))
        driver.find_element(By.ID,"password").send_keys(str(os.getenv('MOODLE_PASSWORD')))
        driver.find_element(By.ID,"loginbtn").click()
        time.sleep(5)

        return driver

    def scraping_task(driver):
        soup = BeautifulSoup(driver.page_source,'html.parser')
        task_table = soup.find_all('div',class_="pb-2")[1]
        GetTask.get_task_from_table(task_table)

    def get_task_from_table(task_table):
        task_dict={}
        task_start_line = task_table.find('div',class_="mt-3")
        task_date=""
        while task_start_line is not None:
            task_date=task_start_line.find("h5").text.replace(' ','').replace('\n','')
            task_dict[task_date]=[]
            task_elements =task_start_line.find_next_sibling('div').find_all('div',recursive=False)
            for task_element in task_elements:
                task_dict[task_date].append({"date":task_date,"time":task_element.find('small').text.replace(' ','').replace('\n',''),"task":task_element.find('a').get("title").replace(' ','').replace('\n',''),"class":task_element.find('small',class_="mb-0").text.replace(' ','').replace('\n',''),"url":task_element.find('a').get('href')})
            task_start_line=task_start_line.find_next_sibling('div',class_="mt-3")
        with open(f'./task.json', 'w') as f:
            json.dump(task_dict, f, ensure_ascii=False)
    def output_to_csv(output_dict):
        with open('./task.csv',"w", encoding="utf_8_sig")as f:
            writer = csv.DictWriter(f, ["date","time","task","class"])
            writer.writeheader()
            for key,value in output_dict.items():
                for task_value in value:
                    task_value["date"]=key
                    writer.writerow(task_value)
    @classmethod
    def task_update(cls):
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
if __name__ == '__main__':
    GetTask.get_moodle_task()