from math import log
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent


def lerp(value, src_min, src_max, dst_min, dst_max):
    return dst_min + (value - src_min) * (dst_max - dst_min) / (src_max - src_min)


def line(x1, y1, x2, y2, color="#cccccc", width=1, extra=""):
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{color}" stroke-width="{width}" {extra}/>'
    )


def text(x, y, value, size=15, anchor="middle", color="#222222", weight="normal"):
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{color}">{value}</text>'
    )


def fmt(value, digits=3):
    return f"{value:.{digits}f}".replace(".", ",")


def add_axes(parts, width, height, left, right, top, bottom, x_min, x_max, y_min, y_max, x_ticks, y_ticks, x_label, y_label):
    plot_w = width - left - right
    plot_h = height - top - bottom

    def sx(x):
        return lerp(x, x_min, x_max, left, left + plot_w)

    def sy(y):
        return lerp(y, y_min, y_max, top + plot_h, top)

    for tick in x_ticks:
        x = sx(tick)
        parts.append(line(x, top, x, top + plot_h, "#e6e6e6"))
        parts.append(line(x, top + plot_h, x, top + plot_h + 7, "#222222", 1.4))
        parts.append(text(x, top + plot_h + 30, fmt(tick, 3) if abs(tick) < 1 else fmt(tick, 1), 13))

    for tick in y_ticks:
        y = sy(tick)
        parts.append(line(left, y, left + plot_w, y, "#e6e6e6"))
        parts.append(line(left - 7, y, left, y, "#222222", 1.4))
        parts.append(text(left - 13, y + 5, fmt(tick, 0), 13, anchor="end"))

    parts.append(line(left, top + plot_h, left + plot_w, top + plot_h, "#222222", 2))
    parts.append(line(left, top, left, top + plot_h, "#222222", 2))
    parts.append(text(left + plot_w / 2, height - 30, x_label, 17))
    parts.append(
        f'<text x="30" y="{top + plot_h / 2:.1f}" font-family="Arial, sans-serif" '
        f'font-size="17" text-anchor="middle" fill="#222222" '
        f'transform="rotate(-90 30 {top + plot_h / 2:.1f})">{y_label}</text>'
    )
    return sx, sy


