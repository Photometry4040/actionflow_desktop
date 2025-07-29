"""
JSON 데이터 관리 유틸리티
SQLite 대신 JSON 파일을 사용하여 데이터 저장 및 관리
"""
import json
import os
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..models.project import Project
from ..models.action import Action
from ..models.settings import Settings, DefaultSettings


class DataManager:
    """JSON 데이터 관리자"""
    
    def __init__(self, data_dir: str = "data"):
        """
        초기화
        
        Args:
            data_dir: 데이터 디렉토리 경로
        """
        self.data_dir = Path(data_dir)
        self.projects_file = self.data_dir / "projects.json"
        self.settings_file = self.data_dir / "settings.json"
        self.templates_file = self.data_dir / "templates.json"
        self.backup_dir = self.data_dir / "backups"
        
        # 데이터 디렉토리 생성
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """데이터 디렉토리 및 파일 생성"""
        self.data_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        # 기본 파일들이 없으면 생성
        if not self.projects_file.exists():
            self._create_default_projects_file()
        
        if not self.settings_file.exists():
            self._create_default_settings_file()
        
        if not self.templates_file.exists():
            self._create_default_templates_file()
    
    def _create_default_projects_file(self):
        """기본 프로젝트 파일 생성"""
        default_data = {
            "projects": [],
            "next_project_id": 1,
            "next_action_id": 1,
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        self._save_json(self.projects_file, default_data)
    
    def _create_default_settings_file(self):
        """기본 설정 파일 생성"""
        default_settings = DefaultSettings.get_default_settings()
        self._save_json(self.settings_file, default_settings.to_dict())
    
    def _create_default_templates_file(self):
        """기본 템플릿 파일 생성"""
        default_data = {
            "templates": [],
            "categories": [
                "웹 자동화",
                "데이터 입력",
                "파일 관리",
                "기타"
            ],
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        self._save_json(self.templates_file, default_data)
    
    def _load_json(self, file_path: Path) -> Dict:
        """JSON 파일 로드 (보안 검증 포함)"""
        try:
            if file_path.exists():
                # 파일 크기 검증 (10MB 제한)
                file_size = file_path.stat().st_size
                if file_size > 10 * 1024 * 1024:  # 10MB
                    raise ValueError(f"파일이 너무 큽니다: {file_size} bytes")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 데이터 구조 검증
                if not isinstance(data, dict):
                    raise ValueError("잘못된 JSON 구조입니다.")
                    
                return data
            return {}
        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            print(f"JSON 파일 로드 오류 ({file_path}): {e}")
            return {}
    
    def _save_json(self, file_path: Path, data: Dict):
        """JSON 파일 저장"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"JSON 파일 저장 오류 ({file_path}): {e}")
    
    # 프로젝트 관리
    def get_all_projects(self) -> List[Project]:
        """모든 프로젝트 반환"""
        data = self._load_json(self.projects_file)
        projects_data = data.get("projects", [])
        return [Project.from_dict(p) for p in projects_data]
    
    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """ID로 프로젝트 조회"""
        projects = self.get_all_projects()
        for project in projects:
            if project.id == project_id:
                return project
        return None
    
    def save_project(self, project: Project):
        """프로젝트 저장"""
        data = self._load_json(self.projects_file)
        projects_data = data.get("projects", [])
        
        # 기존 프로젝트 찾기
        existing_index = -1
        for i, p in enumerate(projects_data):
            if p.get("id") == project.id:
                existing_index = i
                break
        
        project_dict = project.to_dict()
        if existing_index >= 0:
            # 기존 프로젝트 업데이트
            projects_data[existing_index] = project_dict
        else:
            # 새 프로젝트 추가
            projects_data.append(project_dict)
            # ID 자동 증가
            data["next_project_id"] = max(p.get("id", 0) for p in projects_data) + 1
        
        data["projects"] = projects_data
        data["updated_at"] = datetime.now().isoformat()
        
        self._save_json(self.projects_file, data)
    
    def delete_project(self, project_id: int) -> bool:
        """프로젝트 삭제"""
        data = self._load_json(self.projects_file)
        projects_data = data.get("projects", [])
        
        # 프로젝트 찾기 및 삭제
        for i, p in enumerate(projects_data):
            if p.get("id") == project_id:
                del projects_data[i]
                data["projects"] = projects_data
                data["updated_at"] = datetime.now().isoformat()
                self._save_json(self.projects_file, data)
                return True
        
        return False
    
    def get_next_project_id(self) -> int:
        """다음 프로젝트 ID 반환"""
        data = self._load_json(self.projects_file)
        return data.get("next_project_id", 1)
    
    def get_next_action_id(self) -> int:
        """다음 액션 ID 반환"""
        data = self._load_json(self.projects_file)
        return data.get("next_action_id", 1)
    
    def get_next_action_order(self, project_id: int) -> int:
        """프로젝트의 다음 액션 순서 반환"""
        project = self.get_project_by_id(project_id)
        if not project:
            return 1
        
        # 현재 프로젝트의 액션들 중 가장 큰 order_index + 1 반환
        max_order = 0
        for action in project.actions:
            order_index = action.get('order_index', 0)
            if order_index > max_order:
                max_order = order_index
        
        return max_order + 1
    
    def save_action(self, project_id: int, action: Dict):
        """액션 저장 (프로젝트에 추가)"""
        project = self.get_project_by_id(project_id)
        if not project:
            raise ValueError(f"프로젝트 ID {project_id}를 찾을 수 없습니다.")
        
        # 액션을 프로젝트에 추가
        project.add_action(action)
        
        # 프로젝트 저장
        self.save_project(project)
        
        # next_action_id 증가
        data = self._load_json(self.projects_file)
        data["next_action_id"] = data.get("next_action_id", 1) + 1
        self._save_json(self.projects_file, data)
    
    # 설정 관리
    def get_settings(self) -> Settings:
        """설정 반환"""
        data = self._load_json(self.settings_file)
        return Settings.from_dict(data)
    
    def save_settings(self, settings: Settings):
        """설정 저장"""
        self._save_json(self.settings_file, settings.to_dict())
    
    def reset_settings(self):
        """설정 초기화"""
        default_settings = DefaultSettings.get_default_settings()
        self.save_settings(default_settings)
    
    # 템플릿 관리
    def get_templates(self) -> List[Dict]:
        """모든 템플릿 반환"""
        data = self._load_json(self.templates_file)
        return data.get("templates", [])
    
    def get_categories(self) -> List[str]:
        """카테고리 목록 반환"""
        data = self._load_json(self.templates_file)
        return data.get("categories", [])
    
    def save_template(self, template: Dict):
        """템플릿 저장"""
        data = self._load_json(self.templates_file)
        templates = data.get("templates", [])
        
        # 기존 템플릿 찾기
        existing_index = -1
        for i, t in enumerate(templates):
            if t.get("id") == template.get("id"):
                existing_index = i
                break
        
        if existing_index >= 0:
            templates[existing_index] = template
        else:
            templates.append(template)
        
        data["templates"] = templates
        data["updated_at"] = datetime.now().isoformat()
        
        self._save_json(self.templates_file, data)
    
    # 백업 및 복원
    def create_backup(self) -> str:
        """데이터 백업 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        backup_path.mkdir(exist_ok=True)
        
        # 모든 JSON 파일 복사
        for json_file in self.data_dir.glob("*.json"):
            shutil.copy2(json_file, backup_path / json_file.name)
        
        return str(backup_path)
    
    def restore_backup(self, backup_path: str) -> bool:
        """백업에서 복원"""
        try:
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                return False
            
            # 백업 파일들을 데이터 디렉토리로 복사
            for json_file in backup_dir.glob("*.json"):
                shutil.copy2(json_file, self.data_dir / json_file.name)
            
            return True
        except Exception as e:
            print(f"백업 복원 오류: {e}")
            return False
    
    def get_backup_list(self) -> List[str]:
        """백업 목록 반환"""
        backups = []
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir() and backup_dir.name.startswith("backup_"):
                backups.append(str(backup_dir))
        return sorted(backups, reverse=True)
    
    # 유틸리티 메서드
    def export_project(self, project_id: int, export_path: str) -> bool:
        """프로젝트 내보내기"""
        project = self.get_project_by_id(project_id)
        if not project:
            return False
        
        try:
            export_data = {
                "project": project.to_dict(),
                "exported_at": datetime.now().isoformat(),
                "version": "1.0.0"
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"프로젝트 내보내기 오류: {e}")
            return False
    
    def import_project(self, import_path: str) -> Optional[Project]:
        """프로젝트 가져오기"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            project_data = import_data.get("project")
            if not project_data:
                return None
            
            # ID 재할당
            project_data["id"] = self.get_next_project_id()
            
            project = Project.from_dict(project_data)
            self.save_project(project)
            
            return project
        except Exception as e:
            print(f"프로젝트 가져오기 오류: {e}")
            return None
    
    def get_data_info(self) -> Dict[str, Any]:
        """데이터 정보 반환"""
        projects = self.get_all_projects()
        settings = self.get_settings()
        templates = self.get_templates()
        
        return {
            "total_projects": len(projects),
            "total_actions": sum(p.get_action_count() for p in projects),
            "favorite_projects": len([p for p in projects if p.favorite]),
            "settings": settings.to_dict(),
            "templates_count": len(templates),
            "data_directory": str(self.data_dir),
            "last_updated": datetime.now().isoformat()
        } 