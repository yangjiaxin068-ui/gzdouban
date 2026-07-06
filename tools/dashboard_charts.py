# -*- coding: utf-8 -*-
import re
from pathlib import Path

import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Pie


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
    fragment = re.sub(r'\s*"hoverAnimation":\s*true,\n', "\n", fragment)

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
    output_path = HTML_DIR / filename
    chart.render(str(output_path))
    output_path.write_text(
        re.sub(r'\s*"hoverAnimation":\s*true,\n', "\n", output_path.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
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
            font_size=15,
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

    pie = Pie(init_opts=opts.InitOpts(height="100%", width="100%"))
    pie.add(
        "数量",
        pairs,
        radius=["42%", "70%"],
        center=["50%", "50%"],
        label_opts=opts.LabelOpts(formatter="{b}: {d}%", color="#0f0", font_size=16),
    )
    pie.set_global_opts(
        title_opts=opts.TitleOpts(title=""),
        tooltip_opts=opts.TooltipOpts(trigger="item", formatter="{b}: {c}部 ({d}%)"),
        legend_opts=opts.LegendOpts(
            pos_bottom="0",
            pos_left="center",
            textstyle_opts=opts.TextStyleOpts(color="#0f0", font_size=14),
        ),
    )
    pie.set_series_opts(
        itemstyle_opts=opts.ItemStyleOpts(border_color="#071d5f", border_width=2)
    )
    pie.set_colors(["#00f5ff", "#67e8f9", "#22c55e", "#facc15"])
    return _render_chart(pie, "lang_data.html")


def comment_chart():
    movies, counts = _read_count_csv("comment_counts.csv")
    display_movies = [
        f"{name[:6]}..." if len(name) > 6 else name
        for name in movies
    ]
    counts_in_wan = [round(count / 10000, 1) for count in counts]
    line = Line(init_opts=opts.InitOpts(height="100%", width="100%"))
    line.add_xaxis(display_movies)
    line.add_yaxis(
        "评论数量(万)",
        counts_in_wan,
        is_smooth=True,
        symbol="circle",
        symbol_size=8,
        label_opts=opts.LabelOpts(is_show=False),
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
            name="万条",
            name_textstyle_opts=opts.TextStyleOpts(color="#0f0"),
            axislabel_opts=opts.LabelOpts(color="#0f0", font_size=12, formatter="{value}"),
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
