# -*- coding: utf-8 -*-
import json

import pandas as pd

from tools.getDataBase import get_conn


MOVIE_COLUMNS = [
    "id",
    "directors",
    "rate",
    "title",
    "casts",
    "cover",
    "year",
    "types",
    "country",
    "lang",
    "time",
    "movieTime",
    "commentLen",
    "star",
    "summary",
    "imgList",
    "detailLink",
]

VALID_MOVIE_TYPES = {
    "剧情",
    "喜剧",
    "动作",
    "爱情",
    "科幻",
    "动画",
    "悬疑",
    "惊悚",
    "恐怖",
    "犯罪",
    "同性",
    "音乐",
    "歌舞",
    "传记",
    "历史",
    "战争",
    "西部",
    "奇幻",
    "冒险",
    "灾难",
    "武侠",
    "情色",
    "家庭",
    "古装",
    "运动",
    "纪录片",
    "短片",
    "儿童",
    "真人秀",
    "脱口秀",
}


def safe_split(value, default=None):
    if default is None:
        default = []

    if value is None:
        return default.copy()

    if isinstance(value, list):
        return value

    value = str(value).strip()
    if value == "" or value.lower() in ["none", "null"]:
        return default.copy()

    try:
        if value.startswith("[") and value.endswith("]"):
            data = json.loads(value)
            if isinstance(data, list):
                return [str(item).strip() for item in data if str(item).strip()]
    except Exception:
        pass

    return [item.strip() for item in value.split(",") if item.strip()]


def _normalize_movie_row(row):
    item = list(row)

    item[1] = safe_split(item[1], ["无"])          # directors
    item[4] = safe_split(item[4], ["无"])          # casts
    item[7] = [
        movie_type
        for movie_type in safe_split(item[7], ["剧情"])
        if movie_type in VALID_MOVIE_TYPES
    ] or ["剧情"]                                  # types
    item[8] = safe_split(item[8], ["中国大陆"])    # country
    item[9] = safe_split(item[9], ["汉语普通话"])  # lang
    item[13] = safe_split(item[13], ["无"])        # star
    item[15] = safe_split(item[15], [])            # imgList

    return item


def getAllData():
    conn, cursor = get_conn()
    try:
        cursor.execute(
            """
            SELECT
                id, directors, rate, title, casts, cover, [year], types,
                country, lang, [time], movieTime, commentLen, star,
                summary, imgList, detailLink
            FROM dbo.movies
            ORDER BY id
            """
        )
        all_data = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return [_normalize_movie_row(row) for row in all_data]


def getDataFrame():
    return pd.DataFrame(getAllData(), columns=MOVIE_COLUMNS)


def getMaxRate():
    df = getDataFrame()
    rates = pd.to_numeric(df["rate"], errors="coerce").dropna()
    return float(rates.max()) if not rates.empty else 0


def getMinRate():
    df = getDataFrame()
    rates = pd.to_numeric(df["rate"], errors="coerce").dropna()
    return float(rates.min()) if not rates.empty else 0


def getMaxCast():
    all_data = getAllData()
    casts = {}
    max_name = ""
    max_num = 0

    for item in all_data:
        for cast in item[4]:
            if not cast or cast == "无":
                continue
            casts[cast] = casts.get(cast, 0) + 1

    for name, count in casts.items():
        if count > max_num:
            max_num = count
            max_name = name

    return max_name


def getMaxLang():
    all_data = getAllData()
    langs = {}
    max_lang = ""
    max_num = 0

    for item in all_data:
        for lang in item[9]:
            if not lang:
                continue
            langs[lang] = langs.get(lang, 0) + 1

    for lang, count in langs.items():
        if count > max_num:
            max_num = count
            max_lang = lang

    return max_lang


def getTypesAll():
    all_data = getAllData()
    types = {}

    for item in all_data:
        for movie_type in item[7]:
            if movie_type:
                types[movie_type] = types.get(movie_type, 0) + 1

    return types.keys()


def getType_t():
    all_data = getAllData()
    types = {}

    for item in all_data:
        for movie_type in item[7]:
            if movie_type:
                types[movie_type] = types.get(movie_type, 0) + 1

    return [{"name": name, "value": count} for name, count in types.items()]


def getRate_t():
    all_data = getAllData()
    rates = {}

    for item in all_data:
        rate = item[2]
        if rate is None or str(rate).strip() == "":
            continue
        rates[rate] = rates.get(rate, 0) + 1

    rates = dict(sorted(rates.items(), key=lambda item: float(item[0])))
    return rates.keys(), rates.values()


def getTableList():
    def map_fn(item):
        item = list(item)
        item[1] = "/".join(item[1])
        item[4] = "/".join(item[4])
        item[7] = "/".join(item[7])
        item[8] = "/".join(item[8])
        item[9] = "/".join(item[9])
        return item

    return [map_fn(item) for item in getAllData()]
