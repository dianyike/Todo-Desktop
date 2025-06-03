"""
Tkinter UI 建構模組
處理桌面代辦清單應用的用戶介面
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from typing import Optional, List
from models import Task, TaskCategories
from storage import TaskManager
from reminder import ReminderManager, ReminderHelper


class TodoApp:
    """代辦清單主應用程式"""
    
    def __init__(self):
        """初始化應用程式"""
        self.root = tk.Tk()
        self.task_manager = TaskManager()
        self.reminder_manager = ReminderManager()
        
        # 設定提醒回調
        self.reminder_manager.set_notification_callback(self._on_reminder_triggered)
        
        # UI 元件
        self.task_listbox = None
        self.category_combobox = None
        self.task_entry = None
        self.status_label = None
        
        # 初始化UI
        self._setup_ui()
        self._load_tasks()
        
        # 啟動提醒監控
        self.reminder_manager.start_monitoring()
        self.reminder_manager.update_reminders(self.task_manager.get_all_tasks())
    
    def _setup_ui(self):
        """設定用戶介面"""
        self.root.title("📋 桌面代辦清單")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # 設定主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置網格權重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 標題
        title_label = ttk.Label(main_frame, text="📋 桌面代辦清單", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # 新增任務區域
        self._create_add_task_section(main_frame)
        
        # 任務清單區域
        self._create_task_list_section(main_frame)
        
        # 按鈕區域
        self._create_button_section(main_frame)
        
        # 狀態列
        self._create_status_section(main_frame)
    
    def _create_add_task_section(self, parent):
        """創建新增任務區域"""
        # 新增任務框架
        add_frame = ttk.LabelFrame(parent, text="新增任務", padding="5")
        add_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        add_frame.columnconfigure(1, weight=1)
        
        # 任務輸入
        ttk.Label(add_frame, text="任務:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.task_entry = ttk.Entry(add_frame, font=("Arial", 10))
        self.task_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.task_entry.bind('<Return>', lambda e: self._add_task())
        
        # 分類選擇
        ttk.Label(add_frame, text="分類:").grid(row=0, column=2, sticky=tk.W, padx=(5, 5))
        self.category_combobox = ttk.Combobox(add_frame, values=TaskCategories.get_all_categories(), 
                                            state="readonly", width=10)
        self.category_combobox.set(TaskCategories.GENERAL)
        self.category_combobox.grid(row=0, column=3, padx=(0, 5))
        
        # 新增按鈕
        add_button = ttk.Button(add_frame, text="新增", command=self._add_task)
        add_button.grid(row=0, column=4, padx=(5, 0))
    
    def _create_task_list_section(self, parent):
        """創建任務清單區域"""
        # 任務清單框架
        list_frame = ttk.LabelFrame(parent, text="任務清單", padding="5")
        list_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 創建任務清單和滾動條
        list_container = ttk.Frame(list_frame)
        list_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_container.columnconfigure(0, weight=1)
        list_container.rowconfigure(0, weight=1)
        
        self.task_listbox = tk.Listbox(list_container, font=("Arial", 10), 
                                     selectmode=tk.EXTENDED, height=15)
        self.task_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 滾動條
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.task_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.task_listbox.configure(yscrollcommand=scrollbar.set)
        
        # 綁定雙擊事件
        self.task_listbox.bind('<Double-1>', self._on_task_double_click)
        self.task_listbox.bind('<Button-3>', self._on_task_right_click)  # 右鍵功能表
    
    def _create_button_section(self, parent):
        """創建按鈕區域"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        # 任務操作按鈕
        ttk.Button(button_frame, text="✓ 標記完成", command=self._toggle_task_completion).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🗑️ 刪除任務", command=self._delete_selected_tasks).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="⏰ 設定提醒", command=self._set_reminder).pack(side=tk.LEFT, padx=(0, 5))
        
        # 分隔線
        ttk.Separator(button_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # 管理按鈕
        ttk.Button(button_frame, text="🧹 清理已完成", command=self._clear_completed_tasks).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="📊 統計資訊", command=self._show_statistics).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🔄 重新載入", command=self._reload_tasks).pack(side=tk.LEFT, padx=(0, 5))
    
    def _create_status_section(self, parent):
        """創建狀態列"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(status_frame, text="就緒", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # 時間標籤
        self.time_label = ttk.Label(status_frame, text="", anchor=tk.E)
        self.time_label.grid(row=0, column=1, sticky=tk.E)
        
        # 更新時間
        self._update_time()
    
    def _add_task(self):
        """新增任務"""
        task_text = self.task_entry.get().strip()
        if not task_text:
            messagebox.showwarning("警告", "請輸入任務內容！")
            return
        
        category = self.category_combobox.get()
        task = Task(task_text, category)
        
        self.task_manager.add_task(task)
        self.task_entry.delete(0, tk.END)
        
        self._refresh_task_list()
        self._update_status(f"已新增任務: {task_text}")
    
    def _load_tasks(self):
        """載入任務"""
        self.task_manager.load_tasks()
        self._refresh_task_list()
        
        task_count = len(self.task_manager.get_all_tasks())
        self._update_status(f"已載入 {task_count} 個任務")
    
    def _refresh_task_list(self):
        """重新整理任務清單"""
        self.task_listbox.delete(0, tk.END)
        
        for task in self.task_manager.get_all_tasks():
            # 顯示格式：狀態 任務標題 [分類] 提醒時間
            status_icon = "✓" if task.completed else "○"
            reminder_info = ""
            if task.remind_at:
                reminder_info = f" ⏰{task.remind_at.strftime('%m/%d %H:%M')}"
            
            display_text = f"{status_icon} {task.title} [{task.category}]{reminder_info}"
            
            self.task_listbox.insert(tk.END, display_text)
            
            # 設定已完成任務的顏色
            if task.completed:
                self.task_listbox.itemconfig(tk.END, {'fg': 'gray'})
    
    def _toggle_task_completion(self):
        """切換任務完成狀態"""
        selected_indices = self.task_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("警告", "請選擇要操作的任務！")
            return
        
        for index in selected_indices:
            task = self.task_manager.get_all_tasks()[index]
            if task.completed:
                task.mark_uncompleted()
            else:
                task.mark_completed()
        
        self.task_manager.save_tasks()
        self._refresh_task_list()
        self.reminder_manager.update_reminders(self.task_manager.get_all_tasks())
        
        self._update_status(f"已更新 {len(selected_indices)} 個任務的完成狀態")
    
    def _delete_selected_tasks(self):
        """刪除選中的任務"""
        selected_indices = self.task_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("警告", "請選擇要刪除的任務！")
            return
        
        # 確認刪除
        if not messagebox.askyesno("確認", f"確定要刪除 {len(selected_indices)} 個任務嗎？"):
            return
        
        # 倒序刪除以避免索引問題
        tasks = self.task_manager.get_all_tasks()
        for index in reversed(selected_indices):
            task = tasks[index]
            self.task_manager.remove_task(task.id)
            self.reminder_manager.remove_reminder(task.id)
        
        self._refresh_task_list()
        self._update_status(f"已刪除 {len(selected_indices)} 個任務")
    
    def _set_reminder(self):
        """設定提醒"""
        selected_indices = self.task_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("警告", "請選擇要設定提醒的任務！")
            return
        
        if len(selected_indices) > 1:
            messagebox.showwarning("警告", "一次只能為一個任務設定提醒！")
            return
        
        task = self.task_manager.get_all_tasks()[selected_indices[0]]
        self._show_reminder_dialog(task)
    
    def _show_reminder_dialog(self, task: Task):
        """顯示提醒設定對話框"""
        dialog = ReminderDialog(self.root, task)
        result = dialog.result
        
        if result:
            task.set_reminder(result)
            self.task_manager.save_tasks()
            self.reminder_manager.update_reminders(self.task_manager.get_all_tasks())
            self._refresh_task_list()
            
            time_str = result.strftime("%Y-%m-%d %H:%M")
            self._update_status(f"已為任務 '{task.title}' 設定提醒時間: {time_str}")
    
    def _clear_completed_tasks(self):
        """清理已完成的任務"""
        completed_count = len(self.task_manager.get_completed_tasks())
        if completed_count == 0:
            messagebox.showinfo("資訊", "沒有已完成的任務需要清理。")
            return
        
        if messagebox.askyesno("確認", f"確定要清理 {completed_count} 個已完成的任務嗎？"):
            removed_count = self.task_manager.clear_completed_tasks()
            self._refresh_task_list()
            self.reminder_manager.update_reminders(self.task_manager.get_all_tasks())
            self._update_status(f"已清理 {removed_count} 個已完成的任務")
    
    def _show_statistics(self):
        """顯示統計資訊"""
        all_tasks = self.task_manager.get_all_tasks()
        completed_tasks = self.task_manager.get_completed_tasks()
        pending_tasks = self.task_manager.get_pending_tasks()
        
        # 按分類統計
        category_stats = {}
        for task in all_tasks:
            category_stats[task.category] = category_stats.get(task.category, 0) + 1
        
        # 提醒統計
        reminder_status = self.reminder_manager.get_reminder_status()
        
        stats_text = f"""📊 任務統計資訊

