#!/usr/bin/env python3
"""
桌面代辦清單應用程式 v1.2.0
使用 Python 和 Tkinter 開發的跨平台代辦清單工具

新功能 v1.2.0:
- 🌙 深色模式切換
- 🔍 任務搜尋功能 (支援模糊比對)
- 📱 優化提醒通知界面
- 🔧 修復提醒對話框確認按鈕顯示問題

功能特色：
- 任務新增、刪除、標記完成
- 分類管理（工作、生活、學習等）
- 提醒系統（快速選項和自定義時間）
- 資料本地持久化存儲
- 現代化的用戶界面
- 深色/淺色主題切換
- 即時任務搜尋過濾

作者：開發團隊
版本：v1.2.0
更新日期：2025年6月4日
"""

import sys
import os
import traceback
from pathlib import Path

# 確保能夠導入自定義模組
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ui import TodoApp
    from models import Task, TaskCategories
    from storage import TaskManager
    from reminder import ReminderManager
except ImportError as e:
    print(f"導入模組失敗: {e}")
    print("請確保所有必要的模組檔案都存在於同一目錄中")
    sys.exit(1)


def check_dependencies():
    """檢查必要的依賴模組"""
    required_modules = ['tkinter', 'datetime', 'json', 'uuid', 'threading']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"錯誤：缺少必要的模組: {', '.join(missing_modules)}")
        print("請確保您的 Python 安裝包含這些標準模組。")
        return False
    
    return True


def setup_data_directory():
    """設定資料目錄"""
    data_dir = Path("data")
    if not data_dir.exists():
        data_dir.mkdir(exist_ok=True)
        print(f"已建立資料目錄: {data_dir.absolute()}")


def main():
    """主函式"""
    print("桌面代辦清單 v1.2.0 正在啟動...")
    print("新功能：深色模式 🌙 | 任務搜尋 🔍 | 界面優化 📱")
    
    # 處理命令列參數
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h']:
            show_help()
            return
        elif sys.argv[1] in ['--test', '-t']:
            if run_simple_test():
                print("\n是否要啟動應用程式？(y/n): ", end="")
                try:
                    if input().lower().startswith('y'):
                        pass  # 繼續啟動
                    else:
                        return
                except KeyboardInterrupt:
                    print("\n程式已取消。")
                    return
            else:
                print("測試失敗，建議檢查環境配置後再試。")
                return
        else:
            print(f"未知參數: {sys.argv[1]}")
            print("使用 --help 查看可用選項。")
            return
    
    # 檢查依賴
    if not check_dependencies():
        print("請解決依賴問題後重新啟動程式。")
        return
    
    # 設定資料目錄
    setup_data_directory()
    
    try:
        # 啟動應用程式
        from ui import TodoApp
        
        print("正在啟動用戶界面...")
        app = TodoApp()
        print("✓ 應用程式已啟動")
        print("💡 提示：使用右上角的 🌙 圖示切換深色模式")
        print("💡 提示：使用搜尋框快速查找任務")
        
        # 運行應用程式
        app.run()
        
    except KeyboardInterrupt:
        print("\n程式被用戶中斷。")
    except Exception as e:
        print(f"❌ 應用程式啟動失敗: {e}")
        print("\n詳細錯誤資訊：")
        traceback.print_exc()
        print("\n可能的解決方案：")
        print("1. 檢查 Python 版本 (需要 3.7+)")
        print("2. 確保有檔案讀寫權限")
        print("3. 檢查 tkinter 是否正確安裝")
        print("4. 嘗試執行 'python main.py --test' 進行診斷")
    
    print("感謝使用桌面代辦清單！")


def show_help():
    """顯示幫助資訊"""
    help_text = """
桌面代辦清單應用程式 v1.2.0 使用說明

命令列選項：
  python main.py         啟動應用程式
  python main.py --help  顯示此幫助資訊
  python main.py --test   執行簡單測試

新功能 v1.2.0：
  🌙 深色模式         - 右上角切換深色/淺色主題
  🔍 任務搜尋         - 即時搜尋和過濾任務
  📱 優化提醒界面     - 改進提醒通知視窗和按鈕布局
  🔧 界面優化         - 修復各種顯示問題

基本操作：
  1. 新增任務：在輸入框輸入任務內容，選擇分類後按 Enter 或點擊「新增」
  2. 完成任務：雙擊任務或選中後點擊「✓ 標記完成」
  3. 設定提醒：選中任務後點擊「⏰ 設定提醒」
  4. 搜尋任務：在搜尋框輸入關鍵字即時過濾任務
  5. 切換主題：點擊右上角的「🌙」圖示切換深色模式
  6. 刪除任務：選中任務後點擊「🗑️ 刪除任務」
  7. 查看統計：點擊「📊 統計資訊」查看任務完成情況

檔案結構：
  main.py          - 主程式入口
  ui.py            - 用戶界面模組
  models.py        - 資料模型
  storage.py       - 資料存儲
  reminder.py      - 提醒功能
  data/tasks.json  - 任務資料檔案

技術特性：
  - 跨平台支援 (Windows, macOS, Linux)
  - 本地資料存儲，無需網路連接
  - 背景提醒監控
  - 響應式界面設計
  - 深色模式支援
  - 模糊搜尋功能

如有問題，請檢查：
  1. Python 版本是否為 3.7 或更高
  2. 是否有檔案寫入權限
  3. 資料目錄是否可訪問
    """
    print(help_text)


def run_simple_test():
    """執行簡單的功能測試"""
    print("正在執行基本功能測試...")
    
    try:
        # 測試模型
        from models import Task, TaskCategories
        test_task = Task("測試任務", TaskCategories.WORK)
        print(f"✓ 任務模型測試通過: {test_task}")
        
        # 測試存儲
        from storage import TaskManager
        manager = TaskManager()
        print("✓ 任務管理器測試通過")
        
        # 測試提醒
        from reminder import ReminderManager, ReminderHelper
        reminder_mgr = ReminderManager()
        print("✓ 提醒管理器測試通過")
        
        # 測試UI模組導入
        from ui import TodoApp
        print("✓ UI模組測試通過")
        
        print("\n🎉 所有基本功能測試通過！應用程式可以正常啟動。")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        print("詳細錯誤資訊：")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"嚴重錯誤: {e}")
        print("程式無法正常啟動，請檢查 Python 環境配置。")
        sys.exit(1)


