# -*- coding: utf-8 -*-
import random
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from lxml import etree


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tools.getDataBase import get_conn


headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/134.0.0.0 Safari/537.36"
    ),
    "Referer": "https://movie.douban.com/",
}

FETCH_DETAIL = True
COOKIE_FILE = BASE_DIR / "spider" / "douban_cookie.txt"
DETAIL_SLEEP_RANGE = (3, 6)
PAGE_SLEEP_RANGE = (8, 15)


def polite_sleep(label, sleep_range):
    seconds = random.uniform(*sleep_range)
    print(f"{label} sleep: {seconds:.1f}s")
    time.sleep(seconds)


def load_cookie():
    if not COOKIE_FILE.exists():
        return None

    cookie = COOKIE_FILE.read_text(encoding="utf-8").strip()
    return cookie or None


def build_headers(referer=None):
    request_headers = dict(headers)
    if referer:
        request_headers["Referer"] = referer

    cookie = load_cookie()
    if cookie:
        request_headers["Cookie"] = cookie

    return request_headers


def safe_first(items, default=None):
    return items[0] if items else default


def join_list(value):
    if isinstance(value, list):
        return ",".join([str(item) for item in value if item]) or None
    return value if value else None


def extract_info_field(info_block, field_name):
    if not info_block:
        return None

    info_html = str(info_block)
    pattern = rf'<span class="pl">{re.escape(field_name)}:</span>(.*?)(<br\s*/?>|</div>)'
    match = re.search(pattern, info_html, re.S)
    if not match:
        return None

    value_text = BeautifulSoup(match.group(1), "lxml").get_text(separator=" ", strip=True)
    value_text = re.sub(r"\s+", "", value_text).replace("/", ",")
    return value_text or None


def parse_detail_page(html_text):
    result = {
        "year": None,
        "types": None,
        "country": None,
        "lang": None,
        "time": None,
        "movieTime": None,
        "commentLen": None,
        "star": None,
        "summary": None,
        "imgList": None,
    }

    xpath_html = etree.HTML(html_text)
    soup = BeautifulSoup(html_text, "lxml")
    if xpath_html is None:
        return result

    year = safe_first(xpath_html.xpath('//span[@class="year"]/text()'))
    result["year"] = year.strip("()") if year else None

    types = xpath_html.xpath('//span[@property="v:genre"]/text()')
    result["types"] = ",".join(types) if types else None

    info_block = soup.find("div", id="info")
    result["country"] = extract_info_field(info_block, "\u5236\u7247\u56fd\u5bb6/\u5730\u533a")
    result["lang"] = extract_info_field(info_block, "\u8bed\u8a00")

    release_nodes = soup.find_all("span", property="v:initialReleaseDate")
    for release_node in release_nodes:
        match = re.search(r"\d{4}-\d{2}-\d{2}", release_node.get_text())
        if match:
            result["time"] = match.group()
            break

    runtime_node = soup.find("span", property="v:runtime")
    if runtime_node:
        runtime_match = re.search(r"\d+", runtime_node.get_text())
        result["movieTime"] = runtime_match.group() if runtime_match else None
    else:
        result["movieTime"] = str(random.randint(30, 100))

    comment_len = safe_first(xpath_html.xpath('//span[@property="v:votes"]/text()'))
    result["commentLen"] = comment_len if comment_len else None

    star_all = [
        item.strip()
        for item in xpath_html.xpath('//span[@class="rating_per"]/text()')
        if item.strip()
    ]
    result["star"] = ",".join(star_all) if star_all else None

    summary_node = soup.find("span", property="v:summary")
    if summary_node:
        summary_text = summary_node.get_text(separator=" ", strip=True)
        result["summary"] = re.sub(r"\s+", " ", summary_text) if summary_text else None

    img_list = xpath_html.xpath('//div[@id="related-pic"]/ul/li/a/img/@src')
    result["imgList"] = ",".join(img_list) if img_list else None

    return result


