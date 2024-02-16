import pandas as pd
from utility import *

def get_cell_indices(df, value):
    indices = []
    for index, row in df.iterrows():
        for col, val in enumerate(row):
            if val == value:
                indices.append([index, col])
    return indices

def parse_excel(uploaded_file):
    df_observer = pd.DataFrame()
    df = pd.read_excel(uploaded_file, header=None)

    if '★柏崎刈羽６号機　設工認ヒアリング　傍聴者リスト' in df.values:
        indices1 = get_cell_indices(df, 'ヒアリング日時：')
        if indices1:
            s_date = df.iloc[indices1[0][0], indices1[0][1] + 1]
            schedule_date = s_date.strftime("%Y年%m月%d日(%a)")
            s_time = str(df.iloc[indices1[0][0], indices1[0][1] + 2])
            schedule_time = normalize_time_format(s_time)
            
        indices2 = get_cell_indices(df, '中部電力株式会社')
        observer = ''
        if indices2:
            grp0 = ''
            for ind in range(len(indices2)):
                grp = df.iloc[indices2[ind][0], indices2[ind][1] + 1]
                if isinstance(grp, str): grp = grp.split()[-1]
                pst = df.iloc[indices2[ind][0], indices2[ind][1] + 2]
                obs = df.iloc[indices2[ind][0], indices2[ind][1] + 3]
                if isinstance(obs, str): obs = obs.split()[0]
                
                if not pd.isna(grp) and not pd.isna(pst) and not pd.isna(obs):
                    if observer == '':
                        observer = grp + ' ' + obs
                    else:
                        if grp0 == grp:
                            observer += ',' + obs
                        else:
                            observer += ',' + grp + ' ' + obs
                    grp0 = grp
                
        title = ''
        if indices1 and indices2 and observer.split():
            for row in range(indices1[0][0], indices2[0][0] - 1):
                t = df.iloc[row, indices1[0][1] + 3]
                if isinstance(t, str):
                    if '(' in t or '（' in t:
                        title +=  str(t)
                    else:
                        if title == '':
                            title = str(t)
                        else:
                            title += ',' + str(t)
                data_list = [schedule_date, schedule_time, title, observer]
                df_observer = pd.DataFrame([data_list], columns=['日付', '時間', '説明項目', '傍聴者'])
    return df_observer
    