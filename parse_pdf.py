import pdfplumber
import pandas as pd
from utility import *


def get_date(str_date, mdate):
    ind_month = str_date.find("月")
    cur_month = int(str_date[:ind_month])
    ind_day = str_date.find("日")
    cur_day = int(str_date[ind_month + 1:ind_day])
    if cur_month >= 4:
        cur_year = mdate.year
    else:
        if mdate.month >= 4:
            cur_year = mdate.year + 1
        else:
            cur_year = mdate.year
    cur_date = datetime(cur_year, cur_month, cur_day)
    return cur_date.strftime("%Y年%m月%d日(%a)")
    
def parse_pdf(uploaded_file, mdate):
    data_list = []

    with pdfplumber.open(uploaded_file) as pdf:
        num_pages = len(pdf.pages)
        df_main = pd.DataFrame()
        
        for page_num in range(num_pages):
            page = pdf.pages[page_num]
            tables = page.extract_tables()
            
            for i, table in enumerate(tables):
                df = pd.DataFrame(table, columns=[f'列{i}' for i in range(len(table[0]))])
                    
                if df['列0'][0] == '日程':
                    if not df_main.empty:
                        data_list.append([df_header, df_main])
                        df_main = pd.DataFrame()

                    df_header = df.iloc[:2].reset_index(drop=True)  #分割
                    df_header = df_header.dropna(axis=1, how='all') #Noneの列を削除
                    df_header.columns = df_header.iloc[0]           #index=0を列名に
                    df_header = df_header.iloc[1:]                  #index=0を削除
                    df_header = df_header.rename(
                        columns={
                            '日程': '日付',
                            'ヒアリング時間(予定)': '時間',
                        })

                    str_date = df_header['日付'][1]
                    cur_date = get_date(str_date, mdate)
                    df_header.loc[1, '日付'] = cur_date
                    
                    str_time = df_header['時間'][1]
                    cur_time = normalize_time_format(str_time)
                    df_header.loc[1, '時間'] = cur_time
                    
                    not_null_indices = df_header['時間'].notnull()
                    df_header.loc[not_null_indices, '時間'] = df_header.loc[not_null_indices, '時間'].astype(str)

                    df_main = df.iloc[2:].reset_index(drop=True)    #分割
                    df_main = df_main.dropna(axis=1, how='all')     #Noneの列を削除
                    df_main.columns = df_main.iloc[0]               #index=0を列名に
                    df_main = df_main.iloc[1:]                      #index=0を削除
                    
                elif df['列0'][0] == '説明項目':
                    df = df.dropna(axis=1, how='all')               #Noneの列を削除
                    df.columns = df.iloc[0]                         #index=0を列名に
                    df = df.iloc[1:]                                #index=0を削除
                    df_main = pd.concat([df_main, df], ignore_index=True)
                    
                else:                                               #記載不適箇所の処理
                    df.columns = df_main.columns
                    df_main = pd.concat([df_main, df], ignore_index=True)
    
        if not df_main.empty:
            data_list.append([df_header, df_main])
            df_main = pd.DataFrame()
            
    return data_list
    