import csv
import datetime
import json
import os
import time

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By


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
        driver = webdriver.Chrome(executable_path="/bin/chromedriver", options=option)
        driver.get(url)
        driver.find_element(By.ID,"username").send_keys(str(os.getenv('MOODLE_ID')))
        driver.find_element(By.ID,"password").send_keys(str(os.getenv('MOODLE_PASSWORD')))
        driver.find_element(By.NAME,"_eventId_proceed").click()
        time.sleep(10)
        driver.execute_script("window.scrollTo(0, 3000);")

        return driver

    def scraping_task(driver):
        soup = BeautifulSoup(driver.page_source,'html.parser')
        print(soup)
        task_table = soup.find('div',id="page-container-2").find('div',class_="border-bottom pb-2")
        GetTask.get_task_from_table(task_table)

    def get_task_from_table(task_table):
        task_dict={}
        task_start_line = task_table.find('h5')
        task_date=""
        while task_start_line is not None:
            task_date=task_start_line.text
            task_dict[task_date]=[]
            task_elements =task_start_line.find_next_sibling('div').find_all('div',recursive=False)
            for task_element in task_elements:
                task_dict[task_date].append({"date":task_date,"time":task_element.find('small',class_="text-right text-nowrap ml-1").text.replace(' ','').replace('\n',''),"task":task_element.find('h6').text,"class":task_element.find('small').text})
            task_start_line=task_start_line.find_next_sibling('h5')
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
GetTask.get_moodle_task()