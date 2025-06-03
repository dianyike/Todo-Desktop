#!/usr/bin/env python3
"""
桌面代辦清單應用主程式
使用 Python + Tkinter 開發的跨平台桌面任務管理工具

功能特色：
- 新增、刪除、完成任務
- 任務分類管理
- 提醒功能
- 本地JSON儲存
- 簡潔直覺的GUI介面

作者: Dianyike + Cursor
版本: 1.1.0
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

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
    """檢查程式依賴"""
    required_modules = ['tkinter', 'json', 'datetime', 'uuid', 'threading']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"缺少必要模組: {', '.join(missing_modules)}")
        print("請安裝缺少的模組後重試")
        return False
    
    return True


def setup_data_directory():
    """設定資料目錄"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        try:
            os.makedirs(data_dir)
            print(f"已建立資料目錄: {data_dir}")
        except OSError as e:
            print(f"建立資料目錄失敗: {e}")
            return False
    
    return True


def main():
    """主函式"""
    print("📋 桌面代辦清單應用啟動中...")
    
    # 檢查依賴
    if not check_dependencies():
        return 1
    
    # 設定資料目錄
    if not setup_data_directory():
        return 1
    
    try:
        # 建立並運行應用程式
        print("正在初始化用戶介面...")
        app = TodoApp()
        
        print("應用程式已就緒，啟動主視窗...")
        app.run()
        
        print("應用程式正常關閉")
        return 0
        
    except KeyboardInterrupt:
        print("\n使用者中斷程式執行")
        return 0
        
    except tk.TclError as e:
        print(f"GUI錯誤: {e}")
        print("這可能是因為系統不支援圖形介面或Tkinter配置問題")
        return 1
        
    except Exception as e:
        print(f"程式運行時發生錯誤: {e}")
        print("詳細錯誤資訊:")
        import traceback
        traceback.print_exc()
        return 1


def show_help():
    """顯示幫助資訊"""
    help_text = """
📋 桌面代辦清單應用 - 使用說明

啟動方式:
    python main.py          # 正常啟動應用程式
    python main.py --help   # 顯示此幫助資訊
    python main.py --test   # 運行簡單測試

基本功能:
    ✅ 新增任務：在輸入框中輸入任務內容，選擇分類，點擊新增
    📋 檢視任務：在任務清單中檢視所有任務
    ✓ 完成任務：雙擊任務或選中後點擊"標記完成"
    🗑️ 刪除任務：選中任務後點擊"刪除任務"
    ⏰ 設定提醒：選中任務後點擊"設定提醒"
    📂 分類管理：新增任務時可選擇分類

快捷鍵:
    Enter        - 在輸入框中按下可新增任務
    雙擊         - 切換任務完成狀態
    右鍵         - 顯示功能表選單

資料儲存:
    任務資料自動儲存在 data/tasks.json 檔案中
    程式關閉時自動儲存，啟動時自動載入

系統需求:
    - Python 3.7+
    - Tkinter (通常隨Python一起安裝)
    - 支援圖形介面的作業系統

技術支援:
    如遇問題請檢查:
    1. Python版本是否符合要求
    2. Tkinter是否正確安裝
    3. 是否有寫入資料目錄的權限
    """
    print(help_text)


def run_test():
    """運行簡單測試"""
    print("🧪 運行簡單測試...")
    
    try:
        # 測試模型
        from models import Task, TaskCategories
        task = Task("測試任務", TaskCategories.WORK)
        print("✓ 任務模型測試通過")
        
        # 測試儲存
        from storage import TaskManager
        manager = TaskManager("data/test_tasks.json")
        manager.add_task(task)
        loaded_tasks = manager.get_all_tasks()
        assert len(loaded_tasks) == 1
        print("✓ 儲存模組測試通過")
        
        # 清理測試檔案
        import os
        if os.path.exists("data/test_tasks.json"):
            os.remove("data/test_tasks.json")
        
        print("✅ 所有測試通過！")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False


if __name__ == "__main__":
    # 處理命令列參數
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["--help", "-h", "help"]:
            show_help()
            sys.exit(0)
        elif arg in ["--test", "-t", "test"]:
            success = run_test()
            sys.exit(0 if success else 1)
        else:
            print(f"未知參數: {sys.argv[1]}")
            print("使用 --help 查看幫助資訊")
            sys.exit(1)
    
    # 正常啟動應用程式
    sys.exit(main())


