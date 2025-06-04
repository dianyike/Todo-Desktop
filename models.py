"""
任務資料模型模組
提供 Task 類別定義和相關資料結構
"""
import uuid
from datetime import datetime
from typing import Optional


class Task:
    """代辦任務類別"""
    
    def __init__(self, title: str, category: str = "一般", remind_at: Optional[datetime] = None):
        """
        初始化任務
        
        Args:
            title (str): 任務標題
            category (str): 任務分類，預設為"一般"
            remind_at (Optional[datetime]): 提醒時間，可選
        """
        self.id = str(uuid.uuid4())
        self.title = title
        self.category = category
        self.completed = False
        self.remind_at = remind_at
        self.created_at = datetime.now()
        self.completed_at: Optional[datetime] = None
    
    def mark_completed(self):
        """標記任務為已完成"""
        self.completed = True
        self.completed_at = datetime.now()
    
    def mark_uncompleted(self):
        """標記任務為未完成"""
        self.completed = False
        self.completed_at = None
    
    def set_reminder(self, remind_at: datetime):
        """設定提醒時間"""
        self.remind_at = remind_at
    
    def to_dict(self) -> dict:
        """轉換為字典格式，用於JSON儲存"""
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "completed": self.completed,
            "remind_at": self.remind_at.isoformat() if self.remind_at else None,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """從字典建立任務物件"""
        task = cls.__new__(cls)
        task.id = data["id"]
        task.title = data["title"]
        task.category = data["category"]
        task.completed = data["completed"]
        task.remind_at = datetime.fromisoformat(data["remind_at"]) if data["remind_at"] else None
        task.created_at = datetime.fromisoformat(data["created_at"])
        task.completed_at = datetime.fromisoformat(data["completed_at"]) if data["completed_at"] else None
        return task
    
    def __str__(self) -> str:
        """字串表示"""
        status = "✓" if self.completed else "○"
        return f"{status} {self.title} [{self.category}]"
    
    def __repr__(self) -> str:
        """詳細字串表示"""
        return f"Task(id='{self.id}', title='{self.title}', category='{self.category}', completed={self.completed})"


class TaskCategories: #如果要自己定義任務分類，可以使用這個類別
    """任務分類常數"""
    GENERAL = "一般"
    WORK = "工作"
    LIFE = "生活"
    STUDY = "學習"
    HEALTH = "健康"
    
    @classmethod 
    def get_all_categories(cls) -> list:
        """取得所有分類清單"""
        return [cls.GENERAL, cls.WORK, cls.LIFE, cls.STUDY, cls.HEALTH] #這裡記得把自定義任務分類給加上去


