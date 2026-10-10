"""
医生管理服务
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from core.file_manager import file_manager
from core.data_models import Doctor, RelationshipStage, DecisionStyle
from core.ai_integration import ai_integration


class DoctorService:
    """医生管理服务"""
    
    def __init__(self):
        self.fm = file_manager
        self.ai = ai_integration
    
    def create_doctor(
        self,
        name: str,
        hospital: str = "",
        hospital_id: str = "",
        department: str = "",
        department_id: str = "",
        title: str = "",
        interests: List[str] = None,
        decision_style: Optional[str] = None,
        prescription_pattern: str = "",
        unmet_needs: str = "",
        relationship_stage: str = "初识",
        notes: str = ""
    ) -> Doctor:
        """创建医生档案"""
        
        # 生成 ID
        doctor_id = f"doctor_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        doctor = Doctor(
            doctor_id=doctor_id,
            name=name,
            hospital=hospital,
            hospital_id=hospital_id,
            department=department,
            department_id=department_id,
            title=title,
            interests=interests or [],
            decision_style=decision_style,
            prescription_pattern=prescription_pattern,
            unmet_needs=unmet_needs,
            relationship_stage=relationship_stage,
            notes=notes
        )
        
        # 保存
        self.fm.save_model(self.fm.doctors_dir, doctor, doctor_id)
        
        return doctor
    
    def update_doctor(self, doctor_id: str, updates: Dict[str, Any]) -> Optional[Doctor]:
        """更新医生档案"""
        doctor_path = self.fm.doctors_dir / f"{doctor_id}.json"
        data = self.fm.read_json(doctor_path)
        
        if not data:
            return None
        
        # 检查名称是否变更
        name_changed = 'name' in updates and updates['name'] != data.get('name')
        old_name = data.get('name')
        
        # 更新字段
        for key, value in updates.items():
            data[key] = value
        
        data["updated_at"] = datetime.now().isoformat()
        
        self.fm.write_json(doctor_path, data)
        
        # 如果名称变更，同步到所有相关数据
        if name_changed:
            from core.data_sync_service import data_sync_service
            stats = data_sync_service.sync_doctor_name_change(doctor_id, updates['name'])
            print(f"✓ 医生名称已同步: {old_name} -> {updates['name']}")
            print(f"  更新: 拜访{stats['visits']}条, 准备{stats['preparations']}条, "
                  f"联系人{stats['contacts']}条, 客户追踪{stats['customer_tracking']}条")
            
            # 使AI缓存失效
            data_sync_service.invalidate_ai_cache('doctor', doctor_id)
        
        return Doctor(**data)
    
    def get_doctor(self, doctor_id: str) -> Optional[Doctor]:
        """获取医生档案"""
        return self.fm.load_model(
            self.fm.doctors_dir,
            doctor_id,
            Doctor
        )
    
    def list_doctors(self) -> List[Dict[str, Any]]:
        """列出所有医生"""
        doctors = []
        for filename in self.fm.list_files(self.fm.doctors_dir):
            data = self.fm.read_json(self.fm.doctors_dir / f"{filename}.json")
            if data:
                doctors.append(data)
        
        # 按姓名排序
        return sorted(doctors, key=lambda x: x.get("name", ""))
    
    def delete_doctor(self, doctor_id: str) -> bool:
        """删除医生档案"""
        return self.fm.delete_file(self.fm.doctors_dir, doctor_id)
    
    def search_doctors(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索医生"""
        return self.fm.search_files(self.fm.doctors_dir, keyword)
    
    def get_doctors_by_stage(self, stage: str) -> List[Dict[str, Any]]:
        """按关系阶段筛选医生"""
        doctors = []
        for doc in self.list_doctors():
            if doc.get("relationship_stage") == stage:
                doctors.append(doc)
        return doctors
    
    def get_doctor_visits(self, doctor_id: str) -> List[Dict[str, Any]]:
        """获取医生的所有拜访记录"""
        visits = []
        for filename in self.fm.list_files(self.fm.visits_dir):
            if doctor_id in filename:
                data = self.fm.read_json(self.fm.visits_dir / f"{filename}.json")
                if data:
                    visits.append(data)
        
        return sorted(visits, key=lambda x: x.get("visit_date", ""), reverse=True)
    
    def generate_doctor_report(self, doctor_id: str) -> Optional[str]:
        """生成医生分析报告"""
        doctor = self.get_doctor(doctor_id)
        if not doctor:
            return None
        
        visits = self.get_doctor_visits(doctor_id)
        
        # 计算统计数据
        total_visits = len(visits)
        avg_effectiveness = 0
        if visits:
            effectiveness_scores = [v.get("response_effectiveness", 3) for v in visits]
            avg_effectiveness = sum(effectiveness_scores) / len(effectiveness_scores)
        
        content = f"""# 医生档案报告

## 基本信息
- **姓名**: {doctor.name}
- **医院**: {doctor.hospital}
- **科室**: {doctor.department}
- **职称**: {doctor.title}
- **关系阶段**: {doctor.relationship_stage}

## 特征分析
- **兴趣领域**: {', '.join(doctor.interests) or '未记录'}
- **决策风格**: {doctor.decision_style or '未识别'}
- **处方习惯**: {doctor.prescription_pattern or '未记录'}
- **未满足需求**: {doctor.unmet_needs or '未识别'}

## 拜访统计
- **总拜访次数**: {total_visits}
- **平均回应有效性**: {avg_effectiveness:.1f}/5

## 最近拜访记录
"""
        
        for visit in visits[:5]:
            content += f"- [{visit.get('visit_date')}] {visit.get('key_topics', '')[:50]}...\n"
        
        if not visits:
            content += "- 暂无拜访记录\n"
        
        content += f"""
## 备注
{doctor.notes or '无'}

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        
        # 保存报告
        filename = f"doctor_profile_{doctor_id}.md"
        self.fm.write_markdown(self.fm.reports_dir / filename, content)
        
        return content
    
    def get_ai_relationship_analysis(self, doctor_id: str) -> Optional[str]:
        """获取AI关系分析"""
        if not self.ai.is_enabled:
            return None
        
        doctor = self.get_doctor(doctor_id)
        if not doctor:
            return None
        
        visits = self.get_doctor_visits(doctor_id)
        
        return self.ai.analyze_doctor_relationship(doctor.model_dump(), visits)


# 创建全局实例
doctor_service = DoctorService()
