from pathlib import Path
import os
from datetime import datetime
import re


def get_file_times(file_path):
    try:
        stat_info = os.stat(file_path)
        ctime = datetime.fromtimestamp(stat_info.st_ctime)
        mtime = datetime.fromtimestamp(stat_info.st_mtime)
        return ctime, mtime

    except FileNotFoundError:
        print(f"ファイルが見つかりません: {file_path}")
        return None, None

def normalize_time_format(time_str):
    pattern = r'(\d{1,2}:\d{2})\s*～\s*(\d{1,2}:\d{2})'
    match = re.search(pattern, time_str)
    if match:
        start_time = match.group(1)
        end_time = match.group(2)
        return str(start_time) + ' ～ ' + str(end_time)
    else:
        return time_str

def get_excel_files(folder_path):
    excel_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.xlsx') or file.endswith('.xls'):
                if not str(file).startswith("~$"):
                    excel_files.append(os.path.join(root, file))
    return excel_files

def get_files(start_path, keyword=""):
    file_list = []
    start_path = Path(start_path)
    for file_path in start_path.rglob('*'):
        if file_path.is_file():
            if keyword is not None:
                if keyword in str(file_path):
                    file_list.append(file_path)
            else:
                file_list.append(file_path)
    return file_list
