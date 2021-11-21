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

#期刊論文索引系統
def CRAWLER_NCL_JOURNAL(driver_dir,target_dir,data):
    os.chdir(target_dir)

    #已下載資料
    dled_data = DOWNLOADED_DATA('ncl_journal',target_dir)

    filelog = open("ncl_journal_filelog.txt",'a',encoding='utf-8')
    browser = webdriver.Chrome(driver_dir) #指引chromedriver程式
    browser.get('http://readopac2.ncl.edu.tw/nclJournal/search/search_cmd.jsp?la=ch') #期刊論文索引系統指令搜尋頁面
    browser.maximize_window()


    try:
        for code in data:

            survey = code[0]
            keys = code[1]

            if survey in dled_data: #確認是否為已下載過的資料
                continue

            browser.find_element_by_id("textfield1").send_keys(keys) #輸入指令
            Select(browser.find_element_by_name("page_size")).select_by_visible_text("50") #每頁顯示50筆
            time.sleep(5)
            browser.find_element_by_class_name('btn').click() #搜尋

            soup = BeautifulSoup(browser.page_source, 'lxml') #擷取結果頁面


            #日期
            date = time.strftime('%y/%m/%d')

            check = soup.find('td',{'class':'center'}).text

            #無搜尋結果處理
            if '查無資料' in check:
                filelog.write("{0}\t{1}\t{2}\n".format(survey,date,0))
                time.sleep(10)
                browser.get('http://readopac2.ncl.edu.tw/nclJournal/search/search_cmd.jsp?la=ch')
                continue

            
            #頁數
            page_str = soup.find('em')

            #只有一筆搜尋結果處理(只有一筆搜尋結果會直接跳該筆搜尋結果詳目)
            if page_str == None:
                title = soup.find('div',{'class':'caption'}).text.strip().replace('\n','')
                info_html = soup.find('ul',{'class':'publishInfo'})
                info_list = info_html.find_all('li')
                journal = info_list[2].text.strip().replace('\n','')
                au = info_list[0].text.strip().replace('\n','')
                other_info = ''
                for row in range(3,len(info_list)):
                    content = info_list[row].text.strip().replace('\n','')
                    if row == 3:
                        other_info = content
                    else:
                        other_info = other_info + ';' + content
                data = [title,journal,au,other_info]
                data_df = pd.DataFrame(data).T
                data_df.to_csv(survey+'_1.csv', sep=',', encoding='utf-8', header=None)  #存成csv
                filelog.write("{0}\t{1}\t{2}\n".format(survey,date,1))
                browser.get('http://readopac2.ncl.edu.tw/nclJournal/search/search_cmd.jsp?la=ch')
                time.sleep(5)
                continue


            page_int = int(page_str.text) #結果筆數
            page_all = (page_int // 50) + 1 #結果頁數
            page_last = page_int % 50 #最後一頁筆數
            if page_last == 0:
                page_all = page_all - 1

            

            for page in range(1,page_all+1):
                soup = BeautifulSoup(browser.page_source, 'lxml') #擷取每頁頁面
                data_text1 = [tag.text for tag in soup.find_all('label', {"for":"checkbox1"})] #著作標題
                data_text2 = [tag for tag in soup.find_all('ul', {'class':'publishInfo'})] #著作其他資訊

                data_info = [] #著作其他資訊

                for tag in data_text2:
                    journal = tag.find('a').text.replace('\n','').strip() #期刊名稱 刪空行、前後空白
                    info_li = tag.find_all('li')
                    au = '' #作者
                    other_info = '' #其他資訊
                    for index in range(0,len(info_li)):
                        content = info_li[index].text.replace('\n','').strip()
                        if index <= 2:
                            if index == 0:
                                au = content #作者
                        elif index == 3:
                            other_info = content
                        else:
                            if content != '':
                                other_info = other_info + ';' + content
                    data_info.append([journal,au,other_info])

                    
                data_title = pd.DataFrame(data_text1)
                data_title.columns = ['Title'] #標題
                data_title = data_title.loc[:,'Title'].str.strip()
                data_info_df = pd.DataFrame(data_info) #其他資訊
                data_info_df.columns = ['Journal','Author','Other_Info']
                data_merge = pd.concat([data_title,data_info_df], axis = 1) #合併dataframe
                data_merge.to_csv(survey+'_{}.csv'.format(page), sep=',', encoding='utf-8', header=None)  #存成csv

                if page < page_all:
                    time.sleep(10)
                    browser.find_element_by_link_text(str(page+1)).click() #點選下一頁
                    time.sleep(5)

            filelog.write("{0}\t{1}\t{2}\n".format(survey,date,page_int))              

            with open(survey+'_main.csv','a',encoding='utf-8') as singleFile:
                for csv in glob(survey+'_*.csv'):
                    if csv == survey+'_main.csv':
                        pass
                    else:
                        for line in open(csv,'r', encoding='utf-8'):
                            singleFile.write(line)
            singleFile.close()
                
            column_names = ['index','Title','Journal','Author','Other_Info']
            final_file = pd.read_csv(survey+'_main.csv',header = None, names = column_names)
            final_file["cluster"] = survey
            final_file.to_csv(survey+'_final.csv', header=False, index=False)

            time.sleep(10)
            browser.find_element_by_css_selector("a:nth-child(4)").click() #回首頁
            browser.find_element_by_link_text("指令查詢").click() #點選進指令查詢頁面
    except:
        filelog.close()
        browser.close()
        browser.quit()
        return     

            
    browser.close() #關閉瀏覽器
    browser.quit() #退出驅動和關閉所有關聯視窗        
    
    filelog.close()

    return