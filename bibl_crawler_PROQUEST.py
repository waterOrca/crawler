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

def CRAWLER_PROQUEST(driver_dir,target_dir,data):
    os.chdir(target_dir)

    dled_data = DOWNLOADED_DATA('Proquest',target_dir)

    filelog = open('Proquest_filelog.txt','a',encoding='utf-8')

    browser = webdriver.Chrome(driver_dir)
    browser.get('https://search.proquest.com/index')
    browser.maximize_window()


    for code in data:
        survey = code[0]
        keys = code[1]

        if survey in dled_data:
            continue

        browser.find_element_by_id("queryTermField").send_keys(keys)
        time.sleep(10)
        browser.find_element_by_id("searchToResultPage").click()
        time.sleep(20)

        soup = BeautifulSoup(browser.page_source, 'lxml')

        page_str = soup.find('h1', {'id':'pqResultsCount'})
        page_text = page_str.text
        pattern = "[0-9]+"
        page_re = re.findall(pattern, page_text)[0]
        page_int = int(page_re)
        page_all = (page_int // 100) + 1
        page_last = page_int % 100
        if page_last == 0:
            page_all = page_all - 1

        result_list = []
        

        for page in range(1,page_all+1):
            result_dic = {}
            soup = BeautifulSoup(browser.page_source, 'lxml')
            itemIndex = [tag.text for tag in soup.find_all('span', {'class':'indexing'})]
            itemIndexInt = []
            for i in range(0,len(itemIndex)):
                itemIndexInt.append(int(itemIndex[i]))
            for index in itemIndexInt:
                itemName = str('mldcopy{}'.format(index))
                soupItem = soup.find('div', {'id':itemName,'class':'results_list_copy'})
                soupTitle = soupItem.find('div', {"class":"truncatedResultsTitle"}).text.strip().replace("\n",'')
                result_dic.update({index:{'Title':soupTitle}})

                soupInfo = soupItem.find_all('span', {"class":"titleAuthorETC"})
                if len(soupInfo) > 1:
                    soupAuthor = soupInfo[0].text.strip().replace("\n",'')
                    soupJournal = soupInfo[1].text.strip().replace("\n",'')
                    result_dic[index].update({'Author':soupAuthor,'Journal':soupJournal})
                else:
                    result_dic[index].update({'Author':'None','Journal':'None'})
            
            
            result_page = open('{}_{}.txt'.format(survey,page),'w',encoding='utf-8')
            for row in result_dic:
                result_list.append([result_dic[row]['Title'],result_dic[row]['Author'],result_dic[row]['Journal']])
                result_page.write('{}\t{}\t{}\n'.format(result_dic[row]['Title'],result_dic[row]['Author'],result_dic[row]['Journal']))
            result_page.close()

            if page < page_all:
                time.sleep(5)
                browser.find_element_by_css_selector(u"a[title=\"下一頁\"] > span.hidden-xs").click()
                time.sleep(10)


        result_df = pd.DataFrame(result_list)
        result_df.columns = ['Title','Author','Journal']
        result_df['Survey'] = survey

        result_df.to_csv('{}_final.csv'.format(survey), header= False,index = False)

        filelog.write('{}\t{}\t{}\n'.format(survey,time.strftime("%y/%m/%d"),page_int))
        
        browser.find_element_by_link_text("進階檢索").click()
        time.sleep(10)
        browser.find_element_by_link_text("清除表單").click()
        time.sleep(10)

    
    browser.close() #關閉瀏覽器
    browser.quit() #退出驅動和關閉所有關聯視窗

    filelog.close()

    return