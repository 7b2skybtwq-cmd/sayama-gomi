from __future__ import annotations
import argparse, glob, json, os
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw, ImageFont

try:
    import jpholiday
except Exception:
    jpholiday = None

ROOT = Path(__file__).resolve().parent
WASTE_TO_ICON = {
    "もやすごみ": "burnable.png",
    "びん・缶": "bottles_cans.png",
    "ペットボトル": "pet.png",
    "プラスチック": "plastic.png",
    "古紙・古布": "paper_cloth.png",
    "もやさないごみ": "nonburnable.png",
    "収集なし": "none.png",
}
JP_WEEKDAYS = "月火水木金土日"
FONT_PATHS = {
  "regular": [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/*W4.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
  ],
  "bold": [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/System/Library/Fonts/*W6.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
  ],
  "black": [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc",
    "/System/Library/Fonts/*W8.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
  ],
}

def font(size:int, weight:str="regular"):
    for pattern in FONT_PATHS[weight]:
        for path in glob.glob(pattern):
            if Path(path).exists():
                return ImageFont.truetype(path, size=size)
    raise FileNotFoundError("Japanese font not found. Install fonts-noto-cjk.")

def fit_font(draw, text, preferred_size, max_width, weight="black", min_size=8):
    size = preferred_size
    while size >= min_size:
        candidate = font(size, weight)
        box = draw.textbbox((0, 0), text, font=candidate)
        if box[2] - box[0] <= max_width:
            return candidate
        size -= 1
    return font(min_size, weight)

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def collection_for(date, data):
    return data.get("collections", {}).get(date.isoformat(), "収集なし")

def load_schedule(date, explicit_path=None):
    path = Path(explicit_path) if explicit_path else ROOT / "data" / f"schedule-{date.year}.json"
    return load_json(path) if path.exists() else {"collections": {}}

def holiday_name(date):
    if jpholiday is None:
        return ""
    return jpholiday.is_holiday_name(date) or ""

def draw_center(draw, xy, text, fnt, fill=(25,25,25)):
    x, y = xy
    box = draw.textbbox((0,0), text, font=fnt)
    tw = box[2]-box[0]
    draw.text((x - tw/2, y), text, font=fnt, fill=fill)

def draw_right(draw, xy, text, fnt, fill=(25,25,25)):
    x, y = xy
    box = draw.textbbox((0, 0), text, font=fnt)
    draw.text((x - (box[2] - box[0]), y), text, font=fnt, fill=fill)

def paste_icon(canvas, name, box):
    x,y,w,h = box
    icon_path = ROOT / "icons" / WASTE_TO_ICON.get(name, "none.png")
    icon = Image.open(icon_path).convert("RGBA")
    alpha_box = icon.getchannel("A").getbbox()
    if alpha_box:
        icon = icon.crop(alpha_box)
    icon.thumbnail((w,h), Image.Resampling.LANCZOS)
    px = int(x + (w - icon.width)/2)
    py = int(y + (h - icon.height)/2)
    canvas.alpha_composite(icon, (px, py))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="YYYY-MM-DD。未指定なら今日（JST）")
    ap.add_argument("--schedule", default=None, help="data/schedule-YYYY.json を直接指定可")
    ap.add_argument("--output", default=None)
    args = ap.parse_args()

    cfg = load_json(ROOT / "config.json")
    timezone = ZoneInfo(cfg.get("timezone", "Asia/Tokyo"))
    today = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else datetime.now(timezone).date()
    tomorrow = today + timedelta(days=1)
    today_data = load_schedule(today, args.schedule)
    tomorrow_data = today_data if args.schedule or tomorrow.year == today.year else load_schedule(tomorrow)
    d = cfg["design"]
    cw, ch = cfg["canvas"]["width"], cfg["canvas"]["height"]

    img = Image.new("RGBA", (cw, ch), (255,255,255,255))
    m = d["margin"]
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(
        (m,m,cw-m-1,ch-m-1),
        radius=d["card_radius"],
        fill=(255,255,255,255),
        outline=(190,190,190,255),
        width=1,
    )

    date_text = f"{today.year}年{today.month}月{today.day}日（{JP_WEEKDAYS[today.weekday()]}）"
    hname = holiday_name(today)
    draw.text((d["date_x"], d["date_y"]), date_text, font=font(d["date_font_size"], "bold"), fill=(10,10,10))
    draw.line(tuple(d["header_separator"]), fill=(195,195,195), width=1)
    if hname:
        draw.text((d["holiday_x"], d["holiday_y"]), hname, font=font(d["holiday_font_size"], "bold"), fill=(20,20,20))
    draw.line(tuple(d["top_line"]), fill=(195,195,195), width=1)

    today_gomi = collection_for(today, today_data)
    tomorrow_gomi = collection_for(tomorrow, tomorrow_data)

    paste_icon(img, today_gomi, d["today_icon_box"])
    draw.text(
        (d["today_label_x"], d["today_label_y"]),
        "今日",
        font=font(d["today_label_font_size"], "bold"),
        fill=(10,10,10),
    )
    today_font = fit_font(
        draw,
        today_gomi,
        d["today_text_font_size"],
        d["today_text_max_width"],
        "black",
        d["today_text_min_font_size"],
    )
    draw.text((d["today_text_x"], d["today_text_y"]), today_gomi, font=today_font, fill=(5,5,5))

    # dotted divider
    y = d["divider_y"]
    for x in range(d["divider_x1"], d["divider_x2"], d["divider_step"]):
        draw.line((x, y, x+d["divider_dash"], y), fill=(175,175,175), width=1)

    tomorrow_label_font = font(d["tomorrow_label_font_size"], "bold")
    tomorrow_text_font = fit_font(
        draw,
        tomorrow_gomi,
        d["tomorrow_text_font_size"],
        d["tomorrow_text_max_width"],
        "bold",
        d["tomorrow_text_min_font_size"],
    )
    tomorrow_box = draw.textbbox((0, 0), tomorrow_gomi, font=tomorrow_text_font)
    tomorrow_left = d["tomorrow_right"] - (tomorrow_box[2] - tomorrow_box[0])
    draw.text((tomorrow_left, d["tomorrow_label_y"]), "明日", font=tomorrow_label_font, fill=(10,10,10))
    draw_right(draw, (d["tomorrow_right"], d["tomorrow_text_y"]), tomorrow_gomi, tomorrow_text_font, fill=(10,10,10))
    draw.line(tuple(d["tomorrow_divider"]), fill=(195,195,195), width=1)
    paste_icon(img, tomorrow_gomi, d["tomorrow_icon_box"])

    out = Path(args.output or cfg["output"])
    if not out.is_absolute():
        out = ROOT / out
    tmp = out.with_name(f".{out.name}.tmp")
    img.convert("RGB").save(tmp, format="PNG", optimize=True)
    os.replace(tmp, out)
    print(f"generated: {out}  today={today_gomi} tomorrow={tomorrow_gomi}")

if __name__ == "__main__":
    main()