def write_polyline_graph(filename, title, x_label, y_label, x_min, x_max, y_min, y_max, x_ticks, y_ticks, points):
    width, height = 920, 660
    left, right, top, bottom = 105, 45, 75, 95
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="920" height="660" viewBox="0 0 920 660">',
        "<defs>",
        '<marker id="arrow-red" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">',
        '<path d="M 0 0 L 12 6 L 0 12 z" fill="#d12f2f"/>',
        "</marker>",
        "</defs>",
        '<rect width="100%" height="100%" fill="white"/>',
        text(width / 2, 36, title, 24, weight="bold"),
    ]
    sx, sy = add_axes(parts, width, height, left, right, top, bottom, x_min, x_max, y_min, y_max, x_ticks, y_ticks, x_label, y_label)
    curve = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in points)
    parts.append(f'<polyline points="{curve}" fill="none" stroke="#1368aa" stroke-width="4"/>')
    a = points[len(points) // 2 - 5]
    b = points[len(points) // 2 + 5]
    parts.append(line(sx(a[0]), sy(a[1]), sx(b[0]), sy(b[1]), "#d12f2f", 3, 'marker-end="url(#arrow-red)"'))
    for label, point, dx, dy in [("1", points[0], 18, 25), ("2", points[-1], -20, -18)]:
        parts.append(f'<circle cx="{sx(point[0]):.1f}" cy="{sy(point[1]):.1f}" r="6" fill="#d12f2f"/>')
        parts.append(text(sx(point[0]) + dx, sy(point[1]) + dy, label, 20, color="#d12f2f", weight="bold"))
    parts.append("</svg>")
    (OUT_DIR / filename).write_text("\n".join(parts), encoding="utf-8")


def generate_task1_graphs():
    p1_bar = 22.0
    n_ratio = 12.0
    t1 = 823.0
    n_poly = 1.31
    r = 0.4615
    cv = 1.38
    cp = cv + r
    v1 = r * t1 / (p1_bar * 100.0)

    pv_points = []
    ts_points = []
    for i in range(141):
        ratio = 1.0 + (n_ratio - 1.0) * i / 140
        p = p1_bar * ratio
        t = t1 * ratio ** ((n_poly - 1.0) / n_poly)
        v = r * t / (p * 100.0)
        ds = cp * log(t / t1) - r * log(ratio)
        pv_points.append((v, p))
        ts_points.append((ds, t))

    write_polyline_graph(
        "zadacha_1_variant_7_4_h2o_pv.svg",
        "Задача 1: политропное сжатие H2O в P-v",
        "v, м3/кг",
        "P, бар",
        0.02,
        0.18,
        20,
        270,
        [0.02, 0.06, 0.10, 0.14, 0.18],
        [20, 70, 120, 170, 220, 270],
        pv_points,
    )
    write_polyline_graph(
        "zadacha_1_variant_7_4_h2o_ts.svg",
        "Задача 1: политропное сжатие H2O в T-s",
        "s - s1, кДж/(кг*K)",
        "T, K",
        -0.075,
        0.01,
        800,
        1500,
        [-0.07, -0.05, -0.03, -0.01, 0.00],
        [800, 950, 1100, 1250, 1400],
        ts_points,
    )


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


def generate_task2_diagram():
    cycles = [
        {
            "name": "I",
            "color": "#1368aa",
            "p1": "50 бар",
            "t1": "340 °C",
            "p2": "0,24 бар",
            "h1": 3042.4,
            "s1": 6.4080,
            "h2": 2131.6,
            "s2": 6.4080,
            "h3": 268.1,
            "s3": 0.8818,
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

    width, height = 980, 720
    left, right, top, bottom = 95, 55, 70, 95
    x_min, x_max = 0.0, 9.0
    y_min, y_max = 0.0, 3400.0
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="980" height="720" viewBox="0 0 980 720">',
        "<defs>",
        '<marker id="arrow-black" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">',
        '<path d="M 0 0 L 12 6 L 0 12 z" fill="#222222"/>',
        "</marker>",
        "</defs>",
        '<rect width="100%" height="100%" fill="white"/>',
        text(width / 2, 36, "Задача 2: i-S диаграмма двух циклов", 24, weight="bold"),
    ]
    sx, sy = add_axes(
        parts,
        width,
        height,
        left,
        right,
        top,
        bottom,
        x_min,
        x_max,
        y_min,
        y_max,
        list(range(10)),
        list(range(0, 3401, 400)),
        "S, кДж/(кг*K)",
        "i, кДж/кг",
    )
    dome = " ".join(f"{sx(s):.1f},{sy(h):.1f}" for s, h in SAT_LIQ + SAT_VAP)
    parts.append(f'<polygon points="{dome}" fill="#f3f8ff" stroke="#555555" stroke-width="2"/>')
    parts.append(text(sx(4.8), sy(2450), "область влажного пара", 15, color="#555555"))

    for cycle in cycles:
        color = cycle["color"]
        p1 = (sx(cycle["s1"]), sy(cycle["h1"]))
        p2 = (sx(cycle["s2"]), sy(cycle["h2"]))
        p3 = (sx(cycle["s3"]), sy(cycle["h3"]))
        parts.append(line(p1[0], p1[1], p2[0], p2[1], color, 4, 'marker-end="url(#arrow-black)"'))
        parts.append(line(p2[0], p2[1], p3[0], p3[1], color, 2.2))
        parts.append(line(p3[0], p3[1], p1[0], p1[1], color, 2.2, 'stroke-dasharray="8 6"'))
        for label, point, dx, dy in [
            (f"{cycle['name']}1", p1, 20, -12),
            (f"{cycle['name']}2", p2, 22, 8),
            (f"{cycle['name']}3", p3, 26, -8),
        ]:
            parts.append(f'<circle cx="{point[0]:.1f}" cy="{point[1]:.1f}" r="5.5" fill="{color}"/>')
            parts.append(text(point[0] + dx, point[1] + dy, label, 15, color=color, weight="bold"))

    parts.append('<rect x="620" y="535" width="300" height="95" fill="white" stroke="#cccccc"/>')
    for i, cycle in enumerate(cycles):
        y = 575 + i * 35
        parts.append(line(640, y, 682, y, cycle["color"], 4))
        parts.append(text(695, y + 5, f"Цикл {cycle['name']}: P1={cycle['p1']}, t1={cycle['t1']}, P2={cycle['p2']}", 14, anchor="start"))
    parts.append("</svg>")
    (OUT_DIR / "zadacha_2_variant_7_4_is.svg").write_text("\n".join(parts), encoding="utf-8")


def generate_task3_profile():
    width, height = 980, 650
    left, right, top, bottom = 95, 55, 70, 95
    x_min, x_max = 0.0, 0.0084
    y_min, y_max = 0.0, 470.0
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="980" height="650" viewBox="0 0 980 650">',
        '<rect width="100%" height="100%" fill="white"/>',
        text(width / 2, 36, "Задача 3: эпюра температуры через стенку", 24, weight="bold"),
    ]
    sx, sy = add_axes(
        parts,
        width,
        height,
        left,
        right,
        top,
        bottom,
        x_min,
        x_max,
        y_min,
        y_max,
        [0, 0.002, 0.004, 0.006, 0.008],
        list(range(0, 451, 50)),
        "Суммарное тепловое сопротивление от газа, м2*K/Вт",
        "t, °C",
    )
    no_scale = [
        (0.0, 450.0),
        (1 / 5400, 440.3),
        (1 / 5400 + 0.0015 / 58, 438.9),
        (1 / 5400 + 0.0015 / 58 + 1 / 125, 20.0),
    ]
    with_scale = [
        (0.0, 450.0),
        (1 / 5400, 440.4),
        (1 / 5400 + 0.00015 / 3, 437.8),
        (1 / 5400 + 0.00015 / 3 + 0.0015 / 58, 436.4),
        (1 / 5400 + 0.00015 / 3 + 0.0015 / 58 + 1 / 125, 20.0),
    ]
    for points, color, label, y_leg in [
        (no_scale, "#1368aa", "без накипи", 100),
        (with_scale, "#d12f2f", "с накипью", 130),
    ]:
        poly = " ".join(f"{sx(r):.1f},{sy(t):.1f}" for r, t in points)
        parts.append(f'<polyline points="{poly}" fill="none" stroke="{color}" stroke-width="4"/>')
        for r, t in points:
            parts.append(f'<circle cx="{sx(r):.1f}" cy="{sy(t):.1f}" r="5" fill="{color}"/>')
        parts.append(line(690, y_leg, 725, y_leg, color, 4))
        parts.append(text(735, y_leg + 5, label, 16, anchor="start", color=color, weight="bold"))
    parts.append(text(sx(no_scale[-1][0]) - 10, sy(20) - 12, "самый большой перепад: теплоотдача к воде", 14, anchor="end", color="#555555"))
    parts.append("</svg>")
    (OUT_DIR / "zadacha_3_variant_7_4_temperature_profile.svg").write_text("\n".join(parts), encoding="utf-8")


if __name__ == "__main__":
    generate_task1_graphs()
    generate_task2_diagram()
    generate_task3_profile()
