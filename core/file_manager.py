"""
文件管理模块
负责所有数据的读写、目录管理、备份等功能
"""
import os
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Type, TypeVar
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class FileManager:
    """文件管理器"""
    
    def __init__(self, base_path: Optional[str] = None):
        """
        初始化文件管理器
        
        Args:
            base_path: 基础路径，默认为 main.py 所在目录
        """
        if base_path is None:
            # 获取项目根目录
            # 支持打包后的环境：如果是打包的exe，使用exe所在目录
            if getattr(sys, 'frozen', False):
                # 打包后的环境：使用exe所在目录
                self.base_path = Path(sys.executable).parent
            else:
                # 开发环境：使用源代码目录
                self.base_path = Path(__file__).parent.parent
        else:
            self.base_path = Path(base_path)
        
        # 定义目录结构
        self.data_dir = self.base_path / "data"
        self.output_dir = self.base_path / "outputs"
        
        # 数据子目录
        self.doctors_dir = self.data_dir / "doctors"
        self.visits_dir = self.data_dir / "visits"
        self.preparations_dir = self.data_dir / "preparations"
        self.reflections_dir = self.data_dir / "reflections"
        self.knowledge_dir = self.data_dir / "knowledge"
        self.settings_dir = self.data_dir / "settings"
        
        # 知识库子目录
        self.diseases_dir = self.knowledge_dir / "diseases"
        self.products_dir = self.knowledge_dir / "products"
        self.market_dir = self.knowledge_dir / "market"
        
        # 输出子目录
        self.reports_dir = self.output_dir / "reports"
        self.daily_tasks_dir = self.output_dir / "daily_tasks"
        self.learning_paths_dir = self.output_dir / "learning_paths"
        
        # 初始化目录
        self._init_directories()
    
    def _init_directories(self) -> None:
        """创建所有必要的目录"""
        directories = [
            self.doctors_dir,
            self.visits_dir,
            self.preparations_dir,
            self.reflections_dir,
            self.diseases_dir,
            self.products_dir,
            self.market_dir,
            self.settings_dir,
            self.reports_dir,
            self.daily_tasks_dir,
            self.learning_paths_dir,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        # 初始化配置文件
        config_file = self.settings_dir / "config.json"
        if not config_file.exists():
            self._create_default_config(config_file)
    
    def _create_default_config(self, config_file: Path) -> None:
        """创建默认配置文件"""
        default_config = {
            "ai_enabled": False,
            "deepseek_api_key": "",
            "deepseek_base_url": "https://api.deepseek.com",
            "deepseek_model": "deepseek-chat",
            "theme": "dark",
            "language": "zh-CN"
        }
        self.write_json(config_file, default_config)
    
    # ==================== 通用文件操作 ====================
    
    def read_json(self, file_path: Path) -> Optional[dict]:
        """
        读取 JSON 文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            解析后的字典，如果文件不存在返回 None
        """
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误: {file_path} - {e}")
            return None
        except Exception as e:
            print(f"读取文件错误: {file_path} - {e}")
            return None
    
    def write_json(self, file_path: Path, data: dict) -> bool:
        """
        写入 JSON 文件
        
        Args:
            file_path: 文件路径
            data: 要写入的数据
            
        Returns:
            是否成功
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            return True
        except Exception as e:
            print(f"写入文件错误: {file_path} - {e}")
            return False
    
    def write_markdown(self, file_path: Path, content: str) -> bool:
        """
        写入 Markdown 文件
        
        Args:
            file_path: 文件路径
            content: Markdown 内容
            
        Returns:
            是否成功
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"写入文件错误: {file_path} - {e}")
            return False
    
    def read_markdown(self, file_path: Path) -> Optional[str]:
        """读取 Markdown 文件"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            return None
        except Exception as e:
            print(f"读取文件错误: {file_path} - {e}")
            return None
    
    # ==================== 模型操作 ====================
    
    def save_model(self, directory: Path, model: BaseModel, filename: str) -> bool:
        """
        保存 Pydantic 模型到 JSON 文件
        
        Args:
            directory: 目标目录
            model: Pydantic 模型实例
            filename: 文件名（不含扩展名）
            
        Returns:
            是否成功
        """
        file_path = directory / f"{filename}.json"
        return self.write_json(file_path, model.model_dump())
    
    def load_model(self, directory: Path, filename: str, model_class: Type[T]) -> Optional[T]:
        """
        从 JSON 文件加载 Pydantic 模型
        
        Args:
            directory: 目标目录
            filename: 文件名（不含扩展名）
            model_class: 模型类
            
        Returns:
            模型实例，如果不存在返回 None
        """
        file_path = directory / f"{filename}.json"
        data = self.read_json(file_path)
        if data:
            try:
                return model_class(**data)
            except Exception as e:
                print(f"模型解析错误: {file_path} - {e}")
                return None
        return None
    
    def list_files(self, directory: Path, extension: str = ".json") -> List[str]:
        """
        列出目录下的所有文件
        
        Args:
            directory: 目标目录
            extension: 文件扩展名
            
        Returns:
            文件名列表（不含扩展名）
        """
        if not directory.exists():
            return []
        
        files = []
        for f in directory.iterdir():
            if f.is_file() and f.suffix == extension:
                files.append(f.stem)
        return sorted(files)
    
    def delete_file(self, directory: Path, filename: str, extension: str = ".json") -> bool:
        """删除文件"""
        file_path = directory / f"{filename}{extension}"
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"删除文件错误: {file_path} - {e}")
            return False
    
    # ==================== 备份功能 ====================
    
    def backup_data(self, backup_name: Optional[str] = None) -> Optional[Path]:
        """
        备份整个数据目录
        
        Args:
            backup_name: 备份名称，默认使用当前时间戳
            
        Returns:
            备份文件路径
        """
        if backup_name is None:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_dir = self.base_path / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        backup_path = backup_dir / backup_name
        
        try:
            shutil.copytree(self.data_dir, backup_path)
            return backup_path
        except Exception as e:
            print(f"备份错误: {e}")
            return None
    
    # ==================== 配置管理 ====================
    
    def get_config(self) -> dict:
        """获取系统配置"""
        config_file = self.settings_dir / "config.json"
        config = self.read_json(config_file)
        if config is None:
            self._create_default_config(config_file)
            config = self.read_json(config_file)
        return config or {}
    
    def update_config(self, updates: dict) -> bool:
        """更新系统配置"""
        config = self.get_config()
        config.update(updates)
        config_file = self.settings_dir / "config.json"
        return self.write_json(config_file, config)
    
    # ==================== 搜索功能 ====================
    
    def search_files(self, directory: Path, keyword: str) -> List[dict]:
        """
        在指定目录中搜索包含关键词的文件
        
        Args:
            directory: 搜索目录
            keyword: 搜索关键词
            
        Returns:
            匹配的文件信息列表
        """
        results = []
        keyword_lower = keyword.lower()
        
        for filename in self.list_files(directory):
            data = self.read_json(directory / f"{filename}.json")
            if data:
                # 将数据转为字符串进行搜索
                content = json.dumps(data, ensure_ascii=False).lower()
                if keyword_lower in content:
                    results.append({
                        "filename": filename,
                        "data": data
                    })
        
        return results


# 创建全局实例
file_manager = FileManager()
