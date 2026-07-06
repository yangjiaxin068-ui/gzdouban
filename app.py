# -*- coding: utf-8 -*-
import requests
from flask import Flask, Response, redirect, render_template, request, session, url_for
from functools import wraps
from pathlib import Path
import re

from tools.actor import getAllActorMovieNum, getAllDirectorMovieNum
from tools.addressData import getAddressData, getLangData
from tools.dashboard_charts import comment_chart, lang_chart, type_chart, year_chart
from tools.getData import mainFun
from tools.getDataBase import get_conn
from tools.homeData import (
    getAllData,
    getMaxCast,
    getMaxLang,
    getMaxRate,
    getRate_t,
    getTableList,
    getType_t,
    getTypesAll,
    safe_split,
)
from tools.rateData import getCountryRating, getMean, getRate_tType, getStart
from tools.timeData import getMovieTimeList, getTimeList
from tools.typeData import getMovieTypeData
from tools.word_cloud import getCastsImg, getCommentsImg, getTitleImg


app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "ywqqq"
BASE_DIR = Path(__file__).resolve().parent
COVER_CACHE_DIR = BASE_DIR / "static" / "images" / "covers"


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped_view


def extract_douban_image_cookies(html_text):
    status_parts = re.findall(r"(?:WTKkN|bOYDu|wyeCN)\s*:\s*(\d+)", html_text)
    bot_match = re.search(r"\(t,\s*(\d{8,})\)", html_text)
    if len(status_parts) < 3 or not bot_match:
        return None

    status_value = sum(int(value) for value in status_parts)
    return f"__tst_status={status_value}#; EO_Bot_Ssid={bot_match.group(1)}"


def is_valid_jpeg(content):
    return content.startswith(b"\xff\xd8") and len(content) > 1024


def fetch_douban_cover(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/134.0.0.0 Safari/537.36"
        ),
        "Referer": "https://movie.douban.com/",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    }

    response = requests.get(url, headers=headers, timeout=10)
    if is_valid_jpeg(response.content):
        return response.content

    cookie = extract_douban_image_cookies(response.text)
    if not cookie:
        response.raise_for_status()
        return response.content if is_valid_jpeg(response.content) else None

    headers["Cookie"] = cookie
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.content if is_valid_jpeg(response.content) else None


def serve_cached_douban_image(cache_name, image_urls):
    cache_path = COVER_CACHE_DIR / cache_name
    if cache_path.exists():
        return Response(cache_path.read_bytes(), mimetype="image/jpeg")

    image_content = None
    for image_url in image_urls:
        if not image_url:
            continue
        try:
            image_content = fetch_douban_cover(image_url)
        except requests.RequestException:
            image_content = None
        if image_content:
            break

    if not image_content:
        return Response(status=404)

    COVER_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(image_content)
    return Response(image_content, mimetype="image/jpeg")


