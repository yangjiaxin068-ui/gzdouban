# -*- coding: utf-8 -*-
import random
import re
import sys
import time
from pathlib import Path

import requests
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

MAX_MOVIES = None
MAX_PAGES = 2
REVIEW_PAGE_SLEEP_RANGE = (5, 9)
MOVIE_SLEEP_RANGE = (10, 18)
CLEAR_OLD_COMMENTS = True
COOKIE_FILE = BASE_DIR / "spider" / "douban_cookie.txt"


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


def get_movies_id():
    conn, cursor = get_conn()
    try:
        cursor.execute(
            """
            SELECT title, detailLink
            FROM dbo.movies
            WHERE detailLink IS NOT NULL
              AND detailLink <> ''
            ORDER BY id
            """
        )
        data = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    movie_list = []
    for title, detail_link in data:
        match = re.search(r"/subject/(\d+)/", detail_link or "")
        if match:
            movie_list.append({"title": title, "movie_id": match.group(1)})
    return movie_list


def clean_comment(text):
    return (
        text.strip()
        .replace("\n", "")
        .replace("(", "")
        .replace(")", "")
        .replace(" ", "")
    )


def parse_review_page(html_text, default_movie_name=None):
    xpath_html = etree.HTML(html_text)
    if xpath_html is None:
        return default_movie_name, []

    movie_names = xpath_html.xpath('//div[@class="subject-title"]/a/text()')
    if movie_names:
        movie_name = movie_names[0].strip().strip("\u300a\u300b")
    else:
        movie_name = default_movie_name

    comments = []
    divs = xpath_html.xpath('//div[contains(@class, "review-list")]/div')
    for div in divs:
        contents = div.xpath('.//div[@class="short-content"]/text()')
        if not contents:
            continue

        content_data = clean_comment(contents[0])
        if content_data:
            comments.append(content_data)

    return movie_name, comments


def insert_comments(cursor, movie_name, comments):
    sql_insert = """
        INSERT INTO dbo.comments (movieName, commentContent)
        VALUES (?, ?)
    """
    for content in comments:
        try:
            cursor.execute(sql_insert, (movie_name, content))
        except Exception as exc:
            print(f"insert comment failed: {movie_name} -> {exc}")


def clear_old_comments(cursor):
    try:
        cursor.execute("TRUNCATE TABLE dbo.comments")
    except Exception:
        cursor.execute("DELETE FROM dbo.comments")


def spider_main(max_movies=MAX_MOVIES, max_pages=MAX_PAGES):
    conn, cursor = get_conn()
    movie_list = get_movies_id()
    inserted_count = 0
    selected_movies = movie_list if max_movies is None else movie_list[:max_movies]

    if CLEAR_OLD_COMMENTS:
        clear_old_comments(cursor)
        conn.commit()
        print("old comments cleared")

    print(f"movies available for comments: {len(movie_list)}")
    print(f"movies this run: {len(selected_movies)}, review pages per movie: {max_pages}")

    try:
        for movie in selected_movies:
            movie_id = movie["movie_id"]
            default_movie_name = movie["title"]

            for page in range(max_pages):
                base_url = f"https://movie.douban.com/subject/{movie_id}/reviews?start={page * 20}"
                referer_url = f"https://movie.douban.com/subject/{movie_id}/"

                try:
                    response = requests.get(
                        base_url,
                        headers=build_headers(referer_url),
                        timeout=10,
                        allow_redirects=False,
                    )
                except requests.RequestException as exc:
                    print("request review page failed:", base_url, exc)
                    break

                print("review url status:", response.status_code, base_url)
                if response.status_code in (302, 403):
                    print("review request blocked or redirected by server, stop crawling")
                    polite_sleep("blocked review", MOVIE_SLEEP_RANGE)
                    return inserted_count
                if response.status_code != 200:
                    polite_sleep("review retry", REVIEW_PAGE_SLEEP_RANGE)
                    continue

                response.encoding = response.apparent_encoding or response.encoding
                movie_name, comments = parse_review_page(response.text, default_movie_name)
                if movie_name and comments:
                    insert_comments(cursor, movie_name, comments)
                    conn.commit()
                    inserted_count += len(comments)
                    print(f"inserted comments: {movie_name} {len(comments)}")
                else:
                    print("no comments parsed:", base_url)

                polite_sleep("review page", REVIEW_PAGE_SLEEP_RANGE)

            polite_sleep("movie", MOVIE_SLEEP_RANGE)
    finally:
        cursor.close()
        conn.close()

    return inserted_count


if __name__ == "__main__":
    count = spider_main()
    print("total inserted comments:", count)
