# -*- coding: utf-8 -*-
from . import homeData


def _top20_count(values):
    count_data = {}
    for value_list in values:
        for value in value_list:
            if not value or value == "无":
                continue
            count_data[value] = count_data.get(value, 0) + 1

    top_data = sorted(count_data.items(), key=lambda item: item[1])[-20:]
    x = [item[0] for item in top_data]
    y = [item[1] for item in top_data]
    return x, y


def getAllActorMovieNum():
    allData = homeData.getAllData()
    return _top20_count([item[4] for item in allData])


def getAllDirectorMovieNum():
    allData = homeData.getAllData()
    return _top20_count([item[1] for item in allData])
