#!/bin/bash

theme="$HOME/.config/rofi/powermenu/type-2/style-2.rasi"

chosen=$(printf "<span size='16000' foreground='#ff5555'></span>  Poweroff\n \
<span size='20000' foreground='#ff5555'>󰜉</span>  Reboot\n \
<span size='20000' foreground='#ff5555'>󰍃</span>  Lock\n"| \
rofi -dmenu -i -markup-rows -p "Power" -theme "$theme")

case "$chosen" in
    *Shutdown) systemctl poweroff ;;
    *Reboot) systemctl reboot ;;
    *Logout) hyprctl dispatch exit ;;
    *Lock) hyprlock ;;
esac