def update_not_empty(target, source):
    for key, value in source.items():
        if value is not None and value != "":
            target[key] = value


def spider_main(spider_target, page):
    params = {"start": page}
    result = []

    try:
        movies_all_res = requests.get(
            spider_target,
            params=params,
            headers=build_headers(),
            timeout=10,
            allow_redirects=False,
        )
        print("request api status:", movies_all_res.status_code)
        if movies_all_res.status_code in (302, 403):
            print("request blocked or redirected by server, stop crawling for now")
            return result
        movies_all_res.raise_for_status()
        movies_all = movies_all_res.json()
    except requests.RequestException as exc:
        print("request api failed:", exc)
        return result
    except ValueError as exc:
        print("api response is not valid json:", exc)
        return result

    movies_info = movies_all.get("data", [])
    if not movies_info:
        print("no movie data found")
        return result

    for movie_info in movies_info:
        result_data = {
            "directors": join_list(movie_info.get("directors")),
            "rate": movie_info.get("rate"),
            "title": movie_info.get("title"),
            "casts": join_list(movie_info.get("casts")),
            "cover": movie_info.get("cover"),
            "year": None,
            "types": None,
            "country": None,
            "lang": None,
            "time": None,
            "movieTime": None,
            "commentLen": None,
            "star": movie_info.get("star"),
            "summary": None,
            "imgList": None,
            "detailLink": movie_info.get("url"),
        }

        detail_url = movie_info.get("url")
        if FETCH_DETAIL and detail_url:
            try:
                detail_movie_res = requests.get(
                    detail_url,
                    headers=build_headers(spider_target),
                    timeout=10,
                    allow_redirects=False,
                )
                print("request detail status:", detail_movie_res.status_code, detail_url)
                if detail_movie_res.status_code in (302, 403):
                    print("detail request blocked or redirected, stop crawling:", detail_url)
                    result.append(result_data)
                    polite_sleep("blocked detail", PAGE_SLEEP_RANGE)
                    return result
                if detail_movie_res.status_code == 200:
                    detail_movie_res.encoding = (
                        detail_movie_res.apparent_encoding or detail_movie_res.encoding
                    )
                    detail_data = parse_detail_page(detail_movie_res.text)
                    update_not_empty(result_data, detail_data)
                    if not result_data["year"] and not result_data["summary"]:
                        print("detail page structure may be abnormal:", detail_url)
                else:
                    print("request detail failed, skip detail parse:", detail_url)
            except requests.RequestException as exc:
                print("request detail page failed:", detail_url, exc)

            polite_sleep("detail", DETAIL_SLEEP_RANGE)

        result.append(result_data)

    return result


def insert_movies(cursor, movies):
    sql_insert = """
        INSERT INTO dbo.movies (
            directors, rate, title, casts, cover, [year], types, country, lang, [time],
            movieTime, commentLen, star, summary, imgList, detailLink
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    for movie in movies:
        params = (
            movie["directors"],
            movie["rate"],
            movie["title"],
            movie["casts"],
            movie["cover"],
            movie["year"],
            movie["types"],
            movie["country"],
            movie["lang"],
            movie["time"],
            movie["movieTime"],
            movie["commentLen"],
            movie["star"],
            movie["summary"],
            movie["imgList"],
            movie["detailLink"],
        )

        try:
            cursor.execute(sql_insert, params)
        except Exception as exc:
            print(f'insert failed: {movie.get("title")} -> {exc}')


def main():
    conn, cursor = get_conn()
    spider_target = "https://movie.douban.com/j/new_search_subjects"

    try:
        for page in range(20):
            data = spider_main(spider_target, page * 20)
            if not data:
                print(f"page {page + 1} has no insertable data")
                continue

            insert_movies(cursor, data)
            conn.commit()
            print(f"page {page + 1} inserted: {len(data)}")
            polite_sleep("page", PAGE_SLEEP_RANGE)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
