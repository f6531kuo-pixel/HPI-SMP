"""罐子包材示意圖：讀 draw/bottle_XX.json，輸出 PNG＋PDF 到 draw/out/。
用法：python3 draw/make_bottle.py draw/bottle_01.json
黑色實線＝卡尺實測；深紅虛線＝推定值（待確認）。"""
import json, sys, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

for f in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
          "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"]:
    if os.path.exists(f):
        font_manager.fontManager.addfont(f)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=f).get_name()
        break
RED = "#8b0000"

def dim_v(ax, x, y0, y1, text, color="k", side=1):
    ax.annotate("", (x, y0), (x, y1), arrowprops=dict(arrowstyle="<->", color=color, lw=0.8))
    ax.text(x + side * 1.2, (y0 + y1) / 2, text, rotation=90, va="center",
            ha="left" if side > 0 else "right", color=color, fontsize=9)

def dim_h(ax, y, x0, x1, text, color="k", dy=1.2):
    ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<->", color=color, lw=0.8))
    ax.text((x0 + x1) / 2, y + dy, text, ha="center", va="bottom" if dy > 0 else "top",
            color=color, fontsize=9)

def ext(ax, x0, y0, x1, y1, color="k"):
    ax.plot([x0, x1], [y0, y1], color=color, lw=0.4)

