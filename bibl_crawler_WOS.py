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



def CRAWLER_WOS(driver_dir,target_dir,data):
    os.chdir(target_dir)

    dled_data = DOWNLOADED_DATA('WOS',target_dir)

    filelog = open("WOS_filelog.txt",'a',encoding='utf-8')


    try:

        for code in data:

            survey = code[0]
            keys = code[1]

            if survey in dled_data:
                continue

            # 開啟chromedriver，連到目標網頁
            browser = webdriver.Chrome(driver_dir)
            browser.get('http://apps.webofknowledge.com/')
            time.sleep(5)
            browser.find_element_by_link_text("進階檢索").click()
            time.sleep(5)
            browser.find_element_by_id("value(input1)").clear()
            browser.find_element_by_id("value(input1)").send_keys(keys)
            time.sleep(5)
            browser.find_element_by_id("search-button").click()
            time.sleep(10)
            browser.find_element_by_id("hitCount").click()
            time.sleep(10)
            soup = BeautifulSoup(browser.page_source, 'lxml')
            page_result = soup.find('span', {'id':'hitCount.top'}).text
            page_int = int(page_result)
            page_all = (page_int // 10) + 1
            page_last = page_int % 10
            if page_last == 0:
                page_all = page_all - 1

            for page in range(1,page_all+1):
                result_list = []
                soup = BeautifulSoup(browser.page_source, 'lxml')
                numW1 = [tag.text for tag in soup.find_all('div', {'class':'search-results-number-align'})]
                numW2 = ''.join(numW1)
                pattern1 = '[0-9]+'
                num_list = re.findall(pattern1, numW2)
                for index in num_list:
                    #print(index)
                    recordW = soup.find('div', {'id':'RECORD_{}'.format(index)})
                    titleW = recordW.find('value', {'lang_id':''}).text.replace('\n','').strip()
                    authorW1 = [tag.text for tag in recordW.find_all('a', {'title':'尋找此作者的其他記錄'})]
                    authorW2 = ';'.join(authorW1)
                    journalW1 = recordW.find('a','smallV110 snowplow-JCRoverlay')
                    journalW2 = journalW1.find('value', {}).text
                    other_ttl = recordW.find_all('span',{'class':'label'})
                    other_cont = recordW.find_all('span',{'class':'data_bold'})
                    other_list = ''
                    if len(other_ttl) - len(other_cont) > 1:
                        for i in range(1,1+(len(other_ttl)-len(other_cont)-1)):
                            other_ttl.remove(other_ttl[i])
                    for i in range(1,len(other_ttl)):
                        other_list = other_list + other_ttl[i].text.strip().replace(' ','') + other_cont[i-1].text.strip().replace(" ",'') + ';'
                    other_list = other_list.strip()
                    result_list.append([titleW,authorW2,journalW2,other_list])
                result_df = pd.DataFrame(result_list)
                result_df.to_csv(survey+'_{}.csv'.format(page),sep=',', encoding='utf-8', header=None)
                if page < page_all:
                    time.sleep(5)
                    browser.find_element_by_css_selector("a.paginationNext.snowplow-navigation-nextpage-bottom > i").click()
                    time.sleep(10)
            
            filelog.write("{0}\t{1}\t{2}\n".format(survey,time.strftime("%y/%m/%d"),page_int))
            
            #併檔
            with open(survey+'_main.csv','a',encoding='utf-8') as singleFile:
                for csv in glob(survey+'_*.csv'):
                    if csv == survey+'_main.csv':
                        pass
                    else:
                        for line in open(csv,'r',encoding='utf-8'):
                            singleFile.write(line)
            singleFile.close()
            
            column_names = ['Title','Author','Journal','Other Information']
            final = pd.read_csv(survey+'_main.csv',header=None,names=column_names)
            final['Survey'] = survey
            final.to_csv(survey+'_final.csv',header = True, index = False)

            browser.close() #關閉瀏覽器
            time.sleep(10)
    except:
        filelog.close()
        return


    filelog.close()
    
    return