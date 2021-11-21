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

def CRAWLER_AITIRI(driver_dir,target_dir,data):
    os.chdir(target_dir)

    dled_data = DOWNLOADED_DATA('airiti',target_dir)

    filelog = open('airiti_filelog.txt','a',encoding='utf-8')


    browser = webdriver.Chrome(driver_dir)
    browser.get('http://www.airitilibrary.com/')

    search_yr = int(time.strftime('%Y'))-1

    for code in data:
        survey = code[0]
        keys = code[1]

        if survey in dled_data:
            continue

        search_count = 0
        
        while search_count < 5:
            try:
                search_count += 1     
                browser.find_element_by_link_text("進階檢索").click()
                time.sleep(40)
                browser.find_element_by_id("editAlg").click()
                browser.find_element_by_id("Clear").click()
                browser.find_element_by_id("inquiryCondition").clear()
                browser.find_element_by_id("inquiryCondition").send_keys(keys)
                year_filter_yn = YEAR_FILTER(survey) #是否進行年份篩選 (今年-5年~今年)
                if year_filter_yn == 1:
                    time.sleep(5)
                    browser.find_element_by_id("Range_radio").click()
                    browser.find_element_by_id("RangeBegin_select").click()
                    browser.find_element_by_id(str(search_yr-4)).click()
                    browser.find_element_by_id("RangeEnd_select").click()
                    browser.find_element_by_id(str(search_yr)+'a').click()
                time.sleep(5)
                browser.find_element_by_id("PageSize50").click()
                browser.find_element_by_id("AdvancedResearchSubmit").click()
                break
            except RequestException:
                browser.close() #關閉瀏覽器
                time.sleep(10)
                browser = webdriver.Chrome(driver_dir)
                browser.get('http://www.airitilibrary.com/')
        

        category_all = ['期刊文章','會議論文','碩博士論文','電子書','紙本書']

        time.sleep(30)

        soup = BeautifulSoup(browser.page_source, 'lxml')
        category_list = soup.find('div',{'id':'menu'}).text

        for category in category_all:
            if category in category_list:
                browser.find_element_by_id(category).click()
                time.sleep(30)
                soup = BeautifulSoup(browser.page_source, 'lxml')
                checkRightSummary = soup.find('div', {'class':'rightSummary'}).text
                if checkRightSummary == '\n\n依下方條件來精確結果\n\n':
                    page_int = 0
                else:
                    page_str = soup.find('div', {'class':'txt1'})
                    if page_str == None:
                        filelog.write('{}\t{}\t{}\t{}\n'.format(survey,time.strftime("%y/%m/%d"),category,0))
                        continue
                    page_text = page_str.text
                    pattern = '[0-9]+'
                    page_re = re.findall(pattern, page_text)[0]
                    page_int = int(page_re)
                    page_all = (page_int // 50) + 1
                    page_last = page_int % 50
                    if page_last == 0:
                        page_all = page_all - 1
                if page_int == 0:
                    filelog.write('{}\t{}\t{}\t{}\n'.format(survey,time.strftime("%y/%m/%d"),category,0))
                    continue
                for page in range(1,page_all+1):
                    soup = BeautifulSoup(browser.page_source, 'lxml')
                    page_len = soup.find_all('td', {"class":"titleB"})
                    pName_list = []
                    current = 0
                    for current in range(len(page_len)):
                        pName_text = soup.find_all('td', {"class":"titleB"})[current].find('a').text
                        pName_list.append(pName_text.replace("\n",''))
                    pName_all = [tag.text for tag in soup.find_all('td', {"class":"titleB"})]
                    for index in range(0,len(pName_all)):
                        row = ' '.join(pName_all[index].split())
                        row = re.sub(r'\n+', '\n', row).strip().replace('\n',' ')
                        pName_all[index] = row
                    pName_list_df = pd.DataFrame(pName_list)
                    pName_list_df.columns=["title"]
                    pName_all_df = pd.DataFrame(pName_all)
                    pName_all_df.columns=["all"]
                    pName_all_df = pName_all_df.loc[:,'all'].str.strip()
                    #併檔
                    pName_merge = pd.concat([pName_list_df, pName_all_df], axis=1)
                    pName_merge['system'] = "華藝線上"
                    pName_merge['category'] = category
                    pName_merge['cluster'] = survey
                    pName_merge.to_csv('{}_{}_{}.csv'.format(survey, category, page), sep=',', encoding='utf-8', header=None)
                    if page < page_all:
                        browser.find_element_by_id("imgNext").click()
                        time.sleep(10)
            filelog.write('{}\t{}\t{}\t{}\n'.format(survey,time.strftime("%y/%m/%d"),category,page_int))
        
        with open(survey+'_main.csv','a',encoding='utf-8') as singleFile:
            for csv in glob(survey+'_*.csv'):
                if csv == survey + '_main.csv':
                    pass
                else:
                    for line in open(csv,'r',encoding = 'utf-8'):
                        singleFile.write(line)
        singleFile.close()
    
    browser.close() #關閉瀏覽器
    browser.quit() #退出驅動和關閉所有關聯視窗

    filelog.close()

    return