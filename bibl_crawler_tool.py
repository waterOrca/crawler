#encoding: utf-8
import os
import pandas as pd
from os import path

#是否篩選年份
def YEAR_FILTER(survey):
    filter_yn = input("{} 是否加入年份篩選? (y/n)".format(survey))
    if filter_yn == 'Y' or filter_yn == 'y':
        return 1
    elif filter_yn == 'N' or filter_yn == 'n':
        return 0
    else:
        print("輸入錯誤")
        filter_yn = YEAR_FILTER()

def DOWNLOADED_DATA(source_name,target_dir):
    os.chdir(target_dir)
    if path.exists(source_name+'_filelog.txt') == True:
        data_file = open(source_name+'_filelog.txt','r',encoding='utf-8-sig')
        data = [line.split('\t') for line in data_file.read().splitlines()]
        data_df = pd.DataFrame(data)
        downloaded_data = list(data_df[0])
        data_file.close()
        return downloaded_data
    else:
        return []