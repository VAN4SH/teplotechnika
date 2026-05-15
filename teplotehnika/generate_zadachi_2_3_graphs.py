from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent


SAT_LIQ = [
    (0.3543, 101.0),
    (0.5209, 151.5),
    (0.6492, 191.8),
    (0.8320, 251.4),
    (1.0910, 340.5),
    (1.3026, 417.4),
    (1.5301, 504.7),
    (1.8606, 640.2),
    (2.1384, 762.7),
    (2.4470, 908.6),
    (2.7967, 1087.4),
    (3.2077, 1317.1),
    (3.4965, 1491.3),
    (3.7457, 1649.7),
    (4.0154, 1827.1),
    (4.3109, 2021.9),
]

SAT_VAP = [
    (4.5308, 2164.2),
    (4.9299, 2411.4),
    (5.2463, 2580.8),
    (5.4941, 2685.6),
    (5.7448, 2758.6),
    (6.0697, 2800.9),
    (6.3392, 2798.4),
    (6.5850, 2777.1),
    (6.8206, 2748.1),
    (7.1269, 2706.2),
    (7.3588, 2674.9),
    (7.5930, 2645.2),
    (7.9072, 2608.9),
    (8.1489, 2583.9),
    (8.3291, 2566.7),
    (8.5766, 2544.9),
]

CYCLES = [
    {
        "name": "I",
        "color": "#1368aa",
        "p1": "40 бар",
        "t1": "315 °C",
        "p2": "0,22 бар",
        "h1": 3002.9,
        "s1": 6.4349,
        "h2": 2130.0,
        "s2": 6.4349,
        "h3": 260.1,
        "s3": 0.8579,
    },
    {
        "name": "II",
        "color": "#d12f2f",
        "p1": "120 бар",
        "t1": "400 °C",
        "p2": "0,03 бар",
        "h1": 3051.9,
        "s1": 6.0762,
        "h2": 1801.7,
        "s2": 6.0762,
        "h3": 101.0,
        "s3": 0.3543,
    },
]


def lerp(value, src_min, src_max, dst_min, dst_max):
    return dst_min + (value - src_min) * (dst_max - dst_min) / (src_max - src_min)


def text(x, y, value, size=15, anchor="middle", color="#222", weight="normal"):
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{color}">{value}</text>'
    )


def line(x1, y1, x2, y2, color="#ccc", width=1, extra=""):
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{color}" stroke-width="{width}" {extra}/>'
    )


def fmt(value, digits=1):
    return f"{value:.{digits}f}".replace(".", ",")


def generate_is_diagram():
    width, height = 980, 720
    left, right, top, bottom = 95, 55, 70, 95
    plot_w = width - left - right
    plot_h = height - top - bottom
    x_min, x_max = 0.0, 9.0
    y_min, y_max = 0.0, 3400.0

    def sx(s):
        return lerp(s, x_min, x_max, left, left + plot_w)

    def sy(h):
        return lerp(h, y_min, y_max, top + plot_h, top)

    dome_points = SAT_LIQ + SAT_VAP
    dome = " ".join(f"{sx(s):.1f},{sy(h):.1f}" for s, h in dome_points)

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="980" height="720" viewBox="0 0 980 720">',
        "<defs>",
        '<marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">',
        '<path d="M 0 0 L 12 6 L 0 12 z" fill="#222"/>',
        "</marker>",
        "</defs>",
        '<rect width="100%" height="100%" fill="white"/>',
        text(width / 2, 36, "i-S диаграмма: сравнение двух циклов Ренкина", 24, weight="bold"),
    ]

    for s in range(0, 10):
        x = sx(s)
        parts.append(line(x, top, x, top + plot_h, "#e6e6e6"))
        parts.append(line(x, top + plot_h, x, top + plot_h + 7, "#222", 1.4))
        parts.append(text(x, top + plot_h + 30, str(s), 13))
    for h in range(0, 3401, 400):
        y = sy(h)
        parts.append(line(left, y, left + plot_w, y, "#e6e6e6"))
        parts.append(line(left - 7, y, left, y, "#222", 1.4))
        parts.append(text(left - 13, y + 5, str(h), 13, anchor="end"))

    parts.append(line(left, top + plot_h, left + plot_w, top + plot_h, "#222", 2))
    parts.append(line(left, top, left, top + plot_h, "#222", 2))
    parts.append(text(left + plot_w / 2, height - 30, "S, кДж/(кг*K)", 17))
    parts.append(
        f'<text x="30" y="{top + plot_h / 2:.1f}" font-family="Arial, sans-serif" '
        f'font-size="17" text-anchor="middle" fill="#222" '
        f'transform="rotate(-90 30 {top + plot_h / 2:.1f})">i, кДж/кг</text>'
    )
    parts.append(f'<polygon points="{dome}" fill="#f3f8ff" stroke="#555" stroke-width="2"/>')
    parts.append(text(sx(4.8), sy(2450), "область влажного пара", 15, color="#555"))

    for cycle in CYCLES:
        color = cycle["color"]
        p1 = (sx(cycle["s1"]), sy(cycle["h1"]))
        p2 = (sx(cycle["s2"]), sy(cycle["h2"]))
        p3 = (sx(cycle["s3"]), sy(cycle["h3"]))
        parts.append(line(p1[0], p1[1], p2[0], p2[1], color, 4, 'marker-end="url(#arrow)"'))
        parts.append(line(p2[0], p2[1], p3[0], p3[1], color, 2.2))
        parts.append(line(p3[0], p3[1], p1[0], p1[1], color, 2.2, "stroke-dasharray=\"8 6\""))

        for label, point, dx, dy in [
            (f"{cycle['name']}1", p1, 20, -12),
            (f"{cycle['name']}2", p2, 22, 8),
            (f"{cycle['name']}3", p3, 26, -8),
        ]:
            parts.append(f'<circle cx="{point[0]:.1f}" cy="{point[1]:.1f}" r="5.5" fill="{color}"/>')
            parts.append(text(point[0] + dx, point[1] + dy, label, 15, color=color, weight="bold"))

    legend_x, legend_y = 640, 575
    parts.append('<rect x="620" y="535" width="300" height="95" fill="white" stroke="#ccc"/>')
    for i, cycle in enumerate(CYCLES):
        y = legend_y + i * 35
        parts.append(line(legend_x, y, legend_x + 42, y, cycle["color"], 4))
        parts.append(
            text(
                legend_x + 55,
                y + 5,
                f"Цикл {cycle['name']}: P1={cycle['p1']}, t1={cycle['t1']}, P2={cycle['p2']}",
                14,
                anchor="start",
            )
        )

    parts.append("</svg>")
    (OUT_DIR / "zadacha_2_is_diagram.svg").write_text("\n".join(parts), encoding="utf-8")


