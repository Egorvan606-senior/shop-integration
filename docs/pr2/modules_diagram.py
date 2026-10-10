"""Схема модульной структуры модуля интеграции (ПР №2), строгий стиль.

Блоки — прямоугольники, связи — только горизонтальные и вертикальные отрезки.
Внешние системы обозначены символами ГОСТ 19.701-90: «документ» (файл выгрузки),
«данные» (обмен через сеть), «запоминающее устройство с прямым доступом» (БД).

Запуск:  python modules_diagram.py   ->  modules.png
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Ellipse, FancyArrowPatch
from matplotlib.path import Path
from matplotlib.patches import PathPatch

plt.rcParams["font.family"] = "Liberation Serif"
LW = 1.1
FS = 8.6        # текст в блоках
FS_LBL = 7.6    # подписи связей
INK = "black"

fig = plt.figure(figsize=(7.0, 9.4))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 100)
ax.set_ylim(0, 134)
ax.axis("off")


def box(x0, y0, x1, y1, text, ls="-", bold=False):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, lw=LW, ls=ls, ec=INK))
    ax.text((x0 + x1) / 2, (y0 + y1) / 2, text, ha="center", va="center", fontsize=FS,
            fontweight="bold" if bold else "normal", linespacing=1.25)


def frame(x0, y0, x1, y1, title, ls="-", lw=LW, where="top-right"):
    """Рамка модуля. Заголовок ставится туда, где его не пересекают линии связей."""
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, lw=lw, ls=ls, ec=INK))
    if where == "top-right":
        ax.text(x1 - 1.2, y1 - 1.0, title, ha="right", va="top", fontsize=FS, fontweight="bold")
    else:  # bottom-center
        ax.text((x0 + x1) / 2, y0 + 1.0, title, ha="center", va="bottom", fontsize=FS, fontweight="bold")


def data_symbol(x0, y0, x1, y1, text):          # «данные» — параллелограмм
    s = 2.5
    ax.add_patch(Polygon([(x0 + s, y1), (x1, y1), (x1 - s, y0), (x0, y0)], closed=True, fill=False, lw=LW, ec=INK))
    ax.text((x0 + x1) / 2, (y0 + y1) / 2, text, ha="center", va="center", fontsize=FS, linespacing=1.25)


def document_symbol(x0, y0, x1, y1, text):      # «документ» — нижняя граница волной
    h = 1.6
    w = x1 - x0
    verts = [(x0, y0 + h), (x0, y1), (x1, y1), (x1, y0 + h),
             (x0 + w * 0.7, y0 - h * 1.4), (x0 + w * 0.3, y0 + h * 3.4), (x0, y0 + h), (x0, y0 + h)]
    codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts, codes), fill=False, lw=LW, ec=INK))
    ax.text((x0 + x1) / 2, (y0 + y1) / 2 + 1.0, text, ha="center", va="center", fontsize=FS, linespacing=1.25)


def db_symbol(x0, y0, x1, y1, text):            # «запоминающее устройство с прямым доступом» — цилиндр
    e = 2.4
    cx, w = (x0 + x1) / 2, x1 - x0
    ax.add_patch(Ellipse((cx, y1 - e / 2), w, e, fill=False, lw=LW, ec=INK))
    ax.add_patch(matplotlib.patches.Arc((cx, y0 + e / 2), w, e, theta1=180, theta2=360, lw=LW, ec=INK))
    ax.plot([x0, x0], [y0 + e / 2, y1 - e / 2], color=INK, lw=LW)
    ax.plot([x1, x1], [y0 + e / 2, y1 - e / 2], color=INK, lw=LW)
    ax.text(cx, (y0 + y1) / 2 - 0.6, text, ha="center", va="center", fontsize=FS, linespacing=1.25)


def wire(points, label=None, lpos=None, ha="left", dashed=False):
    """Ортогональная линия по точкам; стрелка на последнем отрезке."""
    ls = (0, (4, 2.5)) if dashed else "-"
    xs, ys = zip(*points)
    ax.plot(xs[:-1] + (xs[-1],), ys[:-1] + (ys[-1],), color=INK, lw=LW, ls=ls, solid_capstyle="butt")
    ax.add_patch(FancyArrowPatch(points[-2], points[-1], arrowstyle="-|>", mutation_scale=9,
                                 color=INK, lw=0, shrinkA=0, shrinkB=0))
    if label:
        ax.text(lpos[0], lpos[1], label, ha=ha, va="center", fontsize=FS_LBL, linespacing=1.15,
                bbox=dict(fc="white", ec="none", pad=0.25))


# ---------------- Источники ----------------
ax.text(50, 132.6, "Источники данных", ha="center", va="center", fontsize=FS, fontweight="bold")
document_symbol(4, 120, 34, 130, "И1. Складская система\n(SFTP, файл CSV / XML)")
data_symbol(58, 120, 94, 130, "И2. Интернет-магазин\n(вебхуки о заказах)")

# ---------------- Модуль интеграции ----------------
frame(1, 20.5, 99, 117, "Модуль интеграции shop-integration (src/)", ls=(0, (8, 3, 2, 3)), lw=1.3, where="bottom-center")

frame(3, 85, 97, 112, "Модуль 1. Источник / Интерфейс")
box(6, 88, 32, 101, "connectors/sftp_client\nзагрузка файлов\nвыгрузки")
box(37, 88, 57, 101, "parsers/\nCSV, XML, JSON →\nмодели")
box(62, 88, 94, 101, "webhooks/receiver\nPOST /webhooks/orders\nпроверка подписи HMAC")

frame(3, 53, 97, 77, "Модуль 2. Бизнес-логика / Обработка")
box(5, 55, 26, 69, "services/\ncatalog_sync\nсинхронизация\nкаталога")
box(28, 55, 47, 69, "services/\nstock_calculator\nрасчёт\nостатков")
box(53, 55, 72, 69, "services/\norder_validator\nвалидация\nзаказов")
box(74, 55, 95, 69, "services/\norder_status_sync\nстатусы и\nтрек-номера")

frame(3, 25.5, 97, 45, "Модуль 3. Приёмник / Хранилище", where="bottom-center")
box(6, 30, 40, 39.5, "connectors/\nmarketplace_client\nREST-клиент маркетплейса")
box(43, 30, 57, 39.5, "utils/, config/\nлоги, повтор,\nпараметры", ls=(0, (3, 2)))
box(60, 30, 94, 39.5, "connectors/\ndb_repository\nзапись и чтение заказов")

# ---------------- Приёмники ----------------
data_symbol(6, 5, 40, 14, "П1. Сервер маркетплейса\n(REST API)")
db_symbol(60, 3.5, 94, 15, "П2. БД учётной\nсистемы (СУБД)")
ax.text(50, 1.2, "Приёмники данных", ha="center", va="center", fontsize=FS, fontweight="bold")

# ---------------- Поток А: остатки ----------------
wire([(19, 121.45), (19, 101)], "А1  SFTP, CSV/XML", (20.2, 104.5))
wire([(32, 94.5), (37, 94.5)], "А2", (33.2, 97.2))
wire([(46, 88), (46, 69)], "А3  StockItem[]", (47.2, 82.5))
wire([(30, 55), (30, 39.5)], "А4  остатки", (31.2, 50.5))
wire([(23, 30), (23, 14)], "А5  HTTPS PUT, JSON", (24.2, 17.8))

# ---------------- Поток Б: заказы ----------------
wire([(66, 120), (66, 101)], "Б1  HTTPS POST, JSON", (67.2, 104.5))
wire([(62, 94.5), (57, 94.5)], "Б2", (58.3, 97.2))
wire([(53, 88), (53, 80.5), (58, 80.5), (58, 69)], "Б3  Order", (59.2, 82.6))
wire([(53, 62), (47, 62)], None, dashed=True)
ax.text(50, 64.2, "Б6", ha="center", va="center", fontsize=FS_LBL)
wire([(64, 55), (64, 39.5)], "Б4  заказ", (65.2, 50.5))
wire([(70, 30), (70, 15)], "Б5  SQL INSERT", (71.2, 17.8))

# ---------------- Поток В: статусы и трек-номера ----------------
wire([(86, 15), (86, 30)], "В1  SQL SELECT", (87.2, 17.8))
wire([(90, 39.5), (90, 55)], "В2", (91.2, 50.5))
wire([(80, 55), (80, 47.5), (37, 47.5), (37, 39.5)], "В3", (46, 48.9))

# ---------------- Поток Г: каталог ----------------
wire([(40, 88), (40, 82.5), (15.5, 82.5), (15.5, 69)], "Г1  номенклатура", (16.7, 80.5))
wire([(12, 55), (12, 39.5)], "Г2  карточки", (13.2, 50.5))

fig.savefig("modules.png", dpi=220)
print("saved modules.png")
