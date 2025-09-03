import json
import os
import shutil
from typing import Dict, List, Any, Optional


class DataManager:
    """数据管理器，负责读写JSON数据文件"""
    
    def __init__(self, data_file='data/trading_data.json'):
        """
        初始化数据管理器
        
        参数:
            data_file: 数据文件路径，相对于项目根目录
        """
        # 确保路径是相对于项目根目录的绝对路径
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_file = os.path.join(base_dir, data_file)
        self.temp_file = os.path.join(base_dir, 'data/trading_data_temp.json')
        self.backup_file = os.path.join(base_dir, 'data/trading_data_backup.json')
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        # 加载数据
        self.data = self._load_data()
        # 兼容老文件：补充缺失的键
        self.data.setdefault('positions', [])
        self.data.setdefault('history', [])
        self.data.setdefault('plans', [])
        self.data.setdefault('last_prices', {})  # 代码->最近一次成功价格
    
    def _load_data(self) -> Dict[str, Any]:
        """从JSON文件加载数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # 如果文件不存在，返回默认空数据结构
            return self._create_default_data()
        except json.JSONDecodeError:
            # 如果JSON解析错误，尝试恢复备份
            if os.path.exists(self.backup_file):
                shutil.copy2(self.backup_file, self.data_file)
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self._create_default_data()
    
    def _create_default_data(self) -> Dict[str, Any]:
        """创建默认数据结构"""
        return {
            'positions': [],
            'history': [],
            'plans': [],
            'last_prices': {}
        }
    
    def save_data(self) -> bool:
        """
        安全保存数据到JSON文件
        
        返回:
            bool: 保存是否成功
        """
        try:
            # 1. 保存到临时文件
            with open(self.temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            
            # 2. 备份原文件（如果存在）
            if os.path.exists(self.data_file):
                shutil.copy2(self.data_file, self.backup_file)
            
            # 3. 替换原文件
            shutil.move(self.temp_file, self.data_file)
            
            return True
        except Exception as e:
            # 恢复备份文件（如果存在）
            if os.path.exists(self.backup_file):
                shutil.copy2(self.backup_file, self.data_file)
            print(f"保存数据时发生错误: {str(e)}")
            return False
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """获取所有持仓数据（不依赖派生字段，如market_value/commission）"""
        return self.data.get('positions', [])
    
    def get_history(self) -> List[Dict[str, Any]]:
        """获取所有交易历史数据（每笔含commission可选）"""
        return self.data.get('history', [])
    
    def get_plans(self) -> List[Dict[str, Any]]:
        """获取所有止盈止损计划"""
        return self.data.get('plans', [])
    
    def get_last_prices(self) -> Dict[str, float]:
        """获取最近一次成功的价格缓存"""
        return self.data.get('last_prices', {})
    
    def update_last_prices(self, mapping: Dict[str, float]) -> bool:
        """合并并保存最近价格缓存"""
        if not mapping:
            return True
        self.data.setdefault('last_prices', {}).update({k: float(v) for k, v in mapping.items() if k})
        return self.save_data()
    
    def add_position(self, position: Dict[str, Any]) -> bool:
        self.data.setdefault('positions', []).append(position)
        return self.save_data()
    
    def add_history(self, history: Dict[str, Any]) -> bool:
        self.data.setdefault('history', []).append(history)
        return self.save_data()
    
    def add_plan(self, plan: Dict[str, Any]) -> bool:
        self.data.setdefault('plans', []).append(plan)
        return self.save_data()
    
    def update_plan(self, plan_id: str, updates: Dict[str, Any]) -> bool:
        plans = self.data.get('plans', [])
        for p in plans:
            if p.get('id') == plan_id:
                p.update(updates)
                return self.save_data()
        return False
    
    def delete_plan(self, plan_id: str) -> bool:
        plans = self.data.get('plans', [])
        idx = next((i for i, p in enumerate(plans) if p.get('id') == plan_id), -1)
        if idx >= 0:
            del plans[idx]
            return self.save_data()
        return False
    
    def find_latest_plan_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        plans = [p for p in self.data.get('plans', []) if p.get('name') == name]
        if not plans:
            return None
        try:
            plans.sort(key=lambda x: x.get('created_at', '' ))
        except Exception:
            pass
        return plans[-1] if plans else None
    
    def delete_position(self, index: int) -> bool:
        if 0 <= index < len(self.data['positions']):
            del self.data['positions'][index]
            return self.save_data()
        return False
    
    def delete_history(self, index: int) -> bool:
        if 0 <= index < len(self.data['history']):
            del self.data['history'][index]
            return self.save_data()
        return False