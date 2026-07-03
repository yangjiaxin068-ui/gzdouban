import re
from numpy import *
from . import homeData


def getRate_tType(type):
    allData = homeData.getAllData()
    rateList = []
    rateForm = {}
    for i in allData:
        for j in i[7]:
            if type == j and i[2] is not None and str(i[2]).strip() != '':
                rateList.append(i[2])
    for i in rateList:
        if rateForm.get(i,-1) == -1:
            rateForm[i] = 1
        else:
            rateForm[i] = rateForm[i] + 1
    rateForm = dict(sorted(rateForm.items(), key=lambda item: float(item[0])))
    return rateForm.keys(),rateForm.values()

def getStart(movieName):
    df = homeData.getDataFrame()
    if df.empty:
        return [], ''

    matched = df.loc[df['title'].str.contains(movieName, na=False, regex=False)]
    starts = list(matched['star'])
    search_names = list(matched['title'])
    if not starts or not search_names:
        return [], ''

    searchName = search_names[0]
    startList =  [{
        'name':'五星',
        'value':0
    },{
        'name':'四星',
        'value':0
    },{
        'name': '三星',
        'value':0
    },{
        'name': '二星',
        'value':0
    },{
        'name':'一星',
        'value':0
    }]
    for i,s in enumerate(starts[0]):
        if i >= len(startList):
            break
        startList[i]['value'] = float(re.sub('%','',str(s)))
    return startList,searchName

def getCountryRating():
    allData = homeData.getAllData()
    data = [{
        'name':x,
        'count':0,
        'rating':[]
    } for x in ['中国','美国','英国','韩国','日本','法国','总和']]
    for i in allData:
        data[-1]['count'] = data[-1]['count'] + 1
        data[-1]['rating'].append(float(i[2]))
        for j in data:
            if i[8][0].find(j['name']) != -1:
                j['count'] = j['count'] + 1
                j['rating'].append(float(i[2]))
    x = []
    y = []
    y1 = []
    for i in data:
        i['rating'] = mean(i['rating']) if i['rating'] else 0
        x.append(i['name'])
        y.append(i['count'])
        y1.append(i['rating'])
    return x,y,y1

def getMean():
    allData = homeData.getAllData()
    meanDict = {}

    for i in allData:
        year = i[6]   # year
        rate = i[2]   # rate

        # 跳过空年份
        if year is None or str(year).strip() == '':
            continue

        # 跳过空评分
        if rate is None or str(rate).strip() == '':
            continue

        year = str(year).strip()

        try:
            rate = float(rate)
        except (TypeError, ValueError):
            continue

        if year not in meanDict:
            meanDict[year] = [rate]
        else:
            meanDict[year].append(rate)

    # 按年份排序
    meanList = sorted(meanDict.items(), key=lambda x: x[0])

    rows = []
    columns = []
    for year, rates in meanList:
        rows.append(year)
        columns.append(mean(rates))

    return rows, columns