def main(path):
    d = json.load(open(path))
    m = {k: v["v"] for k, v in d["measured"].items()}
    a = d["assumed"]
    R = m["body_od"] / 2; Rn = m["neck_od"] / 2; Ri = m["neck_id"] / 2; Rc = m["cap_od"] / 2
    Hs = m["body_straight_h"]; Hb = m["bottle_h"]; Ht = m["total_h_with_cap"]
    rb = a["base_r"]; rc = a["cap_top_r"]; hn = a["neck_h_under_cap"]

    # 右半輪廓（瓶身）
    t = np.linspace(-np.pi / 2, 0, 20)
    base = np.c_[R - rb + rb * np.cos(t), rb + rb * np.sin(t)]
    t2 = np.linspace(0, np.pi / 2, 40)
    sh = np.c_[Rn + (R - Rn) * np.cos(t2), Hs + (Hb - Hs) * np.sin(t2)]
    body = np.vstack([[0, 0], base, [R, Hs], sh])
    t3 = np.linspace(0, np.pi / 2, 12)
    cap = np.vstack([[Rc, Hb], [Rc, Ht - rc], np.c_[Rc - rc + rc * np.cos(t3), Ht - rc + rc * np.sin(t3)], [0, Ht]])

    fig = plt.figure(figsize=(11.69, 8.27))  # A4 橫
    ax = fig.add_axes([0.03, 0.06, 0.55, 0.86]); ax.set_aspect("equal"); ax.axis("off")
    for s in (1, -1):
        ax.plot(s * body[:, 0], body[:, 1], "k", lw=1.4)
        ax.plot(s * cap[:, 0], cap[:, 1], "k", lw=1.4)
        ax.plot([s * Rn] * 2, [Hb, Hb + hn], color=RED, ls="--", lw=0.8)   # 蓋內瓶頸（隱藏線）
        ax.plot([s * Ri] * 2, [Hb, Hb + hn], color=RED, ls=":", lw=0.8)
    ax.plot([-Rc, Rc], [Hb, Hb], "k", lw=1.4)
    ax.plot([-Rn, Rn], [Hb + hn] * 2, color=RED, ls="--", lw=0.8)
    ax.plot([0, 0], [-6, Ht + 6], color="0.4", ls="-.", lw=0.6)
    ax.fill_between(cap[:, 0], Hb, cap[:, 1], color="0.85", zorder=0)
    ax.fill_between(-cap[:, 0], Hb, cap[:, 1], color="0.85", zorder=0)

    # 高度尺寸（右側）
    xs = R + 8
    for y in (0, Hs, Hb, Ht):
        ext(ax, (Rc if y == Ht else R if y <= Hs else Rn) + 1, y, xs + 22, y)
    dim_v(ax, xs, 0, Hs, f"{Hs:g}  直身段")
    dim_v(ax, xs + 9, 0, Hb, f"{Hb:g}  瓶高（不含蓋）")
    dim_v(ax, xs + 18, 0, Ht, f"{Ht:g}  全高（含蓋）")
    dim_v(ax, -R - 8, Hs, Hb, f"{Hb - Hs:.1f}  肩部（推算）", color=RED, side=-1)
    dim_v(ax, -Rc - 5, Hb, Ht, f"{Ht - Hb:.1f}  蓋高（推算）", color=RED, side=-1)
    ext(ax, -R - 1, Hs, -R - 10, Hs); ext(ax, -Rn - 1, Hb, -R - 10, Hb); ext(ax, -Rc - 1, Ht, -Rc - 7, Ht)
    # 直徑
    dim_h(ax, -8, -R, R, f"Ø{m['body_od']:g}  瓶身外徑", dy=-1.2)
    ext(ax, -R, rb, -R, -10); ext(ax, R, rb, R, -10)
    dim_h(ax, Ht + 6, -Rc, Rc, f"Ø{m['cap_od']:g}  瓶蓋外徑")
    ext(ax, -Rc, Ht - rc, -Rc, Ht + 8); ext(ax, Rc, Ht - rc, Rc, Ht + 8)
    ax.annotate(f"瓶口螺牙外徑 Ø{m['neck_od']:g}\n瓶口內徑 Ø{m['neck_id']:g}\n（蓋內，虛線）",
                (Rn, Hb + hn * 0.6), (R + 30, Hb + 10), fontsize=8.5,
                arrowprops=dict(arrowstyle="->", lw=0.6))
    ax.text(0, Hs * 0.45, "藍色 PET\n（熱縮膜包覆範圍\n待定）", ha="center", fontsize=9, color="0.35",
            bbox=dict(fc="white", ec="none", pad=1))
    ax.set_xlim(-R - 26, R + 62); ax.set_ylim(-16, Ht + 14)

    # 右側表格
    tx = fig.add_axes([0.60, 0.06, 0.38, 0.86]); tx.axis("off")
    y = 0.98
    tx.text(0, y, d["name"], fontsize=14, weight="bold", va="top"); y -= 0.05
    tx.text(0, y, "單位 mm｜比例 1:1 示意（A4 列印非原寸）", fontsize=9, va="top"); y -= 0.06
    tx.text(0, y, "卡尺實測（黑色）", fontsize=11, weight="bold", va="top"); y -= 0.045
    for v in d["measured"].values():
        tx.text(0, y, f"{v['v']:>7g}", fontsize=9.5, va="top", family="monospace")
        tx.text(0.17, y, f"{v['note']}  〔{v['photo']}〕", fontsize=9, va="top"); y -= 0.038
    y -= 0.02
    tx.text(0, y, "推定值（深紅，待確認）", fontsize=11, weight="bold", va="top", color=RED); y -= 0.045
    for s in [f"瓶底圓角 R{rb:g}", f"蓋內瓶頸高 {hn:g}", "肩部形狀：照片比例畫成橢圓弧",
              f"肩部高 {Hb-Hs:.1f}＝瓶高-直身段", f"蓋高 {Ht-Hb:.1f}＝全高-瓶高"]:
        tx.text(0, y, "・" + s, fontsize=9, va="top", color=RED); y -= 0.036
    y -= 0.02
    tx.text(0, y, "量了但不知量哪裡", fontsize=11, weight="bold", va="top"); y -= 0.045
    for k, v in d["unknown"].items():
        tx.text(0, y, f"・{v['v']:g}〔{k}〕{v['note']}", fontsize=9, va="top"); y -= 0.036
    y -= 0.02
    tx.text(0, y, "沒有讀數的照片", fontsize=11, weight="bold", va="top"); y -= 0.045
    for s in d["no_reading"]:
        tx.text(0, y, "・" + s, fontsize=9, va="top"); y -= 0.036

    base = os.path.splitext(os.path.basename(path))[0]
    os.makedirs(os.path.join(os.path.dirname(path), "out"), exist_ok=True)
    for ext_ in ("png", "pdf"):
        fig.savefig(os.path.join(os.path.dirname(path), "out", f"{base}.{ext_}"), dpi=150)
    print("ok", base)

if __name__ == "__main__":
    main(sys.argv[1])
