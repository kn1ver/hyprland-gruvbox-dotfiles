#!/usr/bin/env sh

export HYPRLAND_INSTANCE_SIGNATURE="$HYPRLAND_INSTANCE_SIGNATURE"

TARGET_KEYBOARD="$1"

/usr/bin/hyprctl devices -j | \
/usr/bin/jq -r --arg kb "$TARGET_KEYBOARD" '.keyboards[] | select(.name == $kb) | .active_keymap' | awk -F'[()]' '{print toupper($2 ? $2 : substr($1,1,2))}'
