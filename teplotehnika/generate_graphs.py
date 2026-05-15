from math import exp, log
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent

P1_BAR = 40.0
P2_BAR = 200.0
N = 5.0
T1 = 823.0
POLYTROPIC_N = 1.2
R = 0.297
CP = 1.039
V1 = R * T1 / (P1_BAR * 100.0)


def lerp(value, src_min, src_max, dst_min, dst_max):
    return dst_min + (value - src_min) * (dst_max - dst_min) / (src_max - src_min)


def fmt(value):
    return f"{value:.3f}".replace(".", ",")


def svg_line(x1, y1, x2, y2, color="#cccccc", width=1, extra=""):
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{color}" stroke-width="{width}" {extra}/>'
    )


def svg_text(x, y, text, size=16, anchor="middle", color="#222222", weight="normal"):
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{color}">{text}</text>'
    )


def write_svg(filename, title, x_label, y_label, x_min, x_max, y_min, y_max, x_ticks, y_ticks, points):
    width = 920
    height = 660
    left = 105
    right = 45
    top = 75
    bottom = 95
    plot_w = width - left - right
    plot_h = height - top - bottom

    def sx(x):
        return lerp(x, x_min, x_max, left, left + plot_w)

    def sy(y):
        return lerp(y, y_min, y_max, top + plot_h, top)

    curve = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in points)
    start_x, start_y = points[0]
    end_x, end_y = points[-1]

    content = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="920" height="660" viewBox="0 0 920 660">',
        "<defs>",
        '<marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">',
        '<path d="M 0 0 L 12 6 L 0 12 z" fill="#d12f2f"/>',
        "</marker>",
        "</defs>",
        '<rect width="100%" height="100%" fill="white"/>',
        svg_text(width / 2, 36, title, size=24, weight="bold"),
    ]

    for tick in x_ticks:
        x = sx(tick)
        content.append(svg_line(x, top, x, top + plot_h, "#e5e5e5"))
        content.append(svg_line(x, top + plot_h, x, top + plot_h + 7, "#222222", 1.5))
        content.append(svg_text(x, top + plot_h + 30, fmt(tick), size=13))

    for tick in y_ticks:
        y = sy(tick)
        content.append(svg_line(left, y, left + plot_w, y, "#e5e5e5"))
        content.append(svg_line(left - 7, y, left, y, "#222222", 1.5))
        content.append(svg_text(left - 13, y + 5, fmt(tick), size=13, anchor="end"))

    content.append(svg_line(left, top + plot_h, left + plot_w, top + plot_h, "#222222", 2))
    content.append(svg_line(left, top, left, top + plot_h, "#222222", 2))
    content.append(svg_text(left + plot_w / 2, height - 30, x_label, size=17))
    content.append(
        f'<text x="30" y="{top + plot_h / 2:.1f}" font-family="Arial, sans-serif" '
        f'font-size="17" text-anchor="middle" fill="#222222" '
        f'transform="rotate(-90 30 {top + plot_h / 2:.1f})">{y_label}</text>'
    )

    content.append(f'<polyline points="{curve}" fill="none" stroke="#1368aa" stroke-width="4"/>')

    # Arrow between two nearby calculated points, so the direction of the process is clear.
    arrow_start = points[len(points) // 2 - 4]
    arrow_end = points[len(points) // 2 + 4]
    content.append(
        svg_line(
            sx(arrow_start[0]),
            sy(arrow_start[1]),
            sx(arrow_end[0]),
            sy(arrow_end[1]),
            "#d12f2f",
            3,
            'marker-end="url(#arrow)"',
        )
    )

    for label, x, y, dx, dy in [
        ("1", start_x, start_y, 18, 25),
        ("2", end_x, end_y, -20, -18),
    ]:
        px = sx(x)
        py = sy(y)
        content.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="6" fill="#d12f2f"/>')
        content.append(svg_text(px + dx, py + dy, label, size=20, weight="bold", color="#d12f2f"))

    content.append("</svg>")
    (OUT_DIR / filename).write_text("\n".join(content), encoding="utf-8")


def pv_points():
    points = []
    for i in range(121):
        p = P1_BAR + (P2_BAR - P1_BAR) * i / 120
        v = V1 * (P1_BAR / p) ** (1.0 / POLYTROPIC_N)
        points.append((v, p))
    return points


def ts_points():
    points = []
    for i in range(121):
        ratio = 1.0 + (N - 1.0) * i / 120
        t = T1 * ratio ** ((POLYTROPIC_N - 1.0) / POLYTROPIC_N)
        ds = CP * log(t / T1) - R * log(ratio)
        points.append((ds, t))
    return points


def main():
    write_svg(
        "pv_graph.svg",
        "Политропное сжатие CO в координатах P-v",
        "v, м3/кг",
        "P, бар",
        0.015,
        0.065,
        40,
        200,
        [0.015, 0.025, 0.035, 0.045, 0.055, 0.065],
        [40, 80, 120, 160, 200],
        pv_points(),
    )
    write_svg(
        "ts_graph.svg",
        "Политропное сжатие CO в координатах T-s",
        "s - s1, кДж/(кг*K)",
        "T, K",
        -0.22,
        0.02,
        800,
        1100,
        [-0.20, -0.15, -0.10, -0.05, 0.00],
        [800, 850, 900, 950, 1000, 1050, 1100],
        ts_points(),
    )


if __name__ == "__main__":
    main()
