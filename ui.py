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
        self.search_entry = None
        self.status_label = None
        self.dark_mode_var = tk.BooleanVar()
        self.style = ttk.Style()
        
        # 任務搜尋相關
        self.original_tasks = []
        self.filtered_tasks = []
        
        # 初始化UI
        self._setup_ui()
        self._setup_themes()
        self._load_tasks()
        
        # 啟動提醒監控
        self.reminder_manager.start_monitoring()
        self.reminder_manager.update_reminders(self.task_manager.get_all_tasks())
    
    def _setup_ui(self):
        """設定用戶介面"""
        self.root.title("桌面代辦清單 v1.2.0")
        self.root.geometry("650x600")
        self.root.resizable(True, True)
        
        # 設定主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置網格權重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # 頂部區域：標題和深色模式切換
        self._create_header_section(main_frame)
        
        # 搜尋區域
        self._create_search_section(main_frame)
        
        # 新增任務區域
        self._create_add_task_section(main_frame)
        
        # 任務清單區域
        self._create_task_list_section(main_frame)
        
        # 按鈕區域
        self._create_button_section(main_frame)
        
        # 狀態列
        self._create_status_section(main_frame)
    
    def _create_header_section(self, parent):
        """創建頂部標題和深色模式區域"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)
        
        # 標題
        title_label = ttk.Label(header_frame, text="桌面代辦清單", font=("Microsoft JhengHei", 18, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # 深色模式切換區域
        dark_mode_frame = ttk.Frame(header_frame)
        dark_mode_frame.grid(row=0, column=1, sticky=tk.E)
        
        # 深色模式標籤
        self.dark_mode_label = ttk.Label(dark_mode_frame, text="深色模式:", font=("Microsoft JhengHei", 10))
        self.dark_mode_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # 深色模式切換按鈕
        self.dark_mode_button = ttk.Checkbutton(
            dark_mode_frame, 
            text="🌙", 
            variable=self.dark_mode_var,
            command=self._toggle_dark_mode
        )
        self.dark_mode_button.pack(side=tk.LEFT)
    
    def _create_search_section(self, parent):
        """創建搜尋區域"""
        search_frame = ttk.LabelFrame(parent, text="搜尋任務", padding="5")
        search_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        # 搜尋標籤和輸入框
        ttk.Label(search_frame, text="搜尋:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame, font=("Microsoft JhengHei", 12))
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.search_entry.bind('<KeyRelease>', self._on_search_changed)
        
        # 清除搜尋按鈕
        clear_search_button = ttk.Button(search_frame, text="清除", command=self._clear_search)
        clear_search_button.grid(row=0, column=2, padx=(5, 0))
    
    def _create_add_task_section(self, parent):
        """創建新增任務區域"""
        # 新增任務框架
        add_frame = ttk.LabelFrame(parent, text="新增任務", padding="5")
        add_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        add_frame.columnconfigure(1, weight=1)
        
        # 任務輸入
        ttk.Label(add_frame, text="任務:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.task_entry = ttk.Entry(add_frame, font=("Microsoft JhengHei", 12))
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
        list_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 創建任務清單和滾動條
        list_container = ttk.Frame(list_frame)
        list_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_container.columnconfigure(0, weight=1)
        list_container.rowconfigure(0, weight=1)
        
        self.task_listbox = tk.Listbox(list_container, font=("Microsoft JhengHei", 12), 
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
        button_frame.grid(row=4, column=0, columnspan=3, pady=(0, 10))
        
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
        status_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(status_frame, text="就緒", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # 時間標籤
        self.time_label = ttk.Label(status_frame, text="", anchor=tk.E)
        self.time_label.grid(row=0, column=1, sticky=tk.E)
        
        # 更新時間
        self._update_time()
    
    def _setup_themes(self):
        """設定主題樣式"""
        # 設定預設主題
        self.style.theme_use('default')
    
    def _toggle_dark_mode(self):
        """切換深色模式"""
        if self.dark_mode_var.get():
            # 切換到深色模式
            self._apply_dark_theme()
            self.dark_mode_button.configure(text="☀️")  # 在深色模式下顯示太陽圖示
            self.dark_mode_label.configure(text="淺色模式:")
            self._update_status("已切換至深色模式")
        else:
            # 切換到淺色模式
            self._apply_light_theme()
            self.dark_mode_button.configure(text="🌙")  # 在淺色模式下顯示月亮圖示
            self.dark_mode_label.configure(text="深色模式:")
            self._update_status("已切換至淺色模式")
    
    def _apply_dark_theme(self):
        """應用深色主題"""
        # 設定主視窗背景
        self.root.configure(bg='#2b2b2b')
        
        # 設定ttk樣式
        self.style.configure('TFrame', background='#2b2b2b')
        self.style.configure('TLabel', background='#2b2b2b', foreground='white')
        self.style.configure('TLabelFrame', background='#2b2b2b', foreground='white')
        self.style.configure('TLabelFrame.Label', background='#2b2b2b', foreground='white')
        self.style.configure('TButton', background='#404040', foreground='white')
        self.style.map('TButton', 
                      background=[('active', '#505050'), ('pressed', '#303030')])
        
        # 專門配置Entry的深色模式
        self.style.configure('TEntry', 
                           background='#404040', 
                           foreground='white', 
                           fieldbackground='#404040',
                           bordercolor='#606060',
                           lightcolor='#606060',
                           darkcolor='#606060',
                           insertcolor='white')
        self.style.map('TEntry',
                      fieldbackground=[('focus', '#505050')],
                      bordercolor=[('focus', '#707070')])
        
        # 專門配置Combobox的深色模式
        self.style.configure('TCombobox', 
                           background='#404040', 
                           foreground='white', 
                           fieldbackground='#404040',
                           bordercolor='#606060',
                           arrowcolor='white',
                           insertcolor='white')
        self.style.map('TCombobox',
                      fieldbackground=[('readonly', '#404040'), ('focus', '#505050')],
                      bordercolor=[('focus', '#707070')])
        
        self.style.configure('TCheckbutton', background='#2b2b2b', foreground='white')
        self.style.map('TCheckbutton',
                      background=[('active', '#404040')])
        
        # 設定Listbox樣式
        self.task_listbox.configure(bg='#404040', fg='white', selectbackground='#606060', selectforeground='white')
        
        # 強制更新所有Entry和Combobox的樣式
        self.task_entry.configure(style='TEntry')
        self.search_entry.configure(style='TEntry')
        self.category_combobox.configure(style='TCombobox')
    
    def _apply_light_theme(self):
        """應用淺色主題"""
        # 重設主視窗背景
        self.root.configure(bg='SystemButtonFace')
        
        # 重設ttk樣式為系統預設
        self.style.configure('TFrame', background='SystemButtonFace')
        self.style.configure('TLabel', background='SystemButtonFace', foreground='SystemWindowText')
        self.style.configure('TLabelFrame', background='SystemButtonFace', foreground='SystemWindowText')
        self.style.configure('TLabelFrame.Label', background='SystemButtonFace', foreground='SystemWindowText')
        self.style.configure('TButton', background='SystemButtonFace', foreground='SystemButtonText')
        self.style.map('TButton', 
                      background=[('active', 'SystemHighlight'), ('pressed', 'SystemHighlight')])
        
        # 重設Entry樣式
        self.style.configure('TEntry', 
                           background='SystemWindow', 
                           foreground='SystemWindowText', 
                           fieldbackground='SystemWindow',
                           bordercolor='SystemButtonShadow',
                           lightcolor='SystemButtonHighlight',
                           darkcolor='SystemButtonShadow',
                           insertcolor='SystemWindowText')
        self.style.map('TEntry',
                      fieldbackground=[('focus', 'SystemWindow')],
                      bordercolor=[('focus', 'SystemHighlight')])
        
        # 重設Combobox樣式
        self.style.configure('TCombobox', 
                           background='SystemWindow', 
                           foreground='SystemWindowText', 
                           fieldbackground='SystemWindow',
                           bordercolor='SystemButtonShadow',
                           arrowcolor='SystemButtonText',
                           insertcolor='SystemWindowText')
        self.style.map('TCombobox',
                      fieldbackground=[('readonly', 'SystemWindow'), ('focus', 'SystemWindow')],
                      bordercolor=[('focus', 'SystemHighlight')])
        
        self.style.configure('TCheckbutton', background='SystemButtonFace', foreground='SystemWindowText')
        self.style.map('TCheckbutton',
                      background=[('active', 'SystemHighlight')])
        
        # 重設Listbox樣式
        self.task_listbox.configure(bg='SystemWindow', fg='SystemWindowText', selectbackground='SystemHighlight', selectforeground='SystemHighlightText')
        
        # 強制更新所有Entry和Combobox的樣式
        self.task_entry.configure(style='TEntry')
        self.search_entry.configure(style='TEntry')
        self.category_combobox.configure(style='TCombobox')
    
    def _on_search_changed(self, event):
        """搜尋內容變更時的處理"""
        search_text = self.search_entry.get().strip().lower()
        if search_text:
            self._filter_tasks(search_text)
        else:
            self._show_all_tasks()
    
    def _filter_tasks(self, search_text):
        """根據搜尋文字過濾任務"""
        self.filtered_tasks = []
        for task in self.original_tasks:
            if search_text in task.title.lower() or search_text in task.category.lower():
                self.filtered_tasks.append(task)
        
        self._refresh_task_list(use_filtered=True)
        self._update_status(f"搜尋到 {len(self.filtered_tasks)} 個任務")
    
    def _show_all_tasks(self):
        """顯示所有任務"""
        self.filtered_tasks = []
        self._refresh_task_list(use_filtered=False)
        self._update_status("顯示所有任務")
    
    def _clear_search(self):
        """清除搜尋"""
        self.search_entry.delete(0, tk.END)
        self._show_all_tasks()
        
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
        self.original_tasks = self.task_manager.get_all_tasks()
        self._refresh_task_list()
        
        task_count = len(self.original_tasks)
        self._update_status(f"已載入 {task_count} 個任務")
    
    def _refresh_task_list(self, use_filtered=False):
        """重新整理任務清單"""
        self.task_listbox.delete(0, tk.END)
        
        # 更新原始任務列表
        if not use_filtered:
            self.original_tasks = self.task_manager.get_all_tasks()
        
        # 決定要顯示的任務列表
        display_tasks = self.filtered_tasks if use_filtered and self.filtered_tasks else self.original_tasks
        
        for task in display_tasks:
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
            messagebox.showwarning("警告", "請選擇要標記的任務！")
            return
        
        # 取得實際任務物件
        display_tasks = self.filtered_tasks if self.filtered_tasks else self.original_tasks
        
        for index in selected_indices:
            if index < len(display_tasks):
                task = display_tasks[index]
                if task.completed:
                    task.mark_uncompleted()
                    self._update_status(f"任務已標記為未完成: {task.title}")
                else:
                    task.mark_completed()
                    self._update_status(f"任務已標記為完成: {task.title}")
        
        self.task_manager.save_tasks()
        self._refresh_task_list(use_filtered=bool(self.filtered_tasks))
    
    def _delete_selected_tasks(self):
        """刪除選中的任務"""
        selected_indices = self.task_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("警告", "請選擇要刪除的任務！")
            return
        
        # 確認刪除
        if not messagebox.askyesno("確認", f"確定要刪除選中的 {len(selected_indices)} 個任務嗎？"):
            return
        
        # 取得實際任務物件
        display_tasks = self.filtered_tasks if self.filtered_tasks else self.original_tasks
        tasks_to_delete = []
        
        for index in selected_indices:
            if index < len(display_tasks):
                tasks_to_delete.append(display_tasks[index])
        
        # 刪除任務
        for task in tasks_to_delete:
            self.task_manager.remove_task(task.id)
            self.reminder_manager.remove_reminder(task.id)
        
        self.task_manager.save_tasks()
        
        # 重新載入和重新整理
        self.original_tasks = self.task_manager.get_all_tasks()
        
        # 如果在搜尋模式，重新過濾
        if self.filtered_tasks:
            search_text = self.search_entry.get().strip().lower()
            if search_text:
                self._filter_tasks(search_text)
            else:
                self._show_all_tasks()
        else:
            self._refresh_task_list()
        
        self._update_status(f"已刪除 {len(tasks_to_delete)} 個任務")
    
    def _set_reminder(self):
        """設定提醒"""
        selected_indices = self.task_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("警告", "請選擇要設定提醒的任務！")
            return
        
        # 只處理第一個選中的任務
        index = selected_indices[0]
        display_tasks = self.filtered_tasks if self.filtered_tasks else self.original_tasks
        
        if index < len(display_tasks):
            task = display_tasks[index]
            remind_time = self._show_reminder_dialog(task)
            
            if remind_time is not None:
                if remind_time is False:  # 清除提醒
                    task.remind_at = None
                    self.reminder_manager.remove_reminder(task.id)
                    self._update_status(f"已清除任務提醒: {task.title}")
                else:  # 設定提醒
                    task.set_reminder(remind_time)
                    self.reminder_manager.add_reminder(task)
                    self._update_status(f"已設定提醒: {task.title} - {remind_time.strftime('%m/%d %H:%M')}")
                
                self.task_manager.save_tasks()
                self._refresh_task_list(use_filtered=bool(self.filtered_tasks))
    
    def _show_reminder_dialog(self, task: Task):
        """顯示提醒設定對話框"""
        dialog = ReminderDialog(self.root, task, self.dark_mode_var.get())
        return dialog.result
    
    def _clear_completed_tasks(self):
        """清理已完成的任務"""
        completed_tasks = [task for task in self.task_manager.get_all_tasks() if task.completed]
        
        if not completed_tasks:
            messagebox.showinfo("資訊", "沒有已完成的任務需要清理。")
            return
        
        if messagebox.askyesno("確認", f"確定要清理 {len(completed_tasks)} 個已完成的任務嗎？"):
            for task in completed_tasks:
                self.task_manager.remove_task(task.id)
                self.reminder_manager.remove_reminder(task.id)
            
            self.task_manager.save_tasks()
            
            # 重新載入任務
            self.original_tasks = self.task_manager.get_all_tasks()
            
            # 如果在搜尋模式，重新過濾
            if self.filtered_tasks:
                search_text = self.search_entry.get().strip().lower()
                if search_text:
                    self._filter_tasks(search_text)
                else:
                    self._show_all_tasks()
            else:
                self._refresh_task_list()
            
            self._update_status(f"已清理 {len(completed_tasks)} 個已完成的任務")
    
    def _show_statistics(self):
        """顯示統計資訊"""
        all_tasks = self.task_manager.get_all_tasks()
        total_tasks = len(all_tasks)
        completed_tasks = len([task for task in all_tasks if task.completed])
        pending_tasks = total_tasks - completed_tasks
        
        # 分類統計
        category_stats = {}
        for task in all_tasks:
            if task.category not in category_stats:
                category_stats[task.category] = {"total": 0, "completed": 0}
            category_stats[task.category]["total"] += 1
            if task.completed:
                category_stats[task.category]["completed"] += 1
        
        # 提醒統計
        upcoming_reminders = self.reminder_manager.get_upcoming_reminders(24)
        
        # 建立統計視窗
        stats_window = tk.Toplevel(self.root)
        stats_window.title("統計資訊")
        stats_window.geometry("400x350")
        stats_window.resizable(False, False)
        stats_window.transient(self.root)
        stats_window.grab_set()
        
        # 整體統計
        overall_frame = ttk.LabelFrame(stats_window, text="整體統計", padding="10")
        overall_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(overall_frame, text=f"總任務數: {total_tasks}").pack(anchor=tk.W)
        ttk.Label(overall_frame, text=f"已完成: {completed_tasks}").pack(anchor=tk.W)
        ttk.Label(overall_frame, text=f"進行中: {pending_tasks}").pack(anchor=tk.W)
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        ttk.Label(overall_frame, text=f"完成率: {completion_rate:.1f}%").pack(anchor=tk.W)
        
        # 分類統計
        category_frame = ttk.LabelFrame(stats_window, text="分類統計", padding="10")
        category_frame.pack(fill=tk.X, padx=10, pady=5)
        
        for category, stats in category_stats.items():
            rate = (stats["completed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            ttk.Label(category_frame, 
                     text=f"{category}: {stats['completed']}/{stats['total']} ({rate:.1f}%)").pack(anchor=tk.W)
        
        # 提醒統計
        reminder_frame = ttk.LabelFrame(stats_window, text="即將到來的提醒", padding="10")
        reminder_frame.pack(fill=tk.X, padx=10, pady=5)
        
        if upcoming_reminders:
            for reminder in upcoming_reminders[:5]:  # 只顯示前5個
                time_str = reminder["remind_at"].strftime("%m/%d %H:%M")
                ttk.Label(reminder_frame, text=f"{time_str} - {reminder['task_title'][:20]}...").pack(anchor=tk.W)
        else:
            ttk.Label(reminder_frame, text="沒有即將到來的提醒").pack(anchor=tk.W)
        
        # 關閉按鈕
        ttk.Button(stats_window, text="關閉", command=stats_window.destroy).pack(pady=10)
    
    def _reload_tasks(self):
        """重新載入任務"""
        self._load_tasks()
        self._clear_search()  # 清除搜尋過濾
        self._update_status("任務已重新載入")
    
    def _on_task_double_click(self, event):
        """任務雙擊事件"""
        self._toggle_task_completion()
    
    def _on_task_right_click(self, event):
        """任務右鍵點擊事件"""
        # 選中右鍵點擊的項目
        index = self.task_listbox.nearest(event.y)
        self.task_listbox.selection_clear(0, tk.END)
        self.task_listbox.selection_set(index)
        
        # 顯示右鍵選單
        self._show_context_menu(event)
    
    def _show_context_menu(self, event):
        """顯示右鍵選單"""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="✓ 標記完成", command=self._toggle_task_completion)
        context_menu.add_command(label="⏰ 設定提醒", command=self._set_reminder)
        context_menu.add_separator()
        context_menu.add_command(label="🗑️ 刪除任務", command=self._delete_selected_tasks)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def _on_reminder_triggered(self, reminder: dict):
        """提醒觸發時的回調"""
        try:
            # 創建通知視窗
            notification_window = tk.Toplevel(self.root)
            notification_window.title("任務提醒")
            notification_window.geometry("320x180")  # 增加寬度和高度
            notification_window.resizable(False, False)
            
            # 設定視窗置頂
            notification_window.attributes('-topmost', True)
            
            # 根據主題設定背景
            if self.dark_mode_var.get():
                notification_window.configure(bg='#2b2b2b')
            else:
                notification_window.configure(bg='SystemButtonFace')
            
            # 主框架，增加內邊距
            main_frame = ttk.Frame(notification_window, padding="15")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 內容標籤
            title_label = ttk.Label(
                main_frame, 
                text="⏰ 任務提醒",
                font=("Microsoft JhengHei", 14, "bold")
            )
            title_label.pack(pady=(0, 10))
            
            task_label = ttk.Label(
                main_frame,
                text=f"任務: {reminder['task_title']}",
                font=("Microsoft JhengHei", 12),
                wraplength=280
            )
            task_label.pack(pady=(0, 5))
            
            time_label = ttk.Label(
                main_frame,
                text=f"提醒時間: {reminder['remind_at'].strftime('%Y-%m-%d %H:%M')}",
                font=("Microsoft JhengHei", 12)
            )
            time_label.pack(pady=(0, 15))
            
            # 確認按鈕框架
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X)
            
            # 確認按鈕 - 使用較大的尺寸和醒目的樣式
            confirm_button = ttk.Button(
                button_frame,
                text="確認",
                command=notification_window.destroy,
                width=15
            )
            confirm_button.pack(pady=5)
            
            # 居中顯示
            notification_window.update_idletasks()
            x = (notification_window.winfo_screenwidth() - notification_window.winfo_width()) // 2
            y = (notification_window.winfo_screenheight() - notification_window.winfo_height()) // 2
            notification_window.geometry(f"+{x}+{y}")
            
            # 設定焦點到確認按鈕
            confirm_button.focus_set()
            
            # 綁定 Enter 鍵
            notification_window.bind('<Return>', lambda e: notification_window.destroy())
            
            # 5秒後自動關閉
            notification_window.after(5000, notification_window.destroy)
            
        except Exception as e:
            print(f"顯示通知視窗錯誤: {e}")
    
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
    
    def __init__(self, parent, task: Task, is_dark_mode: bool = False):
        """初始化對話框"""
        self.result = None
        self.is_dark_mode = is_dark_mode
        
        # 創建對話框視窗
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"設定提醒 - {task.title}")
        self.dialog.geometry("450x350")  # 進一步增加尺寸
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 根據主題設定背景
        if self.is_dark_mode:
            self.dialog.configure(bg='#2b2b2b')
        else:
            self.dialog.configure(bg='SystemButtonFace')
        
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
        main_frame = ttk.Frame(self.dialog, padding="15")  # 增加內邊距
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 快速選項
        ttk.Label(main_frame, text="快速選項:", font=("Microsoft JhengHei", 12, "bold")).pack(anchor=tk.W, pady=(0, 8))
        
        # 快速選項容器，使用Grid佈局實現兩行三欄
        quick_container = ttk.Frame(main_frame)
        quick_container.pack(fill=tk.X, pady=(0, 15))
        
        # 配置網格權重，讓按鈕平均分佈
        for i in range(3):
            quick_container.columnconfigure(i, weight=1)
        
        # 快速提醒按鈕，兩行三欄佈局
        quick_options = ReminderHelper.get_quick_reminder_options()
        for i, option in enumerate(quick_options[:6]):  # 顯示前6個選項
            row = i // 3
            col = i % 3
            btn = ttk.Button(quick_container, text=option["label"], 
                           command=lambda opt=option: self._select_quick_option(opt),
                           width=12)  # 設定按鈕寬度
            btn.grid(row=row, column=col, sticky=(tk.W, tk.E), padx=3, pady=3)
        
        # 分隔線
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # 自定義時間
        ttk.Label(main_frame, text="自定義時間:", font=("Microsoft JhengHei", 12, "bold")).pack(anchor=tk.W, pady=(0, 8))
        
        time_frame = ttk.Frame(main_frame)
        time_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 日期輸入
        ttk.Label(time_frame, text="日期:", font=("Microsoft JhengHei", 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        self.date_entry = ttk.Entry(time_frame, width=12, font=("Microsoft JhengHei", 10))
        self.date_entry.grid(row=0, column=1, padx=(0, 15))
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # 時間輸入
        ttk.Label(time_frame, text="時間:", font=("Microsoft JhengHei", 10)).grid(row=0, column=2, sticky=tk.W, padx=(0, 8))
        self.time_entry = ttk.Entry(time_frame, width=10, font=("Microsoft JhengHei", 10))
        self.time_entry.grid(row=0, column=3)
        self.time_entry.insert(0, "09:00")
        
        # 分隔線
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # 按鈕區域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 左側：清除提醒按鈕
        clear_button = ttk.Button(button_frame, text="清除提醒", command=self._clear_reminder, width=12)
        clear_button.pack(side=tk.LEFT)
        
        # 右側：取消和確認按鈕
        cancel_button = ttk.Button(button_frame, text="取消", command=self._cancel, width=10)
        cancel_button.pack(side=tk.RIGHT, padx=(8, 0))
        
        confirm_button = ttk.Button(button_frame, text="確認", command=self._confirm, width=10)
        confirm_button.pack(side=tk.RIGHT)
        
        # 設定預設焦點到確認按鈕
        confirm_button.focus_set()
        
        # 綁定 Enter 和 Escape 鍵
        self.dialog.bind('<Return>', lambda e: self._confirm())
        self.dialog.bind('<Escape>', lambda e: self._cancel())
    
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
        self.result = False  # 設為False表示清除提醒
        self.dialog.destroy()