def generate_temperature_profile():
    width, height = 980, 650
    left, right, top, bottom = 95, 55, 70, 95
    plot_w = width - left - right
    plot_h = height - top - bottom
    x_min, x_max = 0.0, 0.0115
    y_min, y_max = 0.0, 470.0

    def sx(r):
        return lerp(r, x_min, x_max, left, left + plot_w)

    def sy(t):
        return lerp(t, y_min, y_max, top + plot_h, top)

    no_scale = [
        (0.0, 450.0, "газ"),
        (1 / 5400, 443.3, "сталь со стороны газа"),
        (1 / 5400 + 0.002 / 58, 442.1, "сталь со стороны воды"),
        (1 / 5400 + 0.002 / 58 + 1 / 90, 40.0, "вода"),
    ]
    with_scale = [
        (0.0, 450.0, "газ"),
        (1 / 5400, 443.3, "поверхность накипи"),
        (1 / 5400 + 0.0002 / 3, 440.9, "сталь под накипью"),
        (1 / 5400 + 0.0002 / 3 + 0.002 / 58, 439.7, "сталь у воды"),
        (1 / 5400 + 0.0002 / 3 + 0.002 / 58 + 1 / 90, 40.0, "вода"),
    ]

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="980" height="650" viewBox="0 0 980 650">',
        '<rect width="100%" height="100%" fill="white"/>',
        text(width / 2, 36, "Эпюра температуры через стенку", 24, weight="bold"),
    ]

    for r in [0, 0.002, 0.004, 0.006, 0.008, 0.010]:
        x = sx(r)
        parts.append(line(x, top, x, top + plot_h, "#e6e6e6"))
        parts.append(line(x, top + plot_h, x, top + plot_h + 7, "#222", 1.4))
        parts.append(text(x, top + plot_h + 30, fmt(r, 3), 13))
    for t in range(0, 451, 50):
        y = sy(t)
        parts.append(line(left, y, left + plot_w, y, "#e6e6e6"))
        parts.append(line(left - 7, y, left, y, "#222", 1.4))
        parts.append(text(left - 13, y + 5, str(t), 13, anchor="end"))

    parts.append(line(left, top + plot_h, left + plot_w, top + plot_h, "#222", 2))
    parts.append(line(left, top, left, top + plot_h, "#222", 2))
    parts.append(text(left + plot_w / 2, height - 30, "Суммарное тепловое сопротивление от газа, м2*K/Вт", 16))
    parts.append(
        f'<text x="30" y="{top + plot_h / 2:.1f}" font-family="Arial, sans-serif" '
        f'font-size="17" text-anchor="middle" fill="#222" '
        f'transform="rotate(-90 30 {top + plot_h / 2:.1f})">t, °C</text>'
    )

    for points, color, label in [
        (no_scale, "#1368aa", "без накипи"),
        (with_scale, "#d12f2f", "с накипью"),
    ]:
        poly = " ".join(f"{sx(r):.1f},{sy(t):.1f}" for r, t, _ in points)
        parts.append(f'<polyline points="{poly}" fill="none" stroke="{color}" stroke-width="4"/>')
        for r, t, name in points:
            parts.append(f'<circle cx="{sx(r):.1f}" cy="{sy(t):.1f}" r="5" fill="{color}"/>')
        parts.append(text(735, 105 if color == "#1368aa" else 135, label, 16, anchor="start", color=color, weight="bold"))
        parts.append(line(690, 100 if color == "#1368aa" else 130, 725, 100 if color == "#1368aa" else 130, color, 4))

    parts.append(text(sx(no_scale[-1][0]) - 10, sy(40) - 12, "основной перепад: водяная пленка", 14, anchor="end", color="#555"))
    parts.append("</svg>")
    (OUT_DIR / "zadacha_3_temperature_profile.svg").write_text("\n".join(parts), encoding="utf-8")


if __name__ == "__main__":
    generate_is_diagram()
    generate_temperature_profile()
