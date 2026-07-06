# -*- coding: utf-8 -*-
from pathlib import Path

import stylecloud
from PIL import ImageDraw

from tools.getDataBase import get_conn


BASE_DIR = Path(__file__).resolve().parents[1]
FONT_PATH = BASE_DIR / "static" / "font" / "simhei.ttf"
ALLOWED_MOVIE_FIELDS = {
    "title",
    "casts",
    "directors",
    "summary",
    "types",
    "country",
    "lang",
}
ALLOWED_COMMENT_FIELDS = {"commentContent"}


if not hasattr(ImageDraw.ImageDraw, "textsize"):
    def _textsize(self, text, font=None, *args, **kwargs):
        bbox = self.textbbox((0, 0), text, font=font, *args, **kwargs)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    ImageDraw.ImageDraw.textsize = _textsize


def _validate_field(field, allowed_fields):
    if field not in allowed_fields:
        raise ValueError(f"invalid field: {field}")
    return field


def _join_rows(rows):
    values = []
    for row in rows:
        value = row[0]
        if value is not None and str(value).strip():
            values.append(str(value))
    return ",".join(values)


def _make_word_cloud(text, icon_name, output_name, split_chars=False):
    if split_chars:
        text = ",".join(text)

    stylecloud.gen_stylecloud(
        text=text or "暂无数据",
        icon_name=icon_name,
        output_name=output_name,
        font_path=str(FONT_PATH),
    )


def getTitleImg(field, icon_name, output_name):
    field = _validate_field(field, ALLOWED_MOVIE_FIELDS)
    conn, cursor = get_conn()
    try:
        cursor.execute(f"SELECT {field} FROM dbo.movies")
        text = _join_rows(cursor.fetchall())
    finally:
        cursor.close()
        conn.close()

    _make_word_cloud(text, icon_name, output_name, split_chars=True)


def getCastsImg(field, icon_name, output_name):
    field = _validate_field(field, ALLOWED_MOVIE_FIELDS)
    conn, cursor = get_conn()
    try:
        cursor.execute(f"SELECT {field} FROM dbo.movies")
        text = _join_rows(cursor.fetchall())
    finally:
        cursor.close()
        conn.close()

    _make_word_cloud(text, icon_name, output_name)


def getCommentsImg(field, serchWord, icon_name, output_name):
    field = _validate_field(field, ALLOWED_COMMENT_FIELDS)
    search_word = str(serchWord or "").strip()
    if not search_word:
        return False

    conn, cursor = get_conn()
    try:
        cursor.execute(
            f"""
            SELECT {field}
            FROM dbo.comments
            WHERE REPLACE(REPLACE(movieName, '>', ''), NCHAR(160), '') LIKE ?
            """,
            f"%{search_word}%",
        )
        rows = cursor.fetchall()
        text = _join_rows(rows)
    finally:
        cursor.close()
        conn.close()

    if not text:
        return False

    _make_word_cloud(text, icon_name, output_name, split_chars=True)
    return True