總任務數: {len(all_tasks)}
已完成: {len(completed_tasks)}
待完成: {len(pending_tasks)}
完成率: {len(completed_tasks)/len(all_tasks)*100:.1f}% (如果有任務)

📂 分類統計:
{chr(10).join([f"  {cat}: {count}" for cat, count in category_stats.items()])}

⏰ 提醒狀態:
  監控運行: {'是' if reminder_status['is_running'] else '否'}
  活動提醒: {reminder_status['active_reminders']}
  逾期提醒: {reminder_status['overdue_reminders']}
"""
        
        messagebox.showinfo("統計資訊", stats_text)
    
    def _reload_tasks(self):
        """重新載入任務"""
        self._load_tasks()
        self.reminder_manager.update_reminders(self.task_manager.get_all_tasks())
    
    def _on_task_double_click(self, event):
        """任務雙擊事件"""
        self._toggle_task_completion()
    
    def _on_task_right_click(self, event):
        """任務右鍵點擊事件"""
        # 選中點擊的項目
        index = self.task_listbox.nearest(event.y)
        self.task_listbox.selection_clear(0, tk.END)
        self.task_listbox.selection_set(index)
        
        # 顯示右鍵功能表
        self._show_context_menu(event)
    
    def _show_context_menu(self, event):
        """顯示右鍵功能表"""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="標記完成/未完成", command=self._toggle_task_completion)
        context_menu.add_command(label="設定提醒", command=self._set_reminder)
        context_menu.add_separator()
        context_menu.add_command(label="刪除任務", command=self._delete_selected_tasks)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def _on_reminder_triggered(self, reminder: dict):
        """提醒觸發回調"""
        # 這裡可以自定義提醒行為
        # 目前使用預設的彈窗通知
        pass
    
    def _update_status(self, message: str):
        """更新狀態列"""
        self.status_label.config(text=message)
        # 3秒後恢復為就緒狀態
        self.root.after(3000, lambda: self.status_label.config(text="就緒"))
    
    def _update_time(self):
        """更新時間顯示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        # 每秒更新一次
        self.root.after(1000, self._update_time)
    
    def run(self):
        """運行應用程式"""
        # 設定關閉事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # 居中顯示視窗
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - self.root.winfo_width()) // 2
        y = (self.root.winfo_screenheight() - self.root.winfo_height()) // 2
        self.root.geometry(f"+{x}+{y}")
        
        # 啟動主迴圈
        self.root.mainloop()
    
    def _on_closing(self):
        """應用程式關閉事件"""
        # 停止提醒監控
        self.reminder_manager.stop_monitoring()
        
        # 確保保存任務
        self.task_manager.save_tasks()
        
        # 關閉視窗
        self.root.destroy()


