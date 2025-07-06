import os
import shutil
import sys
import time
import ctypes
import threading
import subprocess

GREEN = "\033[92m"
CYAN = "\033[96m"
RED = "\033[91m"
RESET = "\033[0m"

os.system("chcp 1251 >nul")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def spinner(msg):
    symbols = ['|', '/', '-', '\\']
    idx = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r{CYAN}{msg} {symbols[idx % len(symbols)]}{RESET}")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * (len(msg) + 5) + "\r")

def clean_temp(path):
    try:
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                except: pass
            for name in dirs:
                try:
                    shutil.rmtree(os.path.join(root, name), ignore_errors=True)
                except: pass
    except: pass

def run_powershell(cmd):
    try:
        subprocess.run(["powershell", "-Command", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except: pass

def clear_recycle_bin():
    run_powershell("Clear-RecycleBin -Force")

def clear_software_distribution():
    os.system("net stop wuauserv >nul 2>&1")
    os.system("net stop bits >nul 2>&1")
    clean_temp(r"C:\Windows\SoftwareDistribution\Download")
    os.system("net start wuauserv >nul 2>&1")
    os.system("net start bits >nul 2>&1")

if not is_admin():
    print(f"{RED}❌ Требуются права администратора. Перезапускаем...{RESET}")
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    sys.exit()

print(f"{GREEN}\n🧹 Чистильщик Windows\n{RESET}")

tasks = [
    ("Удаление %TEMP%", lambda: clean_temp(os.environ.get("TEMP", ""))),
    ("Удаление C:\\Windows\\Temp", lambda: clean_temp(r"C:\Windows\Temp")),
    ("Очистка Prefetch", lambda: clean_temp(r"C:\Windows\Prefetch")),
    ("Очистка корзины", clear_recycle_bin),
    ("Очистка кэша обновлений", clear_software_distribution)
]

for label, func in tasks:
    stop_event = threading.Event()
    spin_thread = threading.Thread(target=spinner, args=(label,))
    spin_thread.start()
    func()
    stop_event.set()
    spin_thread.join()
    print(f"{GREEN}✅ {label} — выполнено.{RESET}")

print(f"\n{GREEN}✅ Очистка завершена! Спасибо за доверие — xselid был тут.{RESET}")
os.system("pause")
