# Game IME Booster

這是一個 Windows 輸入法自動切換工具。當偵測到視窗進入「全螢幕遊戲」時，會自動將輸入法切換至英文，避免在遊戲中誤觸注音選字框；退出全螢幕後則自動恢復原有的中文輸入法。

## 功能特點
自動偵測：即時判斷全螢幕狀態，並自動切換對應輸入法。

淡入提示：切換狀態時，於螢幕左上方顯示簡約的淡入淡出提示框。

後台運行：支援最小化至系統列（System Tray），不佔用工作列空間。

開機自啟：內建開機啟動設定功能。

## 環境要求
輸入法設定：系統必須預先安裝「英文 (美國)」輸入法。

管理員權限：建議以系統管理員身分執行，否則可能無法控制高權限遊戲視窗。
(可對exe右鍵->內容->相容性->勾選以系統管理員執行)

## 打包與執行
若需使用「開機自啟」功能，建議將程式打包為 .exe 執行檔，以確保路徑讀取與權限請求正常。

打包步驟
安裝 PyInstaller：
pip install pyinstaller

執行打包指令：
pyinstaller --noconfirm --onefile --windowed --admin --name "GameIMEBooster" game_ime_tray.py

取得檔案：打包後的執行檔位於 dist/GameIMEBooster.exe。

本地開發
若直接運行原始碼，請先安裝必要套件：
pip install -r requirements.txt
python game_ime_tray.py

## 注意事項
防毒軟體：由於程式會修改註冊表以實現開機自啟，若防毒軟體攔截請手動加入白名單。

視窗模式：本工具主要針對「全螢幕」模式開發。
