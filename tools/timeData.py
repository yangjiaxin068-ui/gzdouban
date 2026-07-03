from . import homeData
from datetime import datetime
import re


def getTimeList():
    df = homeData.getDataFrame()
    timeList = list(df['time'])
    cleanTimeList = []

    for date_str in timeList:
        if date_str is None or str(date_str).strip() == '':
            continue

        date_str = str(date_str).strip()

        try:
            # 只接受 yyyy-mm-dd
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            cleanTimeList.append(dt)
        except (ValueError, TypeError):
            # 如果格式不对，直接跳过
            continue

    # 排序
    cleanTimeList.sort()

    # 按年份统计
    timeData = {}
    for dt in cleanTimeList:
        year = str(dt.year)
        if timeData.get(year, -1) == -1:
            timeData[year] = 1
        else:
            timeData[year] += 1

    return list(timeData.keys()), list(timeData.values())


def getMovieTimeList():
    df = homeData.getDataFrame()
    movieTimeList = list(df['movieTime'])
    moveTimeDate = [
        {'name': '短', 'value': 0},     # <=80
        {'name': '中', 'value': 0},     # 81-120
        {'name': '长', 'value': 0},     # 121-150
        {'name': '特长', 'value': 0}    # >150
    ]

    for i in movieTimeList:
        if i is None or str(i).strip() == '':
            continue

        s = str(i).strip()

        # 提取数字，比如 "120分钟" -> 120
        match = re.search(r'\d+', s)
        if not match:
            continue

        try:
            t = int(match.group())
        except (ValueError, TypeError):
            continue

        if t <= 80:
            moveTimeDate[0]['value'] += 1
        elif t <= 120:
            moveTimeDate[1]['value'] += 1
        elif t <= 150:
            moveTimeDate[2]['value'] += 1
        else:
            moveTimeDate[3]['value'] += 1

    return moveTimeDate
