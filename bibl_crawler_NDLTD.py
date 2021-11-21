#encoding: utf-8
import os
from typing import final
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import lxml
import time
import shutil
import csv
from glob import glob
import re
from requests.exceptions import RequestException
from os import path
from bibl_crawler_tool import *

#碩博士論文網
def CRAWLER_NDLTD(driver_dir,target_dir,data):

    os.chdir(target_dir) #改儲存位置到目標資料夾

    #已下載資料
    dled_data = DOWNLOADED_DATA('ndltd',target_dir)

    filelog = open("ndltd_filelog.txt",'a',encoding='utf-8')


    browser = webdriver.Chrome(driver_dir) #指引chromedriver程式
    browser.get('http://ndltd.ncl.edu.tw/cgi-bin/gs32/gsweb.cgi/login?o=dwebmge') #碩博士論文網址
    browser.maximize_window() #瀏覽器最大化


    try:

        for code in data:

            survey = code[0] #叢集名稱
            keys = code[1] #指令

            if survey in dled_data: #目標叢集是否已下載
                continue

            time.sleep(10)
            browser.find_element_by_link_text("指令查詢").click() #點選指令查詢
            time.sleep(10)
            browser.find_element_by_id("ysearchinput0").click() #點指令查詢頁面文字輸入框
            browser.find_element_by_id("ysearchinput0").send_keys(keys) #輸入指令
            browser.find_element_by_id("gs32search").click() #點選搜尋
            time.sleep(10)
            Select(browser.find_element_by_name("jpsize")).select_by_visible_text("100") #選擇一頁顯示100筆

            soup = BeautifulSoup(browser.page_source, 'lxml') #讀取結果頁面

            #日期
            website_date = [tag.text for tag in soup.find_all('div', {'class':'user_div'})]
            date_str = ''.join(website_date)
            date_start = date_str.find("：") + 3
            date_end = date_start + 8
            date = str(date_str[int(date_start):int(date_end)]).replace("/","")

            #頁數
            page_str = soup.find_all("span",class_='etd_e')[1].string
            page_int = int(page_str) #筆數
            page_all = (page_int // 100) + 1 #頁數
            page_last = page_int % 100
            if page_last == 0:
                page_all = page_all - 1
            

            

            for page in range(1,page_all+1):
                time.sleep(10)
                soup = BeautifulSoup(browser.page_source, 'lxml') #讀每頁頁面html
                result_html = soup.find_all('table', {'class':'tableoutsimplefmt2'})
                result_list = []
                for index in result_html:
                    ttl = index.find('a',{'class':'slink'}).text
                    info_html = index.find_all('td',{'class':'std2'})
                    school = info_html[1].text.replace('\n','').strip()
                    author = info_html[2].text.replace('\n','').strip()
                    other_info = ''
                    for row in range(3,len(info_html)):
                        if row == 3:
                            other_info = other_info + info_html[row].text.replace('\n','').strip()
                        else:
                            if info_html[row].text.replace('\n','').strip() != '':
                                other_info = other_info + ';' + info_html[row].text.replace('\n','').strip()
                    result_list.append([ttl,school,author,other_info])
                result_df = pd.DataFrame(result_list)
                result_df.to_csv(survey + '_{}.csv'.format(page),sep=',',encoding='utf-8', header=None) #儲存結果
                if page < page_all:
                    time.sleep(10)
                    browser.find_element_by_name("gonext").click() #點選下一頁
                    
            
            with open(survey+'_main.csv', 'a', encoding='utf-8') as singleFile: #合併檔案
                for csv_file in glob(survey+'_*.csv'):
                    if csv_file == survey+'_main.csv':
                        pass
                    else:
                        for line in open(csv_file,'r',encoding='utf-8'):
                            singleFile.write(line)
            singleFile.close()

            filelog.write('{0}\t{1}\t{2}\n'.format(survey,date,page_int))

            column_names = ['index','title','inst','author','other']
            final_file = pd.read_csv(survey+'_main.csv', header = None, names = column_names) #搜尋結果檔
            final_file["cluster"] = survey #加上叢集名稱
            final_file.to_csv(survey+'_final.csv', header=False, index=False)
    except:
        filelog.close()
        browser.close()
        browser.quit()
        return

    browser.close() #關閉瀏覽器
    browser.quit() #退出驅動和關閉所有關聯視窗

    #匯出每個資料集搜尋下載筆數
    
    filelog.close()

    return