@app.route("/")
def rootRoute():
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        password_checked = request.form.get("passwordCheked", "").strip()

        if not username or not password:
            return redirect(url_for("register"))

        if password != password_checked:
            return "<h1>两次密码不一致！！</h1>"

        conn, cursor = get_conn()
        try:
            cursor.execute("SELECT username FROM dbo.users WHERE username = ?", username)
            user = cursor.fetchone()

            if user:
                return "<h1>用户名已存在！！</h1>"

            cursor.execute(
                "INSERT INTO dbo.users (username, password) VALUES (?, ?)",
                username,
                password,
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            return redirect(url_for("login"))

        conn, cursor = get_conn()
        try:
            cursor.execute(
                """
                SELECT id, username
                FROM dbo.users
                WHERE username = ? AND password = ?
                """,
                username,
                password,
            )
            user = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        if user:
            session["username"] = username
            return redirect(url_for("home"))

        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/home")
@login_required
def home():
    username = session["username"]
    allData = getAllData()
    dataLen = len(allData)
    maxRate = getMaxRate()
    maxCast = getMaxCast()
    typeAll = list(getTypesAll())
    maxLang = getMaxLang()
    types = getType_t()
    x, y = getRate_t()

    return render_template(
        "home.html",
        username=username,
        dataLen=dataLen,
        maxRate=maxRate,
        maxCast=maxCast,
        typeAll=len(typeAll),
        maxLang=maxLang,
        types=types,
        x=list(x),
        y=list(y),
    )


@app.route("/analysis1", methods=["GET", "POST"])
@login_required
def index():
    allData = getAllData()
    allData = len(allData)
    maxRate = getMaxRate()
    typeAll = getTypesAll()
    typeAll = len(typeAll)
    maxLang = getMaxLang()[:2]
    country_x, country_y = getAddressData()
    country_pairs = sorted(
        zip(country_x, country_y),
        key=lambda item: item[1],
        reverse=True,
    )[:10]
    data = {
        "allData": allData,
        "maxRate": maxRate,
        "typeAll": typeAll,
        "maxLang": maxLang,
    }
    return render_template(
        "analysis.html",
        username=session["username"],
        data=data,
        chart_html1=type_chart(),
        chart_html2=year_chart(),
        chart_html3=lang_chart(),
        chart_html4=comment_chart(),
        country_data=[
            {"name": name, "value": value}
            for name, value in country_pairs
        ],
    )


@app.route("/search/<int:searchId>", methods=["GET", "POST"])
@login_required
def search(searchId):
    username = session["username"]
    allData = getAllData()
    data = []

    if request.method == "GET":
        if searchId == 0:
            return render_template("search.html", username=username, data=data)

        for item in allData:
            if item[0] == searchId:
                data.append(item)

        return render_template("search.html", username=username, data=data)

    searchWord = request.form.get("searchIpt", "").strip()
    if not searchWord:
        return redirect(url_for("search", searchId=searchId))

    data = [item for item in allData if searchWord in item[3]]
    return render_template("search.html", username=username, data=data)


@app.route("/time_t")
@login_required
def time_t():
    username = session["username"]
    x, y = getTimeList()
    movieTimeData = getMovieTimeList()

    return render_template(
        "time_t.html",
        username=username,
        x=list(x),
        y=list(y),
        movieTimeData=movieTimeData,
    )


@app.route("/rate_t/<type>", methods=["GET", "POST"])
@login_required
def rate_t(type):
    username = session["username"]
    typeAll = list(getTypesAll())

    if type == "all":
        x, y = getRate_t()
    else:
        x, y = getRate_tType(type)

    if request.method == "GET":
        star, movieName = getStart("")
    else:
        searchWord = request.form.get("searchIpt", "").strip()
        if not searchWord:
            return redirect(url_for("rate_t", type=type))
        star, movieName = getStart(searchWord)
        if not star:
            return redirect(url_for("rate_t", type=type))

    x1, y1 = getMean()
    y1 = [round(y1_val, 2) for y1_val in y1]
    x2, y2, y22 = getCountryRating()
    y22 = [round(y_val, 2) for y_val in y22]

    return render_template(
        "rate_t.html",
        username=username,
        type=type,
        x=list(x),
        y=list(y),
        star=star,
        movieName=movieName,
        x1=x1,
        y1=y1,
        x2=x2,
        y2=y2,
        y22=y22,
        typeAll=typeAll,
    )


@app.route("/address_t")
@login_required
def address_t():
    username = session["username"]
    x, y = getAddressData()
    x1, y1 = getLangData()

    return render_template(
        "address_t.html",
        username=username,
        x=list(x),
        y=list(y),
        x1=list(x1),
        y1=list(y1),
    )


@app.route("/type_t")
@login_required
def type_t():
    username = session["username"]
    result = getMovieTypeData()
    data = sorted(result, key=lambda item: item["value"], reverse=True)
    top10Data = data[:10]

    return render_template("type_t.html", username=username, top10Data=top10Data)


@app.route("/actor_t")
@login_required
def actor_t():
    username = session["username"]
    x, y = getAllDirectorMovieNum()
    x1, y1 = getAllActorMovieNum()

    return render_template(
        "actor_t.html",
        username=username,
        x=list(x),
        y=list(y),
        x1=list(x1),
        y1=list(y1),
    )


@app.route("/tables/<int:id>")
@login_required
def tables(id):
    username = session["username"]
    tablelist = []
    if id == 0:
        tablelist = getTableList()

    return render_template("tables.html", username=username, tablelist=tablelist)


@app.route("/cover/<int:movie_id>")
def movie_cover(movie_id):
    conn, cursor = get_conn()
    try:
        cursor.execute("SELECT cover FROM dbo.movies WHERE id = ?", movie_id)
        row = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if not row or not row[0]:
        return Response(status=404)

    return serve_cached_douban_image(f"{movie_id}.jpg", [row[0]])


@app.route("/movie_image/<int:movie_id>/<int:image_index>")
def movie_image(movie_id, image_index):
    conn, cursor = get_conn()
    try:
        cursor.execute("SELECT imgList, cover FROM dbo.movies WHERE id = ?", movie_id)
        row = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if not row:
        return Response(status=404)

    image_urls = safe_split(row[0], [])
    image_url = image_urls[image_index] if 0 <= image_index < len(image_urls) else row[1]
    return serve_cached_douban_image(f"{movie_id}_{image_index}.jpg", [image_url, row[1]])


@app.route("/title_c")
@login_required
def title_c():
    username = session["username"]
    output_path = BASE_DIR / "static" / "images" / "title.png"
    getTitleImg("title", "fas fa-heart", str(output_path))
    return render_template("title_c.html", username=username)


@app.route("/casts_c")
@login_required
def casts_c():
    username = session["username"]
    output_path = BASE_DIR / "static" / "images" / "casts.png"
    getCastsImg("casts", "fab fa-apple", str(output_path))
    return render_template("casts_c.html", username=username)


@app.route("/comments_c", methods=["GET", "POST"])
@login_required
def comments_c():
    username = session["username"]
    if request.method == "GET":
        return render_template("comments_c.html", username=username)

    searchWord = request.form.get("searchIpt", "").strip()
    if not searchWord:
        return redirect(url_for("comments_c"))

    try:
        output_path = BASE_DIR / "static" / "images" / "comments.png"
        has_data = getCommentsImg("commentContent", searchWord, "fab fa-qq", str(output_path))
        if not has_data:
            return redirect(url_for("comments_c"))
    except Exception:
        return redirect(url_for("comments_c"))

    return render_template("comments_c.html", username=username)


if __name__ == "__main__":
    with app.app_context():
        mainFun()
    app.run(debug=True, port=9898)
