#!/usr/bin/env python3
"""
Todo-Desktop 應用自動打包腳本
使用 PyInstaller 將應用程式打包為 Windows 可執行檔

使用方法:
    python build_exe.py
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


class TodoAppBuilder:
    """Todo 應用打包器"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.dist_dir = self.project_dir / "dist"
        self.build_dir = self.project_dir / "build"
        self.spec_file = self.project_dir / "main.spec"
        
    def clean_build_files(self):
        """清理之前的建置檔案"""
        print("🧹 清理之前的建置檔案...")
        
        # 清理目錄
        dirs_to_clean = [self.dist_dir, self.build_dir]
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   已清理: {dir_path}")
        
        # 清理spec檔案
        if self.spec_file.exists():
            self.spec_file.unlink()
            print(f"   已清理: {self.spec_file}")
        
        # 清理 __pycache__
        for pycache in self.project_dir.rglob("__pycache__"):
            if pycache.is_dir():
                shutil.rmtree(pycache)
                print(f"   已清理: {pycache}")
    
    def check_dependencies(self):
        """檢查打包依賴"""
        print("🔍 檢查打包依賴...")
        
        try:
            import PyInstaller
            print(f"   ✓ PyInstaller 版本: {PyInstaller.__version__}")
        except ImportError:
            print("   ❌ PyInstaller 未安裝")
            print("   請執行: pip install pyinstaller")
            return False
        
        # 檢查主要程式檔案
        main_file = self.project_dir / "main.py"
        if not main_file.exists():
            print(f"   ❌ 主程式檔案不存在: {main_file}")
            return False
        
        print("   ✓ 所有依賴檢查通過")
        return True
    
    def create_icon(self):
        """建立應用程式圖示 (如果沒有的話)"""
        icon_path = self.project_dir / "images" / "icon.ico"
        if not icon_path.exists():
            print("   ℹ️  未找到圖示檔案，將使用預設圖示")
            return None
        print(f"   ✓ 找到應用程式圖示: {icon_path}")
        return str(icon_path)
    
    def build_executable(self):
        """建置可執行檔"""
        print("🔨 開始建置可執行檔...")
        
        # PyInstaller 參數
        cmd = [
            "python", "-m", "PyInstaller",
            "--onefile",                    # 打包成單一檔案
            "--windowed",                   # 不顯示控制台視窗
            "--name=Todo-Desktop",          # 執行檔名稱
            "--distpath=dist",              # 輸出目錄
            "--workpath=build",             # 暫存目錄
            "--clean",                      # 清理暫存檔案
        ]
        
        # 添加圖示 (如果存在)
        icon_path = self.create_icon()
        if icon_path:
            cmd.extend(["--icon", icon_path])
        
        # 添加資料檔案
        cmd.extend([
            "--add-data", "data;data",      # 包含資料目錄
            "--add-data", "images;images",  # 包含圖示資源目錄
        ])
        
        # 主程式檔案
        cmd.append("main.py")
        
        print(f"   執行命令: {' '.join(cmd)}")
        
        try:
            # 執行 PyInstaller
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_dir)
            
            if result.returncode == 0:
                print("   ✓ 建置成功完成")
                return True
            else:
                print("   ❌ 建置失敗")
                print("   錯誤輸出:")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"   ❌ 建置過程發生錯誤: {e}")
            return False
    
    def post_build_cleanup(self):
        """建置後清理"""
        print("🧹 建置後清理...")
        
        # 清理建置目錄
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            print("   已清理建置暫存檔案")
        
        # 清理 spec 檔案
        if self.spec_file.exists():
            self.spec_file.unlink()
            print("   已清理 spec 檔案")
    
    def verify_build(self):
        """驗證建置結果"""
        print("🔍 驗證建置結果...")
        
        exe_path = self.dist_dir / "Todo-Desktop.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"   ✓ 可執行檔已生成: {exe_path}")
            print(f"   檔案大小: {size_mb:.2f} MB")
            return True
        else:
            print(f"   ❌ 未找到可執行檔: {exe_path}")
            return False
    
    def show_results(self):
        """顯示建置結果"""
        print("\n" + "="*50)
        print("📦 Todo-Desktop 打包完成!")
        print("="*50)
        
        exe_path = self.dist_dir / "Todo-Desktop.exe"
        if exe_path.exists():
            print(f"✅ 可執行檔位置: {exe_path.absolute()}")
            print("✅ 您可以直接運行此檔案")
            print("如果有任何問題，請寄信至開發者或查看 GitHub 問題頁面")
        else:
            print("❌ 打包失敗，請檢查錯誤訊息")
    
    def build(self):
        """執行完整建置流程"""
        print("🚀 開始 Todo-Desktop 應用程式打包...")
        print("="*50)
        
        # 執行建置步驟
        if not self.check_dependencies():
            return False
        
        self.clean_build_files()
        
        if not self.build_executable():
            return False
        
        if not self.verify_build():
            return False
        
        self.post_build_cleanup()
        self.show_results()
        
        return True


def main():
    """主函式"""
    try:
        builder = TodoAppBuilder()
        success = builder.build()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n❌ 用戶中斷建置過程")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ 建置過程發生未預期的錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 