"""
客户追踪管理服务
实现4张核心表格的管理功能
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict
import pandas as pd

from core.customer_tracking_models import (
    CustomerDevelopment, FollowUpRecord, CustomerClassification,
    CustomerStatistics, DevelopmentChannel, CustomerLevel, FollowUpStatus
)
from core.file_manager import file_manager


class CustomerTrackingService:
    """客户追踪管理服务"""
    
    def __init__(self):
        self.data_dir = file_manager.data_dir / "customer_tracking"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 4张表格的数据文件
        self.development_file = self.data_dir / "development.json"
        self.followup_file = self.data_dir / "followup.json"
        self.classification_file = self.data_dir / "classification.json"
        self.statistics_file = self.data_dir / "statistics.json"
    
    # ==================== 表1：客户开发表 ====================
    
    def create_development_record(
        self,
        doctor_id: str,
        doctor_name: str,
        hospital: str = "",
        department: str = "",
        development_channel: str = "学术会议",
        channel_detail: str = "",
        referrer: str = "",
        phone: str = "",
        wechat: str = "",
        first_contact_date: Optional[datetime] = None,
        phone_connected_date: Optional[datetime] = None,
        wechat_added_date: Optional[datetime] = None,
        group_created_date: Optional[datetime] = None,
        hospital_level: str = "",
        doctor_influence: str = "",
        prescription_volume: str = "",
        notes: str = ""
    ) -> CustomerDevelopment:
        """创建客户开发记录"""
        record_id = f"dev_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        record = CustomerDevelopment(
            record_id=record_id,
            doctor_id=doctor_id,
            doctor_name=doctor_name,
            hospital=hospital,
            department=department,
            development_channel=development_channel,
            channel_detail=channel_detail,
            referrer=referrer,
            phone=phone,
            wechat=wechat,
            first_contact_date=first_contact_date or datetime.now(),
            phone_connected_date=phone_connected_date,
            wechat_added_date=wechat_added_date,
            group_created_date=group_created_date,
            hospital_level=hospital_level,
            doctor_influence=doctor_influence,
            prescription_volume=prescription_volume,
            notes=notes
        )
        
        # 保存
        records = self._load_development_records()
        records.append(record.dict())
        self._save_development_records(records)
        
        # 同时创建客户分类记录（初始为未分类）
        self.create_classification_record(
            doctor_id=doctor_id,
            doctor_name=doctor_name,
            hospital=hospital,
            department=department
        )
        
        return record
    
    def get_development_record(self, doctor_id: str) -> Optional[CustomerDevelopment]:
        """获取客户开发记录"""
        records = self._load_development_records()
        for r in records:
            if r.get('doctor_id') == doctor_id:
                return CustomerDevelopment(**r)
        return None
    
    def update_development_record(self, record_id: str, updates: Dict[str, Any]) -> bool:
        """更新客户开发记录"""
        records = self._load_development_records()
        for i, r in enumerate(records):
            if r.get('record_id') == record_id:
                r.update(updates)
                r['updated_at'] = datetime.now().isoformat()
                records[i] = r
                self._save_development_records(records)
                return True
        return False
    
    def list_development_records(
        self,
        channel: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[CustomerDevelopment]:
        """列出客户开发记录"""
        records = self._load_development_records()
        result = []
        
        for r in records:
            # 筛选条件
            if channel and r.get('development_channel') != channel:
                continue
            
            if start_date:
                created = datetime.fromisoformat(r.get('created_at'))
                if created < start_date:
                    continue
            
            if end_date:
                created = datetime.fromisoformat(r.get('created_at'))
                if created > end_date:
                    continue
            
            result.append(CustomerDevelopment(**r))
        
        return result
    
    # ==================== 表2：客户追踪表 ====================
    
    def create_followup_record(
        self,
        doctor_id: str,
        doctor_name: str,
        follow_method: str = "微信",
        opening_script: str = "",
        content: str = "",
        customer_replied: bool = False,
        reply_content: str = "",
        reply_date: Optional[datetime] = None,
        effect_score: int = 3,
        notes: str = ""
    ) -> FollowUpRecord:
        """创建跟进记录"""
        follow_id = f"follow_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        # 计算未回复天数
        days_no_reply = 0
        if not customer_replied:
            days_no_reply = (datetime.now() - datetime.now()).days
        
        # 根据客户等级建议下次跟进时间
        classification = self.get_classification_record(doctor_id)
        next_follow_days = 15  # 默认
        if classification:
            next_follow_days = classification.suggested_follow_days
        
        record = FollowUpRecord(
            follow_id=follow_id,
            doctor_id=doctor_id,
            doctor_name=doctor_name,
            follow_method=follow_method,
            opening_script=opening_script,
            content=content,
            customer_replied=customer_replied,
            reply_content=reply_content,
            reply_date=reply_date,
            days_no_reply=days_no_reply,
            next_follow_date=datetime.now() + timedelta(days=next_follow_days),
            follow_status=FollowUpStatus.REPLIED if customer_replied else FollowUpStatus.NO_REPLY,
            effect_score=effect_score,
            notes=notes
        )
        
        # 保存
        records = self._load_followup_records()
        records.append(record.dict())
        self._save_followup_records(records)
        
        # 更新客户分类统计
        self._update_classification_stats(doctor_id, customer_replied)
        
        return record
    
    def list_followup_records(
        self,
        doctor_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None
    ) -> List[FollowUpRecord]:
        """列出跟进记录"""
        records = self._load_followup_records()
        result = []
        
        for r in records:
            if doctor_id and r.get('doctor_id') != doctor_id:
                continue
            
            if status and r.get('follow_status') != status:
                continue
            
            if start_date:
                follow_date = datetime.fromisoformat(r.get('follow_date'))
                if follow_date < start_date:
                    continue
            
            if end_date:
                follow_date = datetime.fromisoformat(r.get('follow_date'))
                if follow_date > end_date:
                    continue
            
            result.append(FollowUpRecord(**r))
        
        return sorted(result, key=lambda x: x.follow_date, reverse=True)
    
    def get_pending_followups(self) -> List[Dict[str, Any]]:
        """获取待跟进列表"""
        classifications = self._load_classification_records()
        pending = []
        
        for c in classifications:
            doctor_id = c.get('doctor_id')
            last_contact = c.get('last_contact_date')
            suggested_days = c.get('suggested_follow_days', 15)
            
            if last_contact:
                last_date = datetime.fromisoformat(last_contact)
                days_passed = (datetime.now() - last_date).days
                
                if days_passed >= suggested_days:
                    pending.append({
                        'doctor_id': doctor_id,
                        'doctor_name': c.get('doctor_name'),
                        'customer_level': c.get('customer_level'),
                        'days_since_last_contact': days_passed,
                        'suggested_follow_days': suggested_days,
                        'overdue_days': days_passed - suggested_days
                    })
        
        return sorted(pending, key=lambda x: x['overdue_days'], reverse=True)
    
    # ==================== 表3：客户分类表 ====================
    
    def create_classification_record(
        self,
        doctor_id: str,
        doctor_name: str,
        hospital: str = "",
        department: str = "",
        customer_level: str = "未分类",
        level_reason: str = ""
    ) -> CustomerClassification:
        """创建客户分类记录"""
        classification_id = f"class_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        # 根据等级设置跟进频率
        follow_days_map = {
            "A类": 5,   # A类：3-5天
            "B类": 7,   # B类：7天
            "C类": 10,  # C类：10天
            "D类": 15,  # D类：15天
            "未分类": 15
        }
        
        record = CustomerClassification(
            classification_id=classification_id,
            doctor_id=doctor_id,
            doctor_name=doctor_name,
            hospital=hospital,
            department=department,
            customer_level=customer_level,
            level_reason=level_reason,
            suggested_follow_days=follow_days_map.get(customer_level, 15)
        )
        
        # 保存
        records = self._load_classification_records()
        records.append(record.dict())
        self._save_classification_records(records)
        
        return record
    
    def get_classification_record(self, doctor_id: str) -> Optional[CustomerClassification]:
        """获取客户分类记录"""
        records = self._load_classification_records()
        for r in records:
            if r.get('doctor_id') == doctor_id:
                return CustomerClassification(**r)
        return None
    
    def update_customer_level(
        self,
        doctor_id: str,
        new_level: str,
        reason: str = ""
    ) -> bool:
        """更新客户等级"""
        records = self._load_classification_records()
        
        for i, r in enumerate(records):
            if r.get('doctor_id') == doctor_id:
                old_level = r.get('customer_level')
                
                # 更新等级
                r['last_level'] = old_level
                r['customer_level'] = new_level
                r['level_change_date'] = datetime.now().isoformat()
                r['level_change_reason'] = reason
                r['updated_at'] = datetime.now().isoformat()
                
                # 更新跟进频率
                follow_days_map = {
                    "A类": 5, "B类": 7, "C类": 10, "D类": 15, "未分类": 15
                }
                r['suggested_follow_days'] = follow_days_map.get(new_level, 15)
                
                records[i] = r
                self._save_classification_records(records)
                return True
        
        return False
    
    def list_customers_by_level(self, level: Optional[str] = None) -> List[CustomerClassification]:
        """按等级列出客户"""
        records = self._load_classification_records()
        result = []
        
        for r in records:
            if level and r.get('customer_level') != level:
                continue
            result.append(CustomerClassification(**r))
        
        return sorted(result, key=lambda x: x.priority, reverse=True)
    
    def _update_classification_stats(self, doctor_id: str, replied: bool):
        """更新客户分类统计"""
        records = self._load_classification_records()
        
        for i, r in enumerate(records):
            if r.get('doctor_id') == doctor_id:
                r['total_contacts'] = r.get('total_contacts', 0) + 1
                if replied:
                    r['reply_count'] = r.get('reply_count', 0) + 1
                
                total = r['total_contacts']
                replies = r['reply_count']
                r['reply_rate'] = round(replies / total * 100, 2) if total > 0 else 0
                r['last_contact_date'] = datetime.now().isoformat()
                r['updated_at'] = datetime.now().isoformat()
                
                records[i] = r
                self._save_classification_records(records)
                break
    
    # ==================== 表4：统计分析表 ====================
    
    def generate_statistics(
        self,
        period: str = "周",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> CustomerStatistics:
        """生成统计报告"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=7)
        if not end_date:
            end_date = datetime.now()
        
        stat_id = f"stat_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 统计新增客户
        dev_records = self.list_development_records(start_date=start_date, end_date=end_date)
        new_customers = len(dev_records)
        new_customer_list = [r.doctor_id for r in dev_records]
        
        # 统计客户分类
        classifications = self._load_classification_records()
        level_counts = defaultdict(int)
        for c in classifications:
            level = c.get('customer_level', '未分类')
            level_counts[level] += 1
        
        # 统计跟进情况
        followups = self.list_followup_records(start_date=start_date, end_date=end_date)
        total_followups = len(followups)
        reply_count = sum(1 for f in followups if f.customer_replied)
        reply_rate = round(reply_count / total_followups * 100, 2) if total_followups > 0 else 0
        
        # 统计渠道
        channel_stats = defaultdict(int)
        for r in dev_records:
            channel_stats[r.development_channel] += 1
        
        stats = CustomerStatistics(
            stat_id=stat_id,
            period=period,
            start_date=start_date,
            end_date=end_date,
            new_customers=new_customers,
            new_customer_list=new_customer_list,
            a_level_count=level_counts.get('A类', 0),
            b_level_count=level_counts.get('B类', 0),
            c_level_count=level_counts.get('C类', 0),
            d_level_count=level_counts.get('D类', 0),
            total_follow_ups=total_followups,
            reply_count=reply_count,
            reply_rate=reply_rate,
            channel_stats=dict(channel_stats)
        )
        
        # 保存
        records = self._load_statistics_records()
        records.append(stats.dict())
        self._save_statistics_records(records)
        
        return stats
    
    # ==================== 导出功能 ====================
    
    def export_to_excel(
        self,
        export_type: str = "all",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        customer_level: Optional[str] = None
    ) -> str:
        """导出Excel表格"""
        output_dir = file_manager.output_dir / "customer_tracking"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = output_dir / f"客户管理_{export_type}_{timestamp}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            if export_type in ["all", "development"]:
                # 表1：客户开发表
                records = self.list_development_records(start_date=start_date, end_date=end_date)
                if records:
                    df = pd.DataFrame([r.dict() for r in records])
                    df.to_excel(writer, sheet_name='客户开发表', index=False)
            
            if export_type in ["all", "followup"]:
                # 表2：客户追踪表
                records = self.list_followup_records(start_date=start_date, end_date=end_date)
                if records:
                    df = pd.DataFrame([r.dict() for r in records])
                    df.to_excel(writer, sheet_name='客户追踪表', index=False)
            
            if export_type in ["all", "classification"]:
                # 表3：客户分类表
                records = self.list_customers_by_level(level=customer_level)
                if records:
                    df = pd.DataFrame([r.dict() for r in records])
                    df.to_excel(writer, sheet_name='客户分类表', index=False)
            
            if export_type in ["all", "statistics"]:
                # 表4：统计分析表
                records = self._load_statistics_records()
                if records:
                    df = pd.DataFrame(records)
                    df.to_excel(writer, sheet_name='统计分析表', index=False)
        
        return str(filename)
    
    # ==================== 数据持久化 ====================
    
    def _load_development_records(self) -> List[Dict]:
        """加载客户开发记录"""
        if self.development_file.exists():
            with open(self.development_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_development_records(self, records: List[Dict]):
        """保存客户开发记录"""
        with open(self.development_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2, default=str)
    
    def _load_followup_records(self) -> List[Dict]:
        """加载跟进记录"""
        if self.followup_file.exists():
            with open(self.followup_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_followup_records(self, records: List[Dict]):
        """保存跟进记录"""
        with open(self.followup_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2, default=str)
    
    def _load_classification_records(self) -> List[Dict]:
        """加载客户分类记录"""
        if self.classification_file.exists():
            with open(self.classification_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_classification_records(self, records: List[Dict]):
        """保存客户分类记录"""
        with open(self.classification_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2, default=str)
    
    def _load_statistics_records(self) -> List[Dict]:
        """加载统计记录"""
        if self.statistics_file.exists():
            with open(self.statistics_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_statistics_records(self, records: List[Dict]):
        """保存统计记录"""
        with open(self.statistics_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2, default=str)


# 创建全局服务实例
customer_tracking_service = CustomerTrackingService()
