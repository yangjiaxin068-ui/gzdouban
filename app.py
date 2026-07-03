# -*- coding: utf-8 -*-
from flask import Flask, redirect, render_template, request, session, url_for

from tools.actor import *
from tools.addressData import *
from tools.getDataBase import get_conn
from tools.homeData import *
from tools.rateData import *
from tools.timeData import *
from tools.typeData import *


app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "ywqqq"


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
def home():
    if "username" not in session:
        return redirect(url_for("login"))

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


@app.route("/search/<int:searchId>", methods=["GET", "POST"])
def search(searchId):
    if "username" not in session:
        return redirect(url_for("login"))

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
def time_t():
    if "username" not in session:
        return redirect(url_for("login"))

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
def rate_t(type):
    if "username" not in session:
        return redirect(url_for("login"))

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
def address_t():
    if "username" not in session:
        return redirect(url_for("login"))

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
def type_t():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    result = getMovieTypeData()
    data = sorted(result, key=lambda item: item["value"], reverse=True)
    top10Data = data[:10]

    return render_template("type_t.html", username=username, top10Data=top10Data)


@app.route("/actor_t")
def actor_t():
    if "username" not in session:
        return redirect(url_for("login"))

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


if __name__ == "__main__":
    app.run(debug=True, port=9898)
