#!/usr/bin/env sh
echo "SIG=$HYPRLAND_INSTANCE_SIGNATURE" > /tmp/hyprlock_test
export HYPRLAND_INSTANCE_SIGNATURE="$HYPRLAND_INSTANCE_SIGNATURE"

/usr/bin/hyprctl devices -j | /usr/bin/jq -r '.keyboards[3].active_keymap' | awk -F'[()]' '{print toupper($2 ? $2 : substr($1,1,2))}'
