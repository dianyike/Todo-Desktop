"""
任務儲存與載入邏輯模組
處理任務資料的本地JSON儲存
"""
import json
import os
from typing import List
from models import Task


class TaskStorage:
    """任務儲存管理類別"""
    
    def __init__(self, data_file: str = "data/tasks.json"):
        """
        初始化儲存管理器
        
        Args:
            data_file (str): 資料檔案路徑，預設為 data/tasks.json
        """
        self.data_file = data_file
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """確保資料目錄存在"""
        data_dir = os.path.dirname(self.data_file)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def save_tasks(self, tasks: List[Task]) -> bool:
        """
        儲存任務清單到JSON檔案
        
        Args:
            tasks (List[Task]): 任務清單
            
        Returns:
            bool: 儲存是否成功
        """
        try:
            # 轉換任務物件為字典清單
            tasks_data = [task.to_dict() for task in tasks]
            
            # 寫入JSON檔案
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"儲存任務失敗: {e}")
            return False
    
    def load_tasks(self) -> List[Task]:
        """
        從JSON檔案載入任務清單
        
        Returns:
            List[Task]: 任務清單
        """
        try:
            # 檢查檔案是否存在
            if not os.path.exists(self.data_file):
                print(f"資料檔案不存在: {self.data_file}，將建立新檔案")
                return []
            
            # 讀取JSON檔案
            with open(self.data_file, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
            
            # 轉換字典為任務物件
            tasks = [Task.from_dict(task_data) for task_data in tasks_data]
            
            print(f"成功載入 {len(tasks)} 個任務")
            return tasks
            
        except json.JSONDecodeError as e:
            print(f"JSON格式錯誤: {e}，將使用空的任務清單")
            return []
        except Exception as e:
            print(f"載入任務失敗: {e}")
            return []
    
    def backup_tasks(self, backup_suffix: str = None) -> bool:
        """
        備份任務檔案
        
        Args:
            backup_suffix (str): 備份檔案後綴，預設為當前時間戳
            
        Returns:
            bool: 備份是否成功
        """
        try:
            if not os.path.exists(self.data_file):
                print("原檔案不存在，無需備份")
                return True
            
            if backup_suffix is None:
                from datetime import datetime
                backup_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            backup_file = f"{self.data_file}.backup_{backup_suffix}"
            
            # 複製檔案
            import shutil
            shutil.copy2(self.data_file, backup_file)
            
            print(f"備份檔案已建立: {backup_file}")
            return True
            
        except Exception as e:
            print(f"備份失敗: {e}")
            return False
    
    def get_file_info(self) -> dict:
        """
        取得檔案資訊
        
        Returns:
            dict: 檔案資訊字典
        """
        try:
            if not os.path.exists(self.data_file):
                return {"exists": False}
            
            stat = os.stat(self.data_file)
            from datetime import datetime
            
            return {
                "exists": True,
                "path": self.data_file,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "created": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            return {"exists": False, "error": str(e)}


class TaskManager:
    """任務管理器類別，整合任務操作與儲存"""
    
    def __init__(self, data_file: str = "data/tasks.json"):
        """初始化任務管理器"""
        self.storage = TaskStorage(data_file)
        self.tasks: List[Task] = []
        self.load_tasks()
    
    def load_tasks(self):
        """載入任務"""
        self.tasks = self.storage.load_tasks()
    
    def save_tasks(self) -> bool:
        """儲存任務"""
        return self.storage.save_tasks(self.tasks)
    
    def add_task(self, task: Task):
        """新增任務"""
        self.tasks.append(task)
        self.save_tasks()
    
    def remove_task(self, task_id: str) -> bool:
        """移除任務"""
        original_length = len(self.tasks)
        self.tasks = [task for task in self.tasks if task.id != task_id]
        
        if len(self.tasks) < original_length:
            self.save_tasks()
            return True
        return False
    
    def get_task_by_id(self, task_id: str) -> Task:
        """根據ID取得任務"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def get_tasks_by_category(self, category: str) -> List[Task]:
        """根據分類取得任務"""
        return [task for task in self.tasks if task.category == category]
    
    def get_completed_tasks(self) -> List[Task]:
        """取得已完成任務"""
        return [task for task in self.tasks if task.completed]
    
    def get_pending_tasks(self) -> List[Task]:
        """取得待完成任務"""
        return [task for task in self.tasks if not task.completed]
    
    def get_all_tasks(self) -> List[Task]:
        """取得所有任務"""
        return self.tasks.copy()
    
    def clear_completed_tasks(self) -> int:
        """清除已完成任務，返回清除數量"""
        original_length = len(self.tasks)
        self.tasks = [task for task in self.tasks if not task.completed]
        removed_count = original_length - len(self.tasks)
        
        if removed_count > 0:
            self.save_tasks()
        
        return removed_count