class ReminderDialog:
    """提醒設定對話框"""
    
    def __init__(self, parent, task: Task):
        """初始化對話框"""
        self.result = None
        
        # 創建對話框視窗
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"設定提醒 - {task.title}")
        self.dialog.geometry("350x250")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中顯示
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - self.dialog.winfo_width()) // 2
        y = (self.dialog.winfo_screenheight() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        self._create_widgets()
        
        # 等待對話框關閉
        self.dialog.wait_window()
    
    def _create_widgets(self):
        """創建對話框部件"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 快速選項
        ttk.Label(main_frame, text="快速選項:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        quick_frame = ttk.Frame(main_frame)
        quick_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 快速提醒按鈕
        quick_options = ReminderHelper.get_quick_reminder_options()
        for i, option in enumerate(quick_options[:4]):  # 只顯示前4個選項
            btn = ttk.Button(quick_frame, text=option["label"], 
                           command=lambda opt=option: self._select_quick_option(opt))
            btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 分隔線
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # 自定義時間
        ttk.Label(main_frame, text="自定義時間:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        time_frame = ttk.Frame(main_frame)
        time_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 日期輸入
        ttk.Label(time_frame, text="日期:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.date_entry = ttk.Entry(time_frame, width=12)
        self.date_entry.grid(row=0, column=1, padx=(0, 10))
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # 時間輸入
        ttk.Label(time_frame, text="時間:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.time_entry = ttk.Entry(time_frame, width=8)
        self.time_entry.grid(row=0, column=3)
        self.time_entry.insert(0, "09:00")
        
        # 按鈕區域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="確認", command=self._confirm).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="取消", command=self._cancel).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="清除提醒", command=self._clear_reminder).pack(side=tk.LEFT)
    
    def _select_quick_option(self, option):
        """選擇快速選項"""
        self.result = option["datetime"]
        self.dialog.destroy()
    
    def _confirm(self):
        """確認設定"""
        date_str = self.date_entry.get()
        time_str = self.time_entry.get()
        
        remind_time = ReminderHelper.parse_reminder_time(time_str, date_str)
        if remind_time:
            self.result = remind_time
            self.dialog.destroy()
        else:
            messagebox.showerror("錯誤", "時間格式不正確！\n請使用格式：日期 YYYY-MM-DD，時間 HH:MM")
    
    def _cancel(self):
        """取消設定"""
        self.dialog.destroy()
    
    def _clear_reminder(self):
        """清除提醒"""
        self.result = None
        self.dialog.destroy()


