# -*- coding: utf-8 -*-
import re
from pathlib import Path

import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Bar, Grid, Line, Liquid, Pie


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "tools" / "data"
HTML_DIR = BASE_DIR / "static" / "html"


def _clean_label(value):
    if pd.isna(value):
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    text = str(value).strip()
    return text[:-2] if text.endswith(".0") else text


def _read_count_csv(filename):
    df = pd.read_csv(DATA_DIR / filename, encoding="utf-8")
    if df.shape[1] < 2:
        raise ValueError(f"{filename} 至少需要两列数据")

    names = [_clean_label(value) for value in df.iloc[:, 0]]
    counts = pd.to_numeric(df.iloc[:, 1], errors="coerce").fillna(0)
    counts = [int(value) if float(value).is_integer() else float(value) for value in counts]
    return names, counts


def _normalize_chart_fragment(html_text):
    body_match = re.search(r"<body[^>]*>(.*?)</body>", html_text, re.I | re.S)
    fragment = body_match.group(1) if body_match else html_text
    fragment = re.sub(
        r'class="chart-container"\s+style="[^"]*"',
        'class="chart-container" style="width:100%; height:100%;"',
        fragment,
    )

    chart_names = re.findall(r"var\s+(chart_[a-zA-Z0-9_]+)\s*=", fragment)
    if chart_names:
        resize_calls = "\n".join(f"{name}.resize();" for name in chart_names)
        fragment += f"""
        <script>
            window.addEventListener("resize", function () {{
                {resize_calls}
            }});
            setTimeout(function () {{
                {resize_calls}
            }}, 100);
        </script>
        """

    return fragment


def chart_from_file(filename):
    return _normalize_chart_fragment((HTML_DIR / filename).read_text(encoding="utf-8"))


def _render_chart(chart, filename):
    chart.render(str(HTML_DIR / filename))
    return _normalize_chart_fragment(chart.render_embed())


def type_chart():
    names, counts = _read_count_csv("type_counts.csv")
    pie = Pie(init_opts=opts.InitOpts(height="100%", width="100%"))
    pie.add(
        "数量",
        list(zip(names, counts)),
        radius=["30%", "60%"],
        label_opts=opts.LabelOpts(
            formatter="{b}:{c}个",
            font_size=16,
            font_style="bold",
            color="#0f0",
        ),
    )
    pie.set_global_opts(
        title_opts=opts.TitleOpts(title=""),
        tooltip_opts=opts.TooltipOpts(axis_pointer_type="shadow"),
        legend_opts=opts.LegendOpts(
            textstyle_opts=opts.TextStyleOpts(font_size=16, color="#0f0")
        ),
    )
    return _render_chart(pie, "type_data.html")


def year_chart():
    years, counts = _read_count_csv("year_counts.csv")
    bar = Bar(init_opts=opts.InitOpts(height="100%", width="100%"))
    bar.add_xaxis(years)
    bar.add_yaxis("数量", counts)
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title=""),
        xaxis_opts=opts.AxisOpts(
            name="年份",
            name_textstyle_opts=opts.TextStyleOpts(color="#0f0"),
            axislabel_opts=opts.LabelOpts(color="#0f0", font_size=12),
            name_location="middle",
            name_gap=25,
        ),
        yaxis_opts=opts.AxisOpts(
            name="数量",
            name_textstyle_opts=opts.TextStyleOpts(color="#0f0"),
            axislabel_opts=opts.LabelOpts(color="#0f0", font_size=12),
            name_location="middle",
            name_gap=25,
        ),
        legend_opts=opts.LegendOpts(
            pos_left="center",
            textstyle_opts=opts.TextStyleOpts(color="#0f0"),
        ),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
    )
    bar.set_series_opts(
        itemstyle_opts=opts.ItemStyleOpts(color="#0ff"),
        label_opts=opts.LabelOpts(color="#000", font_size=12, rotate=45),
    )
    return _render_chart(bar, "year_data.html")


def lang_chart():
    languages, counts = _read_count_csv("lang_counts.csv")
    pairs = [(name, count) for name, count in zip(languages, counts) if name]
    if not pairs:
        pairs = [("暂无", 0)]

    total = sum(count for _, count in pairs) or 1
    while len(pairs) < 2:
        pairs.append(("", 0))

    first_name, first_count = pairs[0]
    second_name, second_count = pairs[1]

    first = Liquid(init_opts=opts.InitOpts(height="100%", width="100%"))
    first.add(
        "占比",
        [first_count / total],
        center=["25%", "50%"],
        color=["#0f0"],
        is_outline_show=False,
        shape="pin",
        label_opts=opts.LabelOpts(font_size=32),
    )
    first.set_global_opts(
        title_opts=opts.TitleOpts(
            title=first_name[:2],
            pos_left="20%",
            pos_top="5%",
            title_textstyle_opts=opts.TextStyleOpts(color="#0f0"),
        )
    )

    second = Liquid(init_opts=opts.InitOpts(height="100%", width="100%"))
    second.add(
        "占比",
        [second_count / total],
        center=["70%", "50%"],
        color=["#0f0"],
        is_outline_show=False,
        shape="pin",
        label_opts=opts.LabelOpts(font_size=32),
    )
    second.set_global_opts(
        title_opts=opts.TitleOpts(
            title=second_name[:2],
            pos_left="65%",
            pos_top="5%",
            title_textstyle_opts=opts.TextStyleOpts(color="#0f0"),
        )
    )

    grid = Grid(init_opts=opts.InitOpts(height="100%", width="100%"))
    grid.add(first, grid_opts=opts.GridOpts())
    grid.add(second, grid_opts=opts.GridOpts())
    return _render_chart(grid, "lang_data.html")


def comment_chart():
    movies, counts = _read_count_csv("comment_counts.csv")
    line = Line(init_opts=opts.InitOpts(height="100%", width="100%"))
    line.add_xaxis(movies)
    line.add_yaxis(
        "评论数量",
        counts,
        is_smooth=True,
        symbol="circle",
        symbol_size=8,
        label_opts=opts.LabelOpts(color="#0f0", font_size=12),
        linestyle_opts=opts.LineStyleOpts(color="#0ff", width=3),
        itemstyle_opts=opts.ItemStyleOpts(color="#0ff"),
    )
    line.set_global_opts(
        title_opts=opts.TitleOpts(title=""),
        xaxis_opts=opts.AxisOpts(
            name="电影",
            name_textstyle_opts=opts.TextStyleOpts(color="#0f0"),
            axislabel_opts=opts.LabelOpts(color="#0f0", font_size=12, rotate=20),
            name_location="middle",
            name_gap=35,
        ),
        yaxis_opts=opts.AxisOpts(
            name="数量",
            name_textstyle_opts=opts.TextStyleOpts(color="#0f0"),
            axislabel_opts=opts.LabelOpts(color="#0f0", font_size=12),
            name_location="middle",
            name_gap=45,
        ),
        legend_opts=opts.LegendOpts(
            pos_left="center",
            textstyle_opts=opts.TextStyleOpts(color="#0f0"),
        ),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
    )
    return _render_chart(line, "comment_data.html")
