#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil

from pathlib import Path
from PIL import Image, ImageFilter, ImageDraw, ImageOps

WALLPAPERS_DIR = "/home/kn1ver/Изображения/wallpapers"
THUMBS_DIR = Path.home() / ".cache" / "walls-thumbs"


def generate_thumbnails():

    THUMBS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    for wall in Path(WALLPAPERS_DIR).iterdir():

        if "active_" in wall.name:
            continue

        thumb_path = THUMBS_DIR / f"{wall.stem}.png"

        try:

            if (
                thumb_path.exists()
                and thumb_path.stat().st_mtime >= wall.stat().st_mtime
            ):
                continue

            img = Image.open(wall).convert("RGBA")

            thumb = ImageOps.fit(
                img,
                (480, 270),
                method=Image.Resampling.LANCZOS
            )

            mask = Image.new("L", (480, 270), 0)

            draw = ImageDraw.Draw(mask)

            draw.rounded_rectangle(
                (0, 0, 479, 269),
                radius=20,
                fill=255
            )

            thumb.putalpha(mask)

            thumb.save(thumb_path, "PNG")

        except Exception as e:
            print(f"Thumbnail error: {wall}: {e}")

def get_rofi_wall_list():

    walls = []

    for wall in sorted(Path(WALLPAPERS_DIR).iterdir()):

        if "active_" in wall.name:
            continue

        thumb = THUMBS_DIR / f"{wall.stem}.png"

        walls.append(
            f"{wall.name}\0icon\x1f{thumb}"
        )

    return walls

args = sys.argv
act = " ".join([i.lower() for i in args])

generate_thumbnails()
walls = get_rofi_wall_list()

run = [
    [
        "rofi",
        "-dmenu",
        "-i",
        "-show-icons",
        "-markup-rows",
        "-p",
        "Walls",
        "-theme",
        "/home/kn1ver/.config/rofi/mystyles/wallpaper_picker.rasi"
    ],
    [
        "rofi",
        "-dmenu",
        "-i",
        "-markup-rows",
        "-p",
        "Walls",
        "-theme",
        "/home/kn1ver/.config/rofi/mystyles/menu.rasi"]
]

def lock_img_save(img, res):
    img.save(f"{WALLPAPERS_DIR}/active_lock_{res[0]}_{res[1]}.png", "png")

def blur_hyprlock_shape(
    img,
    monitor_w=2560,
    monitor_h=1440,

    shape_w=650,
    shape_h=650,
    rounding=25,

    pos_x=0,
    pos_y=0,

    blur_radius=20,
):
    img_w, img_h = img.size

    # =========================
    # Повторяем cover-алгоритм
    # =========================
    scale = max(
        monitor_w / img_w,
        monitor_h / img_h
    )

    scaled_w = img_w * scale
    scaled_h = img_h * scale

    crop_x = (scaled_w - monitor_w) / 2
    crop_y = (scaled_h - monitor_h) / 2

    # =========================
    # Центр фигуры на экране
    # =========================
    center_x = monitor_w / 2 + pos_x
    center_y = monitor_h / 2 + pos_y

    # =========================
    # Координаты фигуры на экране
    # =========================
    screen_x1 = center_x - shape_w / 2
    screen_y1 = center_y - shape_h / 2

    screen_x2 = screen_x1 + shape_w
    screen_y2 = screen_y1 + shape_h

    # =========================
    # Переводим в координаты
    # исходного изображения
    # =========================
    x1 = (screen_x1 + crop_x) / scale
    y1 = (screen_y1 + crop_y) / scale

    x2 = (screen_x2 + crop_x) / scale
    y2 = (screen_y2 + crop_y) / scale

    x1 = round(x1)
    y1 = round(y1)
    x2 = round(x2)
    y2 = round(y2)

    # =========================
    # Блюр области
    # =========================
    region = img.crop((x1, y1, x2, y2))

    blurred_region = region.filter(
        ImageFilter.GaussianBlur(blur_radius)
    )

    # =========================
    # Маска со скруглением
    # =========================
    mask = Image.new("L", region.size, 0)

    draw = ImageDraw.Draw(mask)

    source_rounding = round(rounding / scale)

    draw.rounded_rectangle(
        (
            0,
            0,
            region.width - 1,
            region.height - 1
        ),
        radius=source_rounding,
        fill=255
    )

    img.paste(
        blurred_region,
        (x1, y1),
        mask
    )

    return img

def lock_img_blur(img, res=(2560, 1440)):

    shapes = [
        (650, 650, 0, 0),
        (350, 140, -150, 410),
        (285, 140, 182.5, 410),
    ]

    for w, h, x, y in shapes:
        img = blur_hyprlock_shape(
            img=img,
            monitor_h=res[1],
            monitor_w=res[0],

            shape_w=w,
            shape_h=h,

            pos_x=x,
            pos_y=y
        )

    return img


if not act[len('/home/kn1ver/.local/bin/walls'):]:
    act = subprocess.run(
            run[1],
            cwd="/home/kn1ver",
            input="\n".join([
                "<span size='20000' foreground='#ff5555'>󰑓</span>    Reload Wallpapers",
                "<span size='20000' foreground='#ff5555'>󱪰</span>    Change Lockscreen",
                "<span size='20000' foreground='#ff5555'>󱨀</span>    Change Desktop"]),
            text=True,
            capture_output=True
        ).stdout.strip().lower()

for i in walls:
    print(i)

if "lockscreen" in act:
    
    selected = subprocess.run(
        run[0],
        cwd="/home/kn1ver",
        input="\n".join(walls),
        text=True,
        capture_output=True
    ).stdout.strip()

    if selected:
        print(f"Выбрано: {selected}")
    else:
        print("Отмена")

    new_pic_path = f"{WALLPAPERS_DIR}/{selected}"

    new_pic = Image.open(new_pic_path)
    
    new_pic = lock_img_blur(new_pic, res=(2560, 1440))
    lock_img_save(new_pic, res=(2560, 1440))

    new_pic = lock_img_blur(new_pic, res=(1920, 1080))    
    lock_img_save(new_pic, res=(1920, 1080))

elif "reload" in act:
    kill = ["awww", "kill"] 
    subprocess.run(kill)

    start = ["awww-daemon"]
    subprocess.run(start)

elif "desktop" in act:

    selected = subprocess.run(
        run[0],
        cwd="/home/kn1ver",
        input="\n".join(walls),
        text=True,
        capture_output=True
    ).stdout.strip()

    if selected:
        print(f"Выбрано: {selected}")
    else:
        print("Отмена")

    awww_cmd = ["awww", "img", f"{WALLPAPERS_DIR}/{selected}"]
    subprocess.run(awww_cmd)


    REPO = "/home/kn1ver/hyprland-dotfiles/"
    SOURCE_IMAGE = f"{WALLPAPERS_DIR}/{selected}"
    TARGET_IMAGE = f"{REPO}/wallpapers/active.png"

    subprocess.run(
        ["git", "pull", "--rebase"],
        cwd=REPO,
        check=True
    )

    shutil.copy2(
        SOURCE_IMAGE,
        TARGET_IMAGE
    )

    subprocess.run(
        ["git", "add", "wallpapers/active.png"],
        cwd=REPO,
        check=True
    )

    status = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=REPO
    )

    if status.returncode != 0:
        subprocess.run(
            ["git", "commit", "-m", f"Wallpaper: {selected}"],
            cwd=REPO,
            check=True
        )

        subprocess.run(
            ["git", "push"],
            cwd=REPO,
            check=True
        )

else:
    print("Nothing")
