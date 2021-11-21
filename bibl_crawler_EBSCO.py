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

def CRAWLER_EBSCO(driver_dir,target_dir,data):
    os.chdir(target_dir)

    dled_data = DOWNLOADED_DATA('EBSCO',target_dir)

    filelog = open('EBSCO_filelog.txt','a',encoding='utf-8')

    browser = webdriver.Chrome(driver_dir)

    search_count = 0
    while search_count < 5:
        try:
            search_count +=1
            browser.get('http://search.ebscohost.com/login.asp?profile=ehost&defaultdb=lxh')
            browser.maximize_window()
            time.sleep(10)
            browser.find_element_by_id("selectDBLink").click()
            time.sleep(5)
            browser.find_element_by_id("selectAll").click()
            browser.find_element_by_id("btnOKTop").click()
            time.sleep(5)
            break
        except RequestException:
            browser.close() #關閉瀏覽器
            time.sleep(10)

    search_yr = int(time.strftime('%Y'))-1

    for code in data:
        survey = code[0]
        keys = code[1]

        if survey in dled_data:
            continue

        search_count = 0

        while search_count < 5:
            try:
                search_count +=1
                browser.find_element_by_id("Searchbox1").send_keys(keys)
                yr_filter_yn = YEAR_FILTER(survey)
                if yr_filter_yn == 1:
                    browser.find_element_by_id("common_DT1").click()
                    browser.find_element_by_xpath("//*[@id=\"common_DT1\"]/option[. = 'January']").click()
                    browser.find_element_by_id("common_DT1_FromYear").send_keys(str(search_yr-4))
                    browser.find_element_by_id("common_DT1_ToMonth").click()
                    browser.find_element_by_xpath("//*[@id=\"common_DT1_ToMonth\"]/option[. = 'December']").click()
                    browser.find_element_by_id("common_DT1_ToYear").send_keys(str(search_yr))
                time.sleep(5)
                browser.find_element_by_id("SearchButton").click()
                break
            except RequestException:
                browser.close() #關閉瀏覽器
                time.sleep(10)
                browser = webdriver.Chrome(driver_dir)
                browser.get('http://search.ebscohost.com/login.asp?profile=ehost&defaultdb=lxh')
                browser.maximize_window()
                time.sleep(10)
                browser.find_element_by_id("selectDBLink").click()
                time.sleep(5)
                browser.find_element_by_id("selectAll").click()
                browser.find_element_by_id("btnOKTop").click()
                time.sleep(5)


        soup = BeautifulSoup(browser.page_source, 'lxml')
        ini_result = soup.find('span',{'class':'smart-text-ran-warning'})
        if ini_result != None:
            filelog.write('{}\t{}\t{}\n'.format(survey,time.strftime("%y/%m/%d"),0))
            time.sleep(5)
            browser.find_element_by_id("advanced").click()
            time.sleep(10)
            browser.find_element_by_id("ClearButton").click()
            continue
        page_str = soup.find('h1', {'class':'page-title alt'})
        page_text = page_str.text
        pattern = '[0-9]+'
        page_re = re.findall(pattern, page_text)[2]
        page_int = int(page_re)
        page_all = (page_int // 50) + 1
        page_last = page_int % 50
        if page_last == 0:
            page_all = page_all - 1

        for page in range(1,page_all+1):
            result_list = []
            soup = BeautifulSoup(browser.page_source, 'lxml')
            page_str = soup.find('h1', {'class':'page-title alt'})
            page_text = page_str.text
            pattern = '[0-9]+'
            page_re2 = re.findall(pattern, page_text)[2]
            page_int2 = int(page_re2)
            ttl_list = soup.find_all('a',{'class':'title-link color-p4'})
            content_list = soup.find_all('div',{'class':'display-info'})
            for row in range(0,len(ttl_list)):
                title = ttl_list[row].text #標題
                content = content_list[row].text #作者、期刊名稱、頁數、DOI
                remove = content[content.find('Add to folder'):len(content)]
                content = ' '.join(content.replace(remove,"").replace("\n",'').split())
                db = content[content.find('Database: '):len(content)]
                info = content[0:content.find(', Database: ')]
                result_list.append([(page-1)*50+row+1,title,content,db,survey])
            result_df = pd.DataFrame(result_list)
            result_df.to_csv(survey+'_{}.csv'.format(page),sep=',',encoding='utf-8',header=False,index=False)
            
            if page_int == page_int2:
                if page < page_all:
                    browser.find_element_by_id("ctl00_ctl00_MainContentArea_MainContentArea_bottomMultiPage_lnkNext").click()
                    time.sleep(5)
                else:
                    filelog.write('{}\t{}\t{}\n'.format(survey,time.strftime("%y/%m/%d"),page_int))
            else:
                filelog.write('{}\t{}\t{}\n'.format(survey,time.strftime("%y/%m/%d"),page_int2))
                break

        time.sleep(5)
        browser.find_element_by_id("advanced").click()
        time.sleep(10)
        browser.find_element_by_id("ClearButton").click()
        time.sleep(5)
    
    browser.close() #關閉瀏覽器
    browser.quit() #退出驅動和關閉所有關聯視窗    

    filelog.close()

    return