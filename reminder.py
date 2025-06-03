"""
提醒時間處理模組
處理任務提醒功能和時間管理
"""
import threading
import time
import tkinter as tk
from datetime import datetime, timedelta
from typing import List, Callable, Optional
from models import Task


class ReminderManager:
    """提醒管理器類別"""
    
    def __init__(self):
        """初始化提醒管理器"""
        self.reminders: List[dict] = []
        self.is_running = False
        self.check_thread: Optional[threading.Thread] = None
        self.check_interval = 30  # 每30秒檢查一次
        self.notification_callback: Optional[Callable] = None
    
    def set_notification_callback(self, callback: Callable):
        """
        設定通知回調函式
        
        Args:
            callback (Callable): 當提醒觸發時呼叫的函式
        """
        self.notification_callback = callback
    
    def add_reminder(self, task: Task):
        """
        新增提醒
        
        Args:
            task (Task): 要設定提醒的任務
        """
        if task.remind_at and task.remind_at > datetime.now():
            reminder = {
                "task_id": task.id,
                "task_title": task.title,
                "remind_at": task.remind_at,
                "notified": False
            }
            
            # 避免重複新增
            self.remove_reminder(task.id)
            self.reminders.append(reminder)
            
            print(f"已新增提醒: {task.title} - {task.remind_at.strftime('%Y-%m-%d %H:%M')}")
    
    def remove_reminder(self, task_id: str):
        """
        移除提醒
        
        Args:
            task_id (str): 任務ID
        """
        self.reminders = [r for r in self.reminders if r["task_id"] != task_id]
    
    def update_reminders(self, tasks: List[Task]):
        """
        更新所有提醒
        
        Args:
            tasks (List[Task]): 任務清單
        """
        # 清除所有提醒
        self.reminders.clear()
        
        # 重新新增有效提醒
        for task in tasks:
            if not task.completed and task.remind_at:
                self.add_reminder(task)
    
    def start_monitoring(self):
        """開始監控提醒"""
        if self.is_running:
            return
        
        self.is_running = True
        self.check_thread = threading.Thread(target=self._monitor_reminders, daemon=True)
        self.check_thread.start()
        print("提醒監控已啟動")
    
    def stop_monitoring(self):
        """停止監控提醒"""
        self.is_running = False
        if self.check_thread:
            self.check_thread.join(timeout=1)
        print("提醒監控已停止")
    
    def _monitor_reminders(self):
        """監控提醒的背景執行緒"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                for reminder in self.reminders:
                    if not reminder["notified"] and current_time >= reminder["remind_at"]:
                        # 觸發提醒
                        self._trigger_notification(reminder)
                        reminder["notified"] = True
                
                # 清理已過期且已通知的提醒
                self.reminders = [r for r in self.reminders 
                                if not r["notified"] or r["remind_at"] > current_time]
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"提醒監控錯誤: {e}")
                time.sleep(self.check_interval)
    
    def _trigger_notification(self, reminder: dict):
        """
        觸發通知
        
        Args:
            reminder (dict): 提醒資訊
        """
        print(f"提醒觸發: {reminder['task_title']}")
        
        if self.notification_callback:
            try:
                self.notification_callback(reminder)
            except Exception as e:
                print(f"通知回調錯誤: {e}")
        else:
            # 預設彈窗通知
            self._show_default_notification(reminder)
    
    def _show_default_notification(self, reminder: dict):
        """
        顯示預設通知彈窗
        
        Args:
            reminder (dict): 提醒資訊
        """
        try:
            # 創建通知視窗
            notification_window = tk.Toplevel()
            notification_window.title("任務提醒")
            notification_window.geometry("300x150")
            notification_window.resizable(False, False)
            
            # 設定視窗置頂
            notification_window.attributes('-topmost', True)
            
            # 內容標籤
            title_label = tk.Label(
                notification_window, 
                text="任務提醒",
                font=("Arial", 14, "bold")
            )
            title_label.pack(pady=10)
            
            task_label = tk.Label(
                notification_window,
                text=f"任務: {reminder['task_title']}",
                font=("Arial", 10),
                wraplength=250
            )
            task_label.pack(pady=5)
            
            time_label = tk.Label(
                notification_window,
                text=f"提醒時間: {reminder['remind_at'].strftime('%H:%M')}",
                font=("Arial", 9)
            )
            time_label.pack(pady=5)
            
            # 確認按鈕
            confirm_button = tk.Button(
                notification_window,
                text="確認",
                command=notification_window.destroy,
                width=10
            )
            confirm_button.pack(pady=10)
            
            # 居中顯示
            notification_window.update_idletasks()
            x = (notification_window.winfo_screenwidth() - notification_window.winfo_width()) // 2
            y = (notification_window.winfo_screenheight() - notification_window.winfo_height()) // 2
            notification_window.geometry(f"+{x}+{y}")
            
            # 5秒後自動關閉
            notification_window.after(5000, notification_window.destroy)
            
        except Exception as e:
            print(f"顯示通知視窗錯誤: {e}")
    
    def get_upcoming_reminders(self, hours: int = 24) -> List[dict]:
        """
        取得即將到來的提醒
        
        Args:
            hours (int): 多少小時內的提醒，預設24小時
            
        Returns:
            List[dict]: 提醒清單
        """
        current_time = datetime.now()
        cutoff_time = current_time + timedelta(hours=hours)
        
        upcoming = []
        for reminder in self.reminders:
            if not reminder["notified"] and current_time <= reminder["remind_at"] <= cutoff_time:
                upcoming.append(reminder)
        
        # 按時間排序
        upcoming.sort(key=lambda x: x["remind_at"])
        return upcoming
    
    def get_reminder_status(self) -> dict:
        """
        取得提醒狀態資訊
        
        Returns:
            dict: 狀態資訊
        """
        current_time = datetime.now()
        total_reminders = len(self.reminders)
        active_reminders = len([r for r in self.reminders if not r["notified"]])
        overdue_reminders = len([r for r in self.reminders 
                               if not r["notified"] and r["remind_at"] < current_time])
        
        return {
            "is_running": self.is_running,
            "total_reminders": total_reminders,
            "active_reminders": active_reminders,
            "overdue_reminders": overdue_reminders,
            "check_interval": self.check_interval
        }


class ReminderHelper:
    """提醒輔助工具類別"""
    
    @staticmethod
    def parse_reminder_time(time_str: str, date_str: str = None) -> Optional[datetime]:
        """
        解析提醒時間字串
        
        Args:
            time_str (str): 時間字串，格式如 "14:30" 或 "2:30 PM"
            date_str (str): 日期字串，格式如 "2025-06-03"，為空則使用今天
            
        Returns:
            Optional[datetime]: 解析後的時間，解析失敗返回None
        """
        try:
            if date_str:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            else:
                date_obj = datetime.now().date()
            
            # 嘗試解析不同時間格式
            time_formats = ["%H:%M", "%I:%M %p", "%H:%M:%S"]
            
            for fmt in time_formats:
                try:
                    time_obj = datetime.strptime(time_str.strip(), fmt).time()
                    remind_datetime = datetime.combine(date_obj, time_obj)
                    
                    # 如果時間已過，設定為明天
                    if remind_datetime <= datetime.now():
                        remind_datetime += timedelta(days=1)
                    
                    return remind_datetime
                except ValueError:
                    continue
            
            return None
            
        except Exception as e:
            print(f"解析提醒時間錯誤: {e}")
            return None
    
    @staticmethod
    def get_quick_reminder_options() -> List[dict]:
        """
        取得快速提醒選項
        
        Returns:
            List[dict]: 快速提醒選項清單
        """
        now = datetime.now()
        options = [
            {"label": "5分鐘後", "datetime": now + timedelta(minutes=5)},
            {"label": "15分鐘後", "datetime": now + timedelta(minutes=15)},
            {"label": "30分鐘後", "datetime": now + timedelta(minutes=30)},
            {"label": "1小時後", "datetime": now + timedelta(hours=1)},
            {"label": "今天下午5點", "datetime": now.replace(hour=17, minute=0, second=0, microsecond=0)},
            {"label": "明天上午9點", "datetime": (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)},
        ]
        
        # 過濾掉已過去的時間
        valid_options = [opt for opt in options if opt["datetime"] > now]
        return valid_options
    