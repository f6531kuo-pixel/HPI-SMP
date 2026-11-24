"""罐子包材示意圖：讀 draw/bottle_XX.json，輸出 PNG＋PDF 到 draw/out/。
用法：python3 draw/make_bottle.py draw/bottle_01.json
黑色＝卡尺實測；深紅＝推定值（待確認）。"""
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
    ax.annotate("", (x, y0), (x, y1), arrowprops=dict(arrowstyle="<->", color=color, lw=0.8, shrinkA=0, shrinkB=0))
    ax.text(x + side * 1.2, (y0 + y1) / 2, text, rotation=90, va="center",
            ha="left" if side > 0 else "right", color=color, fontsize=8.5)

def dim_h(ax, y, x0, x1, text, color="k", dy=1.2):
    ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<->", color=color, lw=0.8, shrinkA=0, shrinkB=0))
    ax.text((x0 + x1) / 2, y + dy, text, ha="center", va="bottom" if dy > 0 else "top", color=color, fontsize=9)

def ln(ax, x0, y0, x1, y1, color="k", lw=0.4, ls="-"):
    ax.plot([x0, x1], [y0, y1], color=color, lw=lw, ls=ls)

def main(path):
    d = json.load(open(path))
    M = d["measured"]; m = {k: v["v"] for k, v in M.items()}
    a = d["assumed"]
    R = m["body_od"] / 2; Rn = m["neck_od"] / 2; Ri = m["neck_id"] / 2; Rc = m["cap_od"] / 2
    Hs = m["body_straight_h"]; Hb = m["bottle_h"]; Ht = m["total_h_with_cap"]
    Hc = m["cap_h"]; Hcu = m["cap_upper_h"]
    rb = a["base_r"]; rc = a["cap_top_r"]
    Hcb = Ht - Hc            # 蓋下緣＝瓶頸根部（推定）
    tot_c = RED if M["total_h_with_cap"].get("check") else "k"

    t = np.linspace(-np.pi / 2, 0, 20)
    base = np.c_[R - rb + rb * np.cos(t), rb + rb * np.sin(t)]
    t2 = np.linspace(0, np.pi / 2, 40)
    sh = np.c_[Rn + (R - Rn) * np.cos(t2), Hs + (Hcb - Hs) * np.sin(t2)]
    body = np.vstack([[0, 0], base, [R, Hs], sh])
    t3 = np.linspace(0, np.pi / 2, 12)
    cap = np.vstack([[Rc, Hcb], [Rc, Ht - rc], np.c_[Rc - rc + rc * np.cos(t3), Ht - rc + rc * np.sin(t3)], [0, Ht]])

    fig = plt.figure(figsize=(11.69, 8.27))
    ax = fig.add_axes([0.02, 0.05, 0.57, 0.88]); ax.set_aspect("equal"); ax.axis("off")
    for s in (1, -1):
        ax.fill_between(s * cap[:, 0], Hcb, cap[:, 1], color="0.85", zorder=0)
        ax.plot(s * body[:, 0], body[:, 1], "k", lw=1.4)
        ax.plot(s * cap[:, 0], cap[:, 1], "k", lw=1.4)
        ln(ax, s * Rn, Hcb, s * Rn, Hb, RED, 0.8, "--")     # 蓋內瓶頸
        ln(ax, s * Ri, Hb - 3, s * Ri, Hb, RED, 0.8, ":")
    ln(ax, -Rc, Hcb, Rc, Hcb, "k", 1.4)
    ln(ax, -Rc, Ht - Hcu, Rc, Ht - Hcu, "k", 0.9)          # 上下蓋分界
    ln(ax, -Rn, Hb, Rn, Hb, RED, 0.8, "--")                # 瓶口頂
    ln(ax, 0, -6, 0, Ht + 6, "0.4", 0.6, "-.")

    # 右側高度
    xs = R + 7
    for y, x0 in ((0, R), (Hs, R), (Hb, Rc), (Ht, Rc)):
        ln(ax, x0 + 1, y, xs + 20, y)
    dim_v(ax, xs, 0, Hs, f"{Hs:g}  直身段")
    dim_v(ax, xs + 9, 0, Hb, f"{Hb:g}  瓶高（不含蓋，到瓶口頂）")
    dim_v(ax, xs + 18, 0, Ht, f"{Ht:g}  全高（含蓋）待確認", color=tot_c)
    # 左側：蓋
    xl = -Rc - 5
    for y in (Hcb, Ht - Hcu, Ht):
        ln(ax, -Rc - 1, y, xl - 16, y)
    ln(ax, -R - 1, Hs, -R - 18, Hs)
    dim_v(ax, xl, Hcb, Ht - Hcu, f"{m['cap_lower_h']:g} 下蓋", side=-1)
    dim_v(ax, xl, Ht - Hcu, Ht, f"{Hcu:g}", side=-1)
    ax.text(xl - 1.2, Ht + 1.5, "上蓋", ha="right", fontsize=8.5)
    dim_v(ax, xl - 9, Hcb, Ht, f"{Hc:g} 蓋高", side=-1)
    dim_v(ax, -R - 12, Hs, Hcb, f"{Hcb - Hs:.1f} 肩部（推算）", color=RED, side=-1)
    # 直徑
    dim_h(ax, -8, -R, R, f"Ø{m['body_od']:g}  瓶身外徑", dy=-1.2)
    ln(ax, -R, rb, -R, -10); ln(ax, R, rb, R, -10)
    dim_h(ax, Ht + 6, -Rc, Rc, f"Ø{m['cap_od']:g}  瓶蓋外徑")
    ln(ax, -Rc, Ht - rc, -Rc, Ht + 8); ln(ax, Rc, Ht - rc, Rc, Ht + 8)
    ax.annotate(f"瓶口螺牙外徑 Ø{m['neck_od']:g}\n瓶口內徑 Ø{m['neck_id']:g}\n（蓋內，虛線）",
                (Rn, (Hcb + Hb) / 2), (R + 32, Hb - 4), fontsize=8.5, arrowprops=dict(arrowstyle="->", lw=0.6))
    ax.text(0, Hs * 0.45, "藍色 PET", ha="center", fontsize=9, color="0.35", bbox=dict(fc="white", ec="none", pad=1))
    ax.set_xlim(-R - 34, R + 64); ax.set_ylim(-16, Ht + 14)

    tx = fig.add_axes([0.61, 0.05, 0.38, 0.88]); tx.axis("off")
    y = 0.98
    tx.text(0, y, d["name"], fontsize=14, weight="bold", va="top"); y -= 0.05
    tx.text(0, y, "單位 mm｜示意圖（A4 列印非原寸）", fontsize=9, va="top"); y -= 0.06
    tx.text(0, y, "卡尺實測", fontsize=11, weight="bold", va="top"); y -= 0.045
    for v in M.values():
        c = RED if v.get("check") else "k"
        tx.text(0, y, f"{v['v']:>7g}", fontsize=9.5, va="top", family="monospace", color=c)
        tx.text(0.17, y, f"{v['note']}〔{v['photo']}〕", fontsize=8.5, va="top", color=c, wrap=True); y -= 0.038
    y -= 0.02
    tx.text(0, y, "推定值（深紅，待確認）", fontsize=11, weight="bold", va="top", color=RED); y -= 0.045
    for s in [f"瓶底圓角 R{rb:g}", a["note_neck"], f"蓋下緣高 {Hcb:.2f}＝全高-蓋高",
              f"肩部高 {Hcb-Hs:.1f}＝蓋下緣-直身段，形狀照片比例畫橢圓弧",
              f"下蓋＋上蓋＝{m['cap_lower_h']+Hcu:.2f}，與蓋高 {Hc:g} 差 {m['cap_lower_h']+Hcu-Hc:.2f}（量測誤差）"]:
        tx.text(0, y, "・" + s, fontsize=8.5, va="top", color=RED); y -= 0.036
    y -= 0.02
    tx.text(0, y, "沒有讀數的照片", fontsize=11, weight="bold", va="top"); y -= 0.045
    for s in d["no_reading"]:
        tx.text(0, y, "・" + s, fontsize=8.5, va="top"); y -= 0.036

    b = os.path.splitext(os.path.basename(path))[0]
    od = os.path.join(os.path.dirname(path), "out"); os.makedirs(od, exist_ok=True)
    for e in ("png", "pdf"):
        fig.savefig(os.path.join(od, f"{b}.{e}"), dpi=150)
    print("ok", b)

if __name__ == "__main__":
    main(sys.argv[1])
