"""Граф коммитов Git Flow для варианта 5 (по сценарию gitflow_demo.sh), строгий стиль.

Каждая ветка — горизонтальная линия на своей дорожке, время идёт слева направо.
Создание ветки и слияние изображаются только вертикальными и горизонтальными отрезками.

Запуск: python gitflow_graph.py   ->  gitflow_graph.png
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

plt.rcParams["font.family"] = "Liberation Serif"
INK, LW = "black", 1.6
FS, FS_SMALL = 15, 12.5
DASH = (0, (5, 3))

LANES = ["hotfix/1.0.1", "main", "release/2.0.0", "develop", "feature/crypto-module", "feature/key-storage"]
Y = {name: -1.6 * i for i, name in enumerate(LANES)}

# коммиты: id -> (x, ветка, подпись, вид) ; вид: c — обычный, m — коммит слияния, t — коммит с тегом
N = {
    "m0": (0.0, "main", "v1.0.0", "t"),
    "d0": (1.0, "develop", "", "c"),
    "a1": (2.0, "feature/crypto-module", "шифрование", "c"),
    "b1": (3.0, "feature/key-storage", "хранилище ключей", "c"),
    "a2": (4.0, "feature/crypto-module", "большие файлы", "c"),
    "a3": (5.0, "feature/crypto-module", "тесты", "c"),
    "b2": (5.0, "feature/key-storage", "ротация ключей", "c"),
    "d1": (6.0, "develop", "PR #12", "m"),
    "d2": (7.2, "develop", "PR #14", "m"),
    "r1": (8.2, "release/2.0.0", "версия 2.0.0", "c"),
    "r2": (9.4, "release/2.0.0", "fix > 2 ГБ", "c"),
    "h1": (10.4, "hotfix/1.0.1", "fix подписи", "c"),
    "h2": (11.4, "hotfix/1.0.1", "версия 1.0.1", "c"),
    "m1": (12.2, "main", "v1.0.1", "t"),
    "r3": (13.0, "release/2.0.0", "merge hotfix", "m"),
    "r4": (14.0, "release/2.0.0", "fix ключей", "c"),
    "r5": (15.0, "release/2.0.0", "CHANGELOG", "c"),
    "m2": (16.0, "main", "v2.0.0", "t"),
    "d3": (16.8, "develop", "back-merge", "m"),
}
# где ставить подпись коммита: a — над, b — под, l/r — над и левее/правее
LABEL_POS = {'m0': 'a', 'a1': 'a', 'b1': 'a', 'a2': 'a', 'a3': 'b', 'b2': 'b', 'd1': 'a', 'd2': 'r', 'r1': 'a', 'r2': 'b', 'h1': 'a', 'h2': 'b', 'm1': 'b', 'r3': 'b', 'r4': 'a', 'r5': 'b', 'm2': 'a', 'd3': 'b', 'd0': 'a'}

# создание ветки: (родитель, первый коммит новой ветки[, x момента создания])
BRANCH = [("m0", "d0"), ("d0", "a1"), ("d0", "b1"), ("d2", "r1"), ("m0", "h1", 9.95)]  # hotfix создаётся 24.09 от вершины main
# слияние: (последний коммит исходной ветки, коммит слияния в целевой ветке)
MERGE = [("b2", "d1"), ("a3", "d2"), ("h2", "m1"), ("h2", "r3"), ("r5", "m2"), ("r5", "d3")]
# линии веток между своими коммитами
LINE = {"main": ["m0", "m1", "m2"], "develop": ["d0", "d1", "d2", "d3"],
        "feature/crypto-module": ["a1", "a2", "a3"], "feature/key-storage": ["b1", "b2"],
        "release/2.0.0": ["r1", "r2", "r3", "r4", "r5"], "hotfix/1.0.1": ["h1", "h2"]}


def P(n):
    return N[n][0], Y[N[n][1]]


fig, ax = plt.subplots(figsize=(15, 9.6))

# подписи дорожек и тонкие направляющие
for name in LANES:
    ax.text(-0.75, Y[name], name, ha="right", va="center", fontsize=FS)
    ax.plot([-0.5, 17.4], [Y[name]] * 2, color="#BBBBBB", lw=0.6, ls=(0, (1, 3)), zorder=0)

# линии веток
for br, ids in LINE.items():
    xs = [N[i][0] for i in ids]
    ax.plot([min(xs), max(xs)], [Y[br]] * 2, color=INK, lw=LW * 1.4, zorder=1, solid_capstyle="butt")

# создание ветки: вертикаль от родителя до дорожки новой ветки, затем по дорожке до первого коммита
for item in BRANCH:
    parent, child = item[0], item[1]
    (x1, y1), (x2, y2) = P(parent), P(child)
    xb = item[2] if len(item) > 2 else x1          # момент создания ветки
    ax.plot([xb, xb, x2], [y1, y2, y2], color=INK, lw=LW, zorder=1, solid_joinstyle="miter")

# слияние: по дорожке исходной ветки до x коммита слияния, затем вертикаль со стрелкой
for src, dst in MERGE:
    (x1, y1), (x2, y2) = P(src), P(dst)
    end = y2 + (0.17 if y2 < y1 else -0.17)
    ax.plot([x1, x2], [y1, y1], color=INK, lw=LW, ls=DASH, zorder=1)
    ax.plot([x2, x2], [y1, end], color=INK, lw=LW, ls=DASH, zorder=1)
    ax.add_patch(FancyArrowPatch((x2, y1 + (y2 - y1) * 0.6), (x2, end),
                                 arrowstyle="-|>", mutation_scale=16, color=INK, lw=0, zorder=2))

# коммиты
for n, (x, br, label, kind) in N.items():
    y = Y[br]
    if kind == "t":
        ax.scatter([x], [y], s=210, marker="D", color=INK, zorder=3)
    elif kind == "m":
        ax.scatter([x], [y], s=120, marker="o", color=INK, zorder=3)
    else:
        ax.scatter([x], [y], s=120, marker="o", facecolor="white", edgecolor=INK, linewidth=LW, zorder=3)
    if label:
        side = LABEL_POS.get(n, "a")
        fw = "bold" if kind == "t" else "normal"
        if side == "a":
            ax.text(x, y + 0.3, label, ha="center", va="bottom", fontsize=FS_SMALL, fontweight=fw)
        elif side == "b":
            ax.text(x, y - 0.3, label, ha="center", va="top", fontsize=FS_SMALL, fontweight=fw)
        elif side == "r":  # над и правее — когда сверху и снизу к коммиту подходят линии
            ax.text(x + 0.15, y + 0.3, label, ha="left", va="bottom", fontsize=FS_SMALL, fontweight=fw)
        else:  # над и левее
            ax.text(x - 0.15, y + 0.3, label, ha="right", va="bottom", fontsize=FS_SMALL, fontweight=fw)

# период интеграционного тестирования — размерная линия над дорожкой hotfix
yb = Y["hotfix/1.0.1"] + 1.15
for xv in (8.2, 15.0):
    ax.plot([xv, xv], [Y["release/2.0.0"] + 0.25, yb + 0.15], color="#666666", lw=0.8, ls=(0, (2, 2)), zorder=0)
ax.annotate("", xy=(8.2, yb), xytext=(15.0, yb), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.0))
ax.text(11.6, yb + 0.12, "интеграционное тестирование релиза ≈ 1 месяц", ha="center", va="bottom", fontsize=FS_SMALL)

# ось времени
yt = Y["feature/key-storage"] - 1.0
ax.plot([-0.3, 17.3], [yt, yt], color=INK, lw=1.0)
for x, t in [(0, "01.09"), (2.0, "02.09"), (5.0, "09.09"), (6.0, "10.09"), (7.2, "11.09"), (8.2, "14.09"),
             (10.4, "24.09"), (13.0, "25.09"), (14.0, "02.10"), (16.0, "14.10")]:
    ax.plot([x, x], [yt - 0.08, yt + 0.08], color=INK, lw=1.0)
    ax.text(x, yt - 0.18, t, ha="center", va="top", fontsize=FS_SMALL)

# условные обозначения
yl = yt - 1.05
items = [("line", "ветка"), ("branch", "создание ветки"), ("merge", "слияние (--no-ff)"),
         ("c", "коммит"), ("m", "коммит слияния"), ("t", "коммит с тегом версии")]
x = 0.0
for kind, text in items:
    if kind == "line":
        ax.plot([x, x + 0.6], [yl, yl], color=INK, lw=LW * 1.4)
    elif kind == "branch":
        ax.plot([x, x, x + 0.6], [yl + 0.25, yl, yl], color=INK, lw=LW)
    elif kind == "merge":
        ax.plot([x, x + 0.6], [yl, yl], color=INK, lw=LW, ls=DASH)
        ax.add_patch(FancyArrowPatch((x + 0.3, yl), (x + 0.65, yl), arrowstyle="-|>", mutation_scale=14, color=INK, lw=0))
    elif kind == "c":
        ax.scatter([x + 0.3], [yl], s=100, facecolor="white", edgecolor=INK, linewidth=LW)
    elif kind == "m":
        ax.scatter([x + 0.3], [yl], s=100, color=INK)
    else:
        ax.scatter([x + 0.3], [yl], s=160, marker="D", color=INK)
    ax.text(x + 0.85, yl, text, ha="left", va="center", fontsize=FS_SMALL)
    x += 1.25 + len(text) * 0.17

ax.set_xlim(-4.6, 17.9)
ax.set_ylim(yl - 0.6, Y["hotfix/1.0.1"] + 1.9)
ax.axis("off")
plt.tight_layout()
plt.savefig("gitflow_graph.png", dpi=150)
print("saved gitflow_graph.png")
