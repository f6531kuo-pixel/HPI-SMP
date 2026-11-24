"""護木油（等）瓶身套標示意：正面／背面。
用法：python3 label/make_label.py label/woodoil_v1.json
瓶形讀 draw/bottle_01.json；版型照 ref/HPI淨化液_瓶身示意.png。"""
import json, sys, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon

REG = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
for f in (REG, BOLD): font_manager.fontManager.addfont(f)
FR = font_manager.FontProperties(fname=REG); FB = font_manager.FontProperties(fname=BOLD)
RED = "#c4161c"; BG = "#f2f2ee"; BLUE = "#1f2f9e"; GREY = "#555"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def bottle_outline(m):
    R = m["body_od"] / 2; Rn = m["neck_od"] / 2; Rc = m["cap_od"] / 2
    Hs = m["body_straight_h"]; Hb = m["bottle_h"]; Ht = m["total_h_with_cap"]
    Hn0 = Hb - m["neck_h"]; Hcb = Ht - m["cap_h"]; rb = 4
    t = np.linspace(-np.pi / 2, 0, 16)
    base = np.c_[R - rb + rb * np.cos(t), rb + rb * np.sin(t)]
    t2 = np.linspace(0, np.pi / 2, 30)
    sh = np.c_[Rn + (R - Rn) * np.cos(t2), Hs + (Hn0 - Hs) * np.sin(t2)]
    right = np.vstack([[0, 0], base, [R, Hs], sh, [Rn, Hb]])
    left = right[::-1] * [-1, 1]
    return np.vstack([right, left]), dict(R=R, Rc=Rc, Hcb=Hcb, Ht=Ht, Hb=Hb)

def wrap(s, n):
    out, line = [], ""
    for ch in s:
        if ch in "123456789" and line.endswith("。"):   # 條列換行
            out.append(line); line = ""
        if ch == "\n":
            out.append(line); line = ""; continue
        line += ch
        if len(line) >= n:
            out.append(line); line = ""
    if line: out.append(line)
    return out

