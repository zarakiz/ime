import time
import win32gui
import win32api
import win32con
import threading
import customtkinter as ctk
import tkinter as tk
import winreg
import os
import sys
import pystray
from PIL import Image, ImageDraw

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

LANG_ENGLISH = 0x0409
LANG_CHINESE = 0x0404

class MinimalistNotice:
    def __init__(self, message):
        self.root = tk.Toplevel()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.0)
        self.root.configure(bg="#1a1a1a")

        self.label = tk.Label(
            self.root, 
            text=message, 
            font=("Microsoft JhengHei", 20, "bold"),
            fg="#FFFFFF",
            bg="#1a1a1a",
            padx=12,
            pady=2,
            bd=0,
            highlightthickness=0
        )
        self.label.pack()

        self.root.update_idletasks()
        rw = self.root.winfo_reqwidth()
        rh = self.root.winfo_reqheight()
        
        self.root.geometry(f"{rw}x{rh}+20+20")
        self.fade_in()

    def fade_in(self):
        try:
            alpha = float(self.root.attributes("-alpha"))
            if alpha < 0.8:
                self.root.attributes("-alpha", alpha + 0.2)
                self.root.after(20, self.fade_in)
            else:
                self.root.after(1500, self.fade_out)
        except: pass

    def fade_out(self):
        try:
            alpha = float(self.root.attributes("-alpha"))
            if alpha > 0.0:
                self.root.attributes("-alpha", alpha - 0.2)
                self.root.after(20, self.fade_out)
            else:
                self.root.destroy()
        except: pass

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("遊戲輸入法助手")
        self.geometry("350x300")
        self.resizable(False, False)

        self.is_monitoring = True
        self.was_fullscreen = False
        self.tray_icon = None
        
        self.logo_label = ctk.CTkLabel(self, text="輸入法自動切換助手", font=("Microsoft JhengHei", 22, "bold"))
        self.logo_label.pack(pady=(25, 5))

        self.desc_label = ctk.CTkLabel(
            self, 
            text="全螢幕:英文，退出全螢幕:切回注音", 
            font=("Microsoft JhengHei", 13),
            text_color="#3498db" 
        )
        self.desc_label.pack(pady=(0, 0))

        self.notice_label = ctk.CTkLabel(
            self,
            text="請在系統加入英文鍵盤，並使用系統管理員開啟此程式",
            font=("Microsoft JhengHei", 12, "bold"),
            text_color="#e74c3c",
            wraplength=340 
        )
        self.notice_label.pack(pady=(0, 15))

        self.switch_var = ctk.BooleanVar(value=True)
        self.master_switch = ctk.CTkSwitch(
            self, text="啟用自動切換功能", 
            command=self.toggle_monitoring,
            variable=self.switch_var,
            font=("Microsoft JhengHei", 15)
        )
        self.master_switch.pack(pady=10)

        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.pack(pady=10)
        
        self.status_dot = ctk.CTkLabel(self.status_frame, text="●", text_color="#2ecc71", font=("Arial", 18))
        self.status_dot.pack(side="left", padx=5)
        
        self.status_text = ctk.CTkLabel(self.status_frame, text="系統監控中", font=("Microsoft JhengHei", 13))
        self.status_text.pack(side="left")

        self.autostart_var = ctk.BooleanVar(value=self.check_autostart_registry())
        self.autostart_cb = ctk.CTkCheckBox(
            self, text="隨 Windows 開機啟動", 
            command=self.toggle_autostart,
            variable=self.autostart_var,
            font=("Microsoft JhengHei", 13)
        )
        self.autostart_cb.pack(pady=20)

        self.bind("<Unmap>", self.on_minimize)

        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()

    def create_tray_icon(self):
        if self.tray_icon: return
        
        image = Image.new('RGB', (64, 64), (52, 152, 219))
        d = ImageDraw.Draw(image)
        d.text((15, 10), "A", fill=(255, 255, 255), font=None)
        
        menu = pystray.Menu(
            pystray.MenuItem("顯示介面", self.show_window),
            pystray.MenuItem("結束程式", self.quit_app)
        )
        self.tray_icon = pystray.Icon("GameIME", image, "遊戲輸入法助手", menu)
        self.tray_icon.run()

    def on_minimize(self, event):
        if self.state() == 'iconic':
            self.withdraw()
            if not self.tray_icon:
                threading.Thread(target=self.create_tray_icon, daemon=True).start()

    def show_window(self):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        self.deiconify()
        self.state('normal')

    def quit_app(self):
        if self.tray_icon:
            self.tray_icon.stop()
        self.destroy()
        sys.exit()

    def toggle_monitoring(self):
        self.is_monitoring = self.switch_var.get()
        if self.is_monitoring:
            self.status_text.configure(text="系統監控中")
            self.status_dot.configure(text_color="#2ecc71")
        else:
            self.status_text.configure(text="監控已暫停")
            self.status_dot.configure(text_color="#e74c3c")
            self.was_fullscreen = False

    def check_autostart_registry(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, "GameIMEBooster")
            winreg.CloseKey(key)
            return True
        except: return False

    def toggle_autostart(self):
        app_path = os.path.realpath(sys.executable)
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
            if self.autostart_var.get():
                winreg.SetValueEx(key, "GameIMEBooster", 0, winreg.REG_SZ, f'"{app_path}"')
            else:
                try: winreg.DeleteValue(key, "GameIMEBooster")
                except: pass
            winreg.CloseKey(key)
        except: pass

    def monitor_loop(self):
        while True:
            if self.is_monitoring:
                try:
                    current_fullscreen = self.is_fullscreen()
                    if current_fullscreen and not self.was_fullscreen:
                        self.switch_ime(LANG_ENGLISH)
                        self.after(0, lambda: MinimalistNotice("輸入法：英文"))
                        self.was_fullscreen = True
                    elif not current_fullscreen and self.was_fullscreen:
                        self.switch_ime(LANG_CHINESE)
                        self.was_fullscreen = False
                except: pass
            time.sleep(0.5)

    def is_fullscreen(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd: return False
            class_name = win32gui.GetClassName(hwnd)
            title = win32gui.GetWindowText(hwnd).lower()
            if class_name in ["Chrome_WidgetWin_1", "MozillaWindowClass"]: return False
            if any(x in title for x in ["netflix", "vlc", "potplayer"]): return False
            if class_name in ["Progman", "WorkerW", "Shell_TrayWnd", "NotifyIconOverflowWindow"]: return False
            rect = win32gui.GetWindowRect(hwnd)
            w, h = rect[2] - rect[0], rect[3] - rect[1]
            sw, sh = win32api.GetSystemMetrics(win32con.SM_CXSCREEN), win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            return w >= sw and h >= sh
        except: return False

    def switch_ime(self, lang_id):
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                win32api.PostMessage(hwnd, win32con.WM_INPUTLANGCHANGEREQUEST, 0, lang_id)
        except: pass

if __name__ == "__main__":
    app = App()
    app.mainloop()