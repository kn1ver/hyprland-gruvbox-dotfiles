#!/usr/bin/env python3

import subprocess
import shutil
import os

# Пути к твоим конфигам
CONFIG_DIR = "/etc/sing-box"
CONF_1 = os.path.join(CONFIG_DIR, "ru-to-is.json")
CONF_2 = os.path.join(CONFIG_DIR, "ru-to-fi.json")
CONF_3 = os.path.join(CONFIG_DIR, "fi-bypass.json")
CONF_4 = os.path.join(CONFIG_DIR, "is-bypass.json")
MAIN_CONF = os.path.join(CONFIG_DIR, "main.json")

systemctl_output = subprocess.run(
    ["systemctl"],
    capture_output=True,
    text=True,
    check=True
).stdout.splitlines()

is_running = any("sing-box" in line for line in systemctl_output)

current_profile = "Unknown"
if os.path.exists(MAIN_CONF):
    try:
        with open(MAIN_CONF, 'r') as f_main, open(CONF_1, 'r') as f_1:
            if f_main.read() == f_1.read():
                current_profile = "RU to IS"
    except Exception:
        pass
    
    try:
        with open(MAIN_CONF, 'r') as f_main, open(CONF_2, 'r') as f_2:
            if f_main.read() == f_2.read():
                current_profile = "RU to FI"
    except Exception:
        pass

    try:
        with open(MAIN_CONF, 'r') as f_main, open(CONF_3, 'r') as f_2:
            if f_main.read() == f_2.read():
                current_profile = "FI Bypass"
    except Exception:
        pass

    try:
        with open(MAIN_CONF, 'r') as f_main, open(CONF_4, 'r') as f_2:
            if f_main.read() == f_2.read():
                current_profile = "IS Bypass"
    except Exception:
        pass
    
    # with open(MAIN_CONF, 'r') as c_main:
    #     c_1 = open(CONF_1, 'r')
    #     c_2 = open(CONF_2, 'r')
    #     c_3 = open(CONF_3, 'r')
    #     c_4 = open(CONF_4, 'r')

    #     if c_main.read() == c_1.read(): current_profile = "RU to IS"
    #     elif c_main.read() == c_2.read(): current_profile = "RU to FI"
    #     elif c_main.read() == c_3.read(): current_profile = "FI Bypass"
    #     elif c_main.read() == c_4.read(): current_profile = "IS Bypass"

    #     c_1.close()
    #     c_2.close()
    #     c_3.close()
    #     c_4.close()


def switch_pofile(conf):
    try:
        subprocess.run([
            "sudo",
            "/usr/local/bin/switch-singbox",
            conf
        ])
    except Exception as e: print(e)


status = f"On ({current_profile})" if is_running else "Off"
run =[
    "rofi",
    "-dmenu",
    "-i",
    "-markup-rows",
    "-p",
    f"Sing-box: {status}",
    "-theme",
    "/home/kn1ver/.config/rofi/mystyles/proxy.rasi"
]

menu = [
    "<span size='20000' foreground='#ff5555'>󰮫</span>    Switch Proxy",
    "<span size='20000' foreground='#ff5555'>󰑓</span>    Restart Proxy"
]
if is_running: menu.append("<span size='20000' foreground='#ff5555'></span>    Turn Off Proxy")
else: menu.append("<span size='20000' foreground='#ff5555'></span>    Turn On Proxy")

act = subprocess.run(
            run,
            cwd="/home/kn1ver",
            input="\n".join(menu),
            text=True,
            capture_output=True
        ).stdout.strip().lower()

if "restart" in act:
    restart_cmd = ["sudo", "systemctl", "restart", "sing-box"]
    subprocess.run(restart_cmd)

elif "on" in act:
    turn_on_cmd = ["sudo", "systemctl", "start", "sing-box"]
    subprocess.run(turn_on_cmd)

elif "off" in act:
    turn_off_cmd = ["sudo", "systemctl", "stop", "sing-box"]
    subprocess.run(turn_off_cmd)

elif "switch" in act:
    server = subprocess.run(
        run,
        cwd="/home/kn1ver",
        input="\n".join([
            "<span size='20000' foreground='#ff5555'>1.</span>   RU to IS",
            "<span size='20000' foreground='#ff5555'>2.</span>   RU to FI",
            "<span size='20000' foreground='#ff5555'>3.</span>   FI Bypass",
            "<span size='20000' foreground='#ff5555'>4.</span>   IS Bypass"
        ]),
        text=True,
        capture_output=True
    ).stdout.strip().lower()
    
    if "ru to is" in server:
        switch_pofile(CONF_1)

    elif "ru to fi" in server:
        switch_pofile(CONF_2)
        
    elif "fi bypass" in server:
        switch_pofile(CONF_3)
    
    elif "is bypass" in server:
        switch_pofile(CONF_4)
