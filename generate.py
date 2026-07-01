from __future__ import annotations
import argparse, glob, json, os
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw, ImageFont, ImageFilter

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

def fit_font(draw, text, preferred_size, max_width, weight="black"):
    size = preferred_size
    while size >= 48:
        candidate = font(size, weight)
        box = draw.textbbox((0, 0), text, font=candidate)
        if box[2] - box[0] <= max_width:
            return candidate
        size -= 2
    return font(48, weight)

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

def paste_icon(canvas, name, box):
    x,y,w,h = box
    icon_path = ROOT / "icons" / WASTE_TO_ICON.get(name, "none.png")
    icon = Image.open(icon_path).convert("RGBA")
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

    img = Image.new("RGBA", (cw, ch), (255,255,255,0))
    shadow = Image.new("RGBA", (cw, ch), (255,255,255,0))
    sd = ImageDraw.Draw(shadow)
    m = d["margin"]
    sd.rounded_rectangle((m,m,cw-m,ch-m), radius=d["card_radius"], fill=(0,0,0,30))
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    img.alpha_composite(shadow)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((m,m,cw-m,ch-m), radius=d["card_radius"], fill=(255,255,255,255), outline=(220,220,220,255), width=2)

    date_text = f"{today.year}年{today.month}月{today.day}日（{JP_WEEKDAYS[today.weekday()]}）"
    hname = holiday_name(today)
    draw.text((d["date_x"], d["date_y"]), date_text, font=font(56, "bold"), fill=(20,20,20))
    draw.line((d["header_separator_x"], 94, d["header_separator_x"], 151), fill=(205,205,205), width=2)
    if hname:
        draw.text((d["holiday_x"], d["date_y"]+5), hname, font=font(38, "bold"), fill=(25,25,25))
    draw.line((84, d["top_line_y"], cw-84, d["top_line_y"]), fill=(210,210,210), width=2)

    today_gomi = collection_for(today, today_data)
    tomorrow_gomi = collection_for(tomorrow, tomorrow_data)

    paste_icon(img, today_gomi, d["today_icon_box"])
    draw.text((d["today_label_x"], d["today_label_y"]), "今日", font=font(72, "bold"), fill=(20,20,20))
    today_font = fit_font(draw, today_gomi, 136, d["today_text_max_width"], "black")
    draw.text((d["today_text_x"], d["today_text_y"]), today_gomi, font=today_font, fill=(20,20,20))

    # dotted divider
    y = d["divider_y"]
    for x in range(85, cw-85, 14):
        draw.line((x, y, x+5, y), fill=(205,205,205), width=4)

    tx, ty = d["tomorrow_x"], d["tomorrow_y"]
    draw.text((tx, ty), "明日", font=font(42, "bold"), fill=(25,25,25))
    draw.text((tx, ty+55), tomorrow_gomi, font=font(42, "bold"), fill=(25,25,25))
    draw.line(tuple(d["tomorrow_divider"]), fill=(210,210,210), width=2)
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
