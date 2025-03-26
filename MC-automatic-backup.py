import os
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
import zipfile

# 全局变量
backup_count = 0
stop_backup = False

def backup_directory(dir_path, backup_dir):
    global backup_count

    if not os.path.isdir(dir_path):
        update_status(f"错误: 目录 {dir_path} 不存在")
        return

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # 创建带有时间戳的备份文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_file_name = f"backup_{timestamp}.zip"
    backup_path = os.path.join(backup_dir, backup_file_name)

    # 压缩目录
    try:
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=dir_path)
                    try:
                        zipf.write(file_path, arcname=arcname)
                    except PermissionError:
                        update_status(f"文件 {file_path} 被占用，无法备份")
    except Exception as e:
        update_status(f"备份失败: {e}")
        return
    
    backup_count += 1
    update_status(f"已备份 {backup_count} 次。")

def select_directory():
    dir_path = filedialog.askdirectory(title="选择要备份的目录")
    if dir_path:
        dir_entry.delete(0, tk.END)
        dir_entry.insert(0, dir_path)

def select_backup_dir():
    backup_dir = filedialog.askdirectory(title="选择备份文件保存的目录")
    if backup_dir:
        backup_dir_entry.delete(0, tk.END)
        backup_dir_entry.insert(0, backup_dir)

def perform_backup():
    dir_path = dir_entry.get()
    backup_dir = backup_dir_entry.get()
    if dir_path and backup_dir:
        backup_directory(dir_path, backup_dir)
    else:
        messagebox.showwarning("警告", "请指定目录和备份目录")

def start_auto_backup():
    global stop_backup

    try:
        interval = int(interval_entry.get())
        if interval <= 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning("警告", "请输入有效的时间间隔（分钟）")
        return

    stop_backup = False
    threading.Thread(target=auto_backup, args=(interval,), daemon=True).start()
    messagebox.showinfo("信息", f"自动备份已启动，每 {interval} 分钟备份一次")

def auto_backup(interval):
    while not stop_backup:
        for remaining in range(interval * 60, 0, -1):
            if stop_backup:
                break
            mins, secs = divmod(remaining, 60)
            time_str = f"距离下次备份还有 {mins:02}:{secs:02} 分钟"
            update_timer(time_str)
            time.sleep(1)
        if not stop_backup:
            perform_backup()

def stop_auto_backup():
    global stop_backup
    stop_backup = True
    update_timer("自动备份已停止。")

def update_status(message):
    status_label.config(text=message)

def update_timer(message):
    timer_label.config(text=message)

# 创建主窗口
root = tk.Tk()
root.title("文件/文件夹自动备份 BY小趴菜")

# 目录选择
dir_label = tk.Label(root, text="选择目录:")
dir_label.grid(row=0, column=0, padx=10, pady=10)

dir_entry = tk.Entry(root, width=50)
dir_entry.grid(row=0, column=1, padx=10, pady=10)

dir_button = tk.Button(root, text="浏览", command=select_directory)
dir_button.grid(row=0, column=2, padx=10, pady=10)

# 备份目录选择
backup_dir_label = tk.Label(root, text="选择备份目录:")
backup_dir_label.grid(row=1, column=0, padx=10, pady=10)

backup_dir_entry = tk.Entry(root, width=50)
backup_dir_entry.grid(row=1, column=1, padx=10, pady=10)

backup_dir_button = tk.Button(root, text="浏览", command=select_backup_dir)
backup_dir_button.grid(row=1, column=2, padx=10, pady=10)

# 时间间隔输入
interval_label = tk.Label(root, text="备份间隔时间（分钟）:")
interval_label.grid(row=2, column=0, padx=10, pady=10)

interval_entry = tk.Entry(root, width=20)
interval_entry.grid(row=2, column=1, padx=10, pady=10)

# 自动备份按钮
auto_backup_button = tk.Button(root, text="启动自动备份", command=start_auto_backup)
auto_backup_button.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

# 停止备份按钮
stop_backup_button = tk.Button(root, text="停止自动备份", command=stop_auto_backup)
stop_backup_button.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

# 立即备份按钮
backup_button = tk.Button(root, text="立即备份", command=perform_backup)
backup_button.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

# 定时器标签
timer_label = tk.Label(root, text="定时器未启动")
timer_label.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

# 状态标签
status_label = tk.Label(root, text="未进行任何备份")
status_label.grid(row=7, column=0, columnspan=3, padx=10, pady=10)

# 运行主循环
root.mainloop()
