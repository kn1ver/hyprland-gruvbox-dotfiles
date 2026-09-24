#!/usr/bin/env python3

import subprocess
from pathlib import Path
from PIL import Image, ImageFilter, ImageDraw, ImageOps

IMAGE_DIR = Path.home() / ".cache" / "calendar-months"

run =[
    "rofi",
    "-dmenu",
    "-i",
    "-show-icons",
    "-markup-rows",
    "-p",
    "Calendar",
    "-theme",
    "/home/kn1ver/.config/rofi/mystyles/calendar.rasi"
]

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
months_icons = []


for month in months:
    thumb = IMAGE_DIR / f"{month.lower()}.png"

    if not thumb.exists():
        img = Image.open(thumb).convert("RGBA")
        mask = Image.new("L", (230, 240), 0)
        draw = ImageDraw.Draw(mask)

        draw.rounded_rectangle(
            (0, 0, 229, 239),
            radius=20,
            fill=255
        )

        img.putalpha(mask)
        img.save(thumb, "PNG")

    months_icons.append(
        f"{month}\0icon\x1f{thumb}"
    )


chosen_month = subprocess.run(
    run,
    cwd="/home/kn1ver",
    input="\n".join(months_icons),
    text=True,
    capture_output=True
).stdout.strip()
