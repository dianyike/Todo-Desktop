# 📦 Todo-Desktop 打包注意事項

本文件包含將 Todo-Desktop 應用程式打包為可執行檔的詳細說明和注意事項。

---

## 🚀 快速打包

### 方法一：使用自動化腳本（推薦）

```bash
# 1. 安裝打包依賴
pip install pyinstaller

# 2. 執行自動打包腳本
python build_exe.py
```

### 方法二：手動打包

```bash
# 1. 安裝 PyInstaller
pip install pyinstaller

# 2. 清理舊檔案
Remove-Item -Path "dist", "build", "*.spec" -Recurse -Force -ErrorAction SilentlyContinue

# 3. 執行打包命令
pyinstaller --onefile --windowed --name="Todo-Desktop" --icon="images/icon.ico" --add-data="data;data" --add-data="images;images" main.py
```

---

## ⚠️ 重要注意事項

### 1. **系統需求**

- **Windows 10/11** (64 位元)
- **Python 3.7+** (建議 3.10+)
- **足夠的磁碟空間** (至少 100MB 用於建置過程)

### 2. **打包環境檢查**

在打包前請確認：

- [ ] Python 版本相容 (`python --version`)
- [ ] PyInstaller 已安裝 (`pip list | findstr pyinstaller`)
- [ ] 所有程式檔案完整存在
- [ ] Tkinter 可正常運行 (`python -c "import tkinter"`)

### 3. **常見問題與解決方案**

#### 問題 1：`ModuleNotFoundError`

**症狀**：打包後執行檔案出現模組找不到錯誤
**解決方案**：

- 確保所有依賴都在相同目錄
- 檢查 `--add-data` 參數是否正確
- 使用虛擬環境進行打包

#### 問題 2：檔案過大

**症狀**：生成的 .exe 檔案超過 50MB
**解決方案**：

- 使用 `--exclude-module` 排除不必要的模組
- 考慮使用 `--onedir` 替代 `--onefile`
- 檢查是否包含了過多的資料檔案

#### 問題 3：啟動緩慢

**症狀**：雙擊執行檔後需要較長時間才顯示視窗
**解決方案**：

- 這是 PyInstaller 的正常行為
- 可添加啟動畫面或載入提示
- 考慮使用 `--onedir` 模式

#### 問題 4：防毒軟體警告

**症狀**：生成的檔案被防毒軟體標記為可疑 例如會檢測到自製的 ico
**解決方案**：

- 這是常見的誤報，PyInstaller 打包的檔案經常觸發
- 可考慮數位簽章
- 提醒用戶添加白名單例外

### 4. **資料檔案處理**

- `data/tasks.json` 會隨 exe 一起打包
- `images/icon.ico` 應用程式圖示會內嵌到執行檔中
- 執行檔會自動在相同目錄建立 `data` 資料夾
- 用戶的任務資料會保存在執行檔目錄下

### 5. **分發建議**

#### 5.1 檔案結構

打包完成後的分發檔案：

```
Todo-Desktop/
├── Todo-Desktop.exe     # 主執行檔
├── README.txt          # 簡化的使用說明
└── data/               # 資料目錄（首次執行自動建立）
    └── tasks.json      # 任務資料檔案
```

#### 5.2 使用說明檔案範例

建議建立 `README.txt`：

```
Todo-Desktop 桌面代辦清單應用程式

安裝方法：
1. 無需安裝，直接雙擊 Todo-Desktop.exe 即可運行
2. 首次運行會自動建立 data 資料夾用於儲存任務

基本使用：
- 在輸入框輸入任務後按 Enter 或點擊「新增」
- 雙擊任務可標記完成/未完成
- 右鍵點擊任務可顯示功能表
- 所有資料會自動儲存

系統需求：
- Windows 10/11
- 支援圖形介面

如有問題請聯絡：dianyike1013@gmail.com
```

### 6. **效能最佳化建議**

#### 6.1 減少檔案大小

```bash
# 使用更精確的排除模組
pyinstaller --onefile --windowed \
    --exclude-module=matplotlib \
    --exclude-module=numpy \
    --exclude-module=pandas \
    --name="Todo-Desktop" \
    --add-data="data;data" \
    main.py
```

#### 6.2 提升啟動速度

- 考慮將常用的模組預先載入
- 最小化應用程式啟動時的初始化工作
- 使用 splash screen 改善使用者體驗

### 7. **測試檢查清單**

打包完成後，請進行以下測試：

- [ ] **功能測試**

  - [ ] 新增任務正常
  - [ ] 刪除任務正常
  - [ ] 標記完成正常
  - [ ] 分類功能正常
  - [ ] 提醒功能正常
  - [ ] 統計功能正常

- [ ] **資料持久化測試**

  - [ ] 關閉應用程式後重新開啟，資料保持
  - [ ] 新增任務後重啟，資料存在
  - [ ] 備份功能正常

- [ ] **環境測試**

  - [ ] 在乾淨的 Windows 系統上測試
  - [ ] 在不同使用者帳戶下測試
  - [ ] 在不同硬碟分區測試

- [ ] **異常處理測試**
  - [ ] 刪除 data 資料夾後重新啟動
  - [ ] 修改 tasks.json 檔案測試容錯性
  - [ ] 權限不足時的錯誤處理

### 8. **版本資訊與更新**

建議在 main.py 中添加版本資訊：

```python
VERSION = "1.0.0"
BUILD_DATE = "2025-06-03"
```

---

## 🛠 進階打包選項

### 隱藏控制台視窗

```bash
pyinstaller --onefile --noconsole main.py
```

### 添加應用程式圖示

```bash
pyinstaller --onefile --windowed --icon=images/icon.ico main.py
```

### 指定輸出目錄

```bash
pyinstaller --onefile --distpath=release main.py
```

### 添加版本資訊（需要 version.txt）

```bash
pyinstaller --onefile --version-file=version.txt main.py
```

---

## 📋 打包完成後的後續工作

1. **病毒掃描**：使用多個防毒引擎掃描確保安全
2. **數位簽章**：考慮申請代碼簽章證書
3. **分發測試**：在多台機器上測試相容性
4. **使用者文件**：準備詳細的使用說明
5. **技術支援**：準備常見問題解答

---

_最後更新：2025-06-03_  
_適用版本：Todo-Desktop v1.1.0_