def main(path):
    c = json.load(open(path))
    m = {k: v["v"] for k, v in json.load(open(os.path.join(ROOT, "draw/bottle_01.json")))["measured"].items()}
    poly, g = bottle_outline(m)
    R, Rc, Hcb, Ht = g["R"], g["Rc"], g["Hcb"], g["Ht"]
    y0, y1 = c["label_y"]
    gap = 70
    fig = plt.figure(figsize=(12.8, 10.8), facecolor=BG)
    ax = fig.add_axes([0.08, 0.06, 0.84, 0.80]); ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-R - 45, gap + R + 55); ax.set_ylim(-14, Ht + 6)
    fig.canvas.draw()
    pt_mm = (ax.transData.transform((1, 0))[0] - ax.transData.transform((0, 0))[0]) * 72 / fig.dpi
    fs = lambda mm: mm * pt_mm   # 字高（mm）→ 字級

    for i, cx in enumerate((0, gap)):
        ax.add_patch(Polygon(poly + [cx, 0], closed=True, fc=BLUE, ec="#121a5e", lw=1, alpha=0.9))
        ax.add_patch(FancyBboxPatch((cx - Rc, Hcb), 2 * Rc, Ht - Hcb, boxstyle="round,pad=0,rounding_size=1.2",
                                    fc="#151515", ec="#000", lw=0.8))
        for k in np.linspace(-Rc + 1.5, Rc - 1.5, 13):
            ax.plot([cx + k] * 2, [Hcb + 1, Ht - m["cap_upper_h"] - 0.5], color="#444", lw=0.5)
        ax.plot([cx - Rc, cx + Rc], [Ht - m["cap_upper_h"]] * 2, color="#555", lw=0.8)
        ax.add_patch(Rectangle((cx - R, y0), 2 * R, y1 - y0, fc="white", ec="#ccc", lw=0.6))
        ax.add_patch(Rectangle((cx - R, y0), 2.2, y1 - y0, fc="#e6e6e6", ec="none"))
        ax.add_patch(Rectangle((cx + R - 2.2, y0), 2.2, y1 - y0, fc="#e6e6e6", ec="none"))
        ax.text(cx, -9, "正面" if i == 0 else "背面", ha="center", fontproperties=FB, fontsize=13)

    f = c["front"]; L = 9
    ax.add_patch(FancyBboxPatch((-L / 2, 70), L, L, boxstyle="round,pad=0,rounding_size=0.8", fc=RED, ec="none"))
    ax.text(0, 74.5, "HPI", ha="center", va="center", color="white", fontproperties=FB, fontsize=fs(3.2))
    ax.text(0, 61, f["name"], ha="center", va="center", fontproperties=FB, fontsize=fs(4.6), color="#222")
    if f.get("model"):
        ax.text(0, 56.3, f["model"], ha="center", va="center", fontproperties=FR, fontsize=fs(2.0), color="#666")
    ax.plot([-3.5, 3.5], [53, 53], color=RED, lw=1.4)
    for j, s in enumerate(f["features"]):
        ax.text(0, 46.5 - j * 5.2, s, ha="center", va="center", fontproperties=FR, fontsize=fs(2.6), color="#333")
    ax.text(R - 3.5, 10.5, f["capacity"], ha="right", va="center", fontproperties=FR, fontsize=fs(1.9), color="#333")

    x0 = gap - R + 3.2; y = y1 - 4.0; th = 1.45; lh = th * 1.55
    for head, body in c["back"]:
        inline = not head.startswith("【")
        if inline:
            lines = wrap(head + body, 25)
            for k, s in enumerate(lines):
                ax.text(x0, y, s, va="top", fontproperties=FB if k == 0 and False else FR, fontsize=fs(th), color="#333")
                y -= lh
        else:
            ax.text(x0, y, head, va="top", fontproperties=FB, fontsize=fs(th * 1.05), color="#222"); y -= lh
            for s in wrap(body, 25):
                ax.text(x0, y, s, va="top", fontproperties=FR, fontsize=fs(th), color="#333"); y -= lh
        y -= lh * 0.45
    ax.add_patch(Rectangle((x0, y0 + 2.5), 6, 6, fc="none", ec="#999", lw=0.6, ls="--"))
    ax.text(x0 + 3, y0 + 5.5, "回收\n標誌", ha="center", va="center", fontproperties=FR, fontsize=fs(1.2), color="#888")
    ax.add_patch(Rectangle((gap + R - 3.2 - 18, y0 + 2.5), 18, 7, fc="none", ec="#999", lw=0.6, ls="--"))
    ax.text(gap + R - 12.2, y0 + 6, "條碼 EAN-13", ha="center", va="center", fontproperties=FR, fontsize=fs(1.4), color="#888")

    # 尺寸註記
    kw = dict(fontproperties=FR, fontsize=10, color=GREY)
    ax.plot([-R - 8] * 2, [y0, y1], color=GREY, lw=0.7)
    for yy in (y0, y1): ax.plot([-R - 10, -R - 6], [yy, yy], color=GREY, lw=0.7)
    ax.text(-R - 10, (y0 + y1) / 2, f"套標高 {y1 - y0:g} mm\n（直身段 {m['body_straight_h']:g} mm）", ha="right", va="center", **kw)
    ax.text(-R - 10, y0 / 2, f"底部留 {y0:g} mm", ha="right", va="center", **kw)
    ax.plot([gap + R + 1, gap + R + 8], [60, 60], color=GREY, lw=0.7)
    ax.text(gap + R + 9, 60, f"瓶身 Ø{m['body_od']:g} mm\n（周長 {np.pi * m['body_od']:.1f} mm）\n套標環繞 360°", va="center", **kw)

    fig.text(0.04, 0.95, c["title"], fontproperties=FB, fontsize=18, color="#222")
    fig.text(0.04, 0.92, c["sub"], fontproperties=FR, fontsize=10, color=GREY)
    fig.text(0.04, 0.025, c["note"], fontproperties=FR, fontsize=9, color=GREY)
    b = os.path.splitext(os.path.basename(path))[0]
    od = os.path.join(os.path.dirname(os.path.abspath(path)), "out"); os.makedirs(od, exist_ok=True)
    for e in ("png", "pdf"):
        fig.savefig(os.path.join(od, f"{b}.{e}"), dpi=150, facecolor=BG)
    print("ok", b)

if __name__ == "__main__":
    main(sys.argv[1])
