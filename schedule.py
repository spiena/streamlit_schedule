import streamlit as st
#import pandas as pd
from datetime import datetime

from parse_pdf import *
from parse_excel import *
#from utility import *


schedule_path = r"\\Ps92h121\0005200本店　原子力本部　原子力部\ＢＦ対応\07 安全審査議事録\10 他社工認ヒア議事録\柏崎工認ヒアリング\柏崎６号機\100_スケジュール"
key_word_schedule = "KK6設工認ヒアリング週間予定表"

observer_path = r"\\Ps92h121\0005200本店　原子力本部　原子力部\ＢＦ対応\07 安全審査議事録\10 他社工認ヒア議事録\柏崎工認ヒアリング\柏崎６号機\200_傍聴希望者集約"

paper_path = r"\\Ps92h121\0005200本店　原子力本部　原子力部\ＢＦ対応\07 安全審査議事録\10 他社工認ヒア議事録\柏崎工認ヒアリング\柏崎６号機\300_ヒアリング資料(議事録を含む)"

schedule_list = []
df_observer = pd.DataFrame()


def index_of_schedule_list(num):
    ret = -1
    if schedule_list:
        for i in range(len(schedule_list)):
            s = schedule_list[i]
            if str(num) == str(s[0]):
                ret = i
    return ret

def get_summary(df):
    summary_list = df['説明項目'].dropna().tolist()
    ret = ''
    for s in summary_list:
        if ret == '': ret = str(s)
        else: ret += "，" + str(s)
    return ret

def get_observer(df):
    s_date = df['日付'][1]
    s_time = df['時間'][1]
    filtered_df = df_observer[(df_observer['日付'] == s_date) & (df_observer['時間'] == s_time)]
    if not filtered_df.empty:
        return filtered_df['傍聴者'].values[0]
    else:
        return '無し'


if __name__ == "__main__":
    
    st.header('柏崎刈羽６号機 設工認ヒアスケジュール')
    
    if st.button('更新'):
        slist = ['詳細', '一覧']
        tabs = st.tabs(slist)
    
        with tabs[0]:
            schedule_file_progress_bar = st.progress(0, 'ヒア情報処理')
            observer_file_progress_bar = st.progress(0, '傍聴者処理')
            
            schedule_files = get_files(schedule_path, keyword=key_word_schedule)
            for i in range(len(schedule_files)):
                f = schedule_files[i]
                schedule_file_progress_bar.progress((i + 1)/len(schedule_files), 'ヒア情報処理')
                ctime, mtime = get_file_times(f)
                
                data_list = parse_pdf(f, mtime)
                for d in data_list:
                    cur_count = d[0].loc[1, '回数']
                    ind = index_of_schedule_list(cur_count)
                    if ind != -1:
                        if mtime > schedule_list[ind][1]:
                            schedule_list[ind] = [cur_count, mtime, d[0], d[1]]
                    else:
                        schedule_list.append([cur_count, mtime, d[0], d[1]])
            
            df_observer = pd.DataFrame()
            observer_files = get_excel_files(observer_path)
            for i in range(len(observer_files)):
                f = observer_files[i]
                observer_file_progress_bar.progress((i + 1)/len(observer_files), '傍聴者処理')
                ctime, mtime = get_file_times(f)
                
                df_data = parse_excel(f)
                if not df_data.empty:
                    df_observer = pd.concat([df_observer, df_data], ignore_index=True)
            df_observer = df_observer.drop_duplicates()
    
            for s in schedule_list:
                df_header = s[2]
                st.write(df_header)
                with st.expander(get_summary(s[3])):
                    st.write('傍聴者： ' + get_observer(df_header))
                    st.write(s[3])
                st.markdown('<hr>', unsafe_allow_html=True)
                
        with tabs[1]:
            df_summary = pd.DataFrame()
            for s in schedule_list:
                df_header = s[2]
                title = get_summary(s[3])
                df_header.insert(3, '説明項目', title)
                df_summary = pd.concat([df_summary, df_header], ignore_index=True)
            df_summary = pd.merge(df_summary, df_observer, on=['日付', '時間'], how='left')
            st.write(df_summary)
            df_summary.to_csv('./output_data/スケジュール一覧.csv', encoding='utf-8', index=False)
            st.write('csvで出力しました。')
