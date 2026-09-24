#!/usr/bin/env python3

import os
import re
import subprocess

HOME = os.path.expanduser("~")
THEME_PATH = os.path.join(HOME, ".config/rofi/mystyles/menu.rasi")

ROFI_CMD = ["rofi", "-dmenu", "-i", "-markup-rows", "-p", "Bluetooth Manager"]
if os.path.exists(THEME_PATH):
    ROFI_CMD += ["-theme", THEME_PATH]


def run_rofi(prompt, items):
    """Вызывает rofi и возвращает выбранную строку текста."""
    cmd = ROFI_CMD.copy()
    if prompt != "Bluetooth Manager":
        try:
            p_idx = cmd.index("-p")
            cmd[p_idx + 1] = prompt
        except ValueError:
            pass

    res = subprocess.run(
        cmd,
        input="\n".join(items),
        text=True,
        capture_output=True
    ).stdout.strip()
    return res


def get_power_status():
    try:
        out = subprocess.run(["bluetoothctl", "show"], text=True, capture_output=True).stdout
        return "yes" if "Powered: yes" in out else "no"
    except Exception:
        return "no"


def parse_line_for_device(line):
    """Извлекает MAC-адрес и имя устройства из вывода bluetoothctl."""
    line = re.sub(r'\x1b\[[0-9;]*m', '', line)  # Очистка от ANSI-цветов
    match = re.search(r'([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5})\s+(.*)', line)
    if match:
        mac = match.group(1).strip()
        name = match.group(2).strip()
        return mac, name
    return None


def get_devices(mode="all"):
    """Получает подключенные или все известные устройства."""
    if mode == "connected":
        out = subprocess.run(["bluetoothctl", "devices"], text=True, capture_output=True).stdout
        devices = []
        for line in out.strip().split("\n"):
            parsed = parse_line_for_device(line)
            if parsed:
                mac, name = parsed
                info = subprocess.run(["bluetoothctl", "info", mac], text=True, capture_output=True).stdout
                if "Connected: yes" in info:
                    devices.append((mac, name))
        return devices
    else:
        # Изменили paired-devices на обычный devices, чтобы видеть ВСЕ сохраненные/наушники
        out = subprocess.run(["bluetoothctl", "devices"], text=True, capture_output=True).stdout
        devices = []
        for line in out.strip().split("\n"):
            parsed = parse_line_for_device(line)
            if parsed:
                devices.append(parsed)
        return devices


def device_actions_menu(mac, name):
    """Подменю управления выбранным устройством."""
    info = subprocess.run(["bluetoothctl", "info", mac], text=True, capture_output=True).stdout
    is_connected = "Connected: yes" in info

    items = []
    if is_connected:
        items.append("<span size='20000' foreground='#ff5555'>󰂭</span>    Disconnect")
    else:
        items.append("<span size='20000' foreground='#50fa7b'>󰂱</span>    Connect")

    items.append("<span size='20000' foreground='#ff5555'>󰆴</span>    Remove / Unpair")
    items.append("<span size='20000' foreground='#6272a4'>󰅖</span>    Back")

    act = run_rofi(f"Device: {name}", items).lower()

    if not act or "back" in act:
        return

    if "connect" in act and "disconnect" not in act:
        subprocess.run(["bluetoothctl", "connect", mac])
    elif "disconnect" in act:
        subprocess.run(["bluetoothctl", "disconnect", mac])
    elif "remove" in act:
        subprocess.run(["bluetoothctl", "remove", mac])


def handle_device_selection(selected):
    if not selected or "back" in selected.lower():
        return False
    
    mac_match = re.search(r'([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5})', selected)
    if mac_match:
        mac = mac_match.group(1)
        name = re.sub(r'<[^>]*>', '', selected).strip()
        if " | " in name:
            name = name.split(" | ")[0].strip()
        device_actions_menu(mac, name)
        return True
    return False


def main():
    while True:
        power_status = get_power_status()

        if power_status == "yes":
            power_str = "<span size='20000' foreground='#ff5555'></span>    Turn Off Bluetooth"
        else:
            power_str = "<span size='20000' foreground='#ff5555'></span>    Turn On Bluetooth"

        menu_items = [
            power_str,
            "<span size='20000' foreground='#ff5555'>󰂱</span>    Connected Devices",
            "<span size='20000' foreground='#ff5555'>󰌷</span>    All Known Devices" # Переименовали пункт
        ]

        act = run_rofi("Bluetooth Manager", menu_items).lower()

        if not act:
            break

        if "turn off" in act or "turn on" in act:
            do = "off" if power_status == "yes" else "on"
            subprocess.run(["bluetoothctl", "power", do])

        elif "connected" in act:
            while True:
                devices = get_devices(mode="connected")
                
                # Добавляем пункт Back в начало списка элементов Rofi
                dev_strings = ["<span size='20000' foreground='#6272a4'>󰅖</span>    Back"]
                
                if devices:
                    dev_strings += [f"<span size='20000' foreground='#8be9fd'>󰂱</span>    {name} | <span foreground='#6272a4'>{mac}</span>" for mac, name in devices]
                else:
                    dev_strings += ["<span foreground='#ff5555'>No connected devices found</span>"]
                
                selected = run_rofi("Connected Devices", dev_strings)
                
                if not selected or "back" in selected.lower() or "no connected" in selected.lower():
                    break
                
                handle_device_selection(selected)

        elif "all known" in act or "paired" in act:
            while True:
                devices = get_devices(mode="all")
                
                # Добавляем пункт Back в начало списка элементов Rofi
                dev_strings = ["<span size='20000' foreground='#6272a4'>󰅖</span>    Back"]
                
                if devices:
                    dev_strings += [f"<span size='20000' foreground='#ffb86c'>󰌷</span>    {name} | <span foreground='#6272a4'>{mac}</span>" for mac, name in devices]
                else:
                    dev_strings += ["<span foreground='#ff5555'>No devices found</span>"]
                
                selected = run_rofi("All Known Devices", dev_strings)
                
                if not selected or "back" in selected.lower() or "no devices" in selected.lower():
                    break
                
                handle_device_selection(selected)


if __name__ == "__main__":
    main()
