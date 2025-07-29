"""
프로젝트 관리 로직
프로젝트 CRUD 기능 및 검색/필터링 기능
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.project import Project
from ..utils.data_manager import DataManager


class ProjectManager:
    """프로젝트 관리자 클래스"""
    
    def __init__(self):
        """초기화"""
        self.data_manager = DataManager()
    
    # 프로젝트 CRUD 기능
    def create_project(self, name: str, description: str = "", category: str = "기타", favorite: bool = False) -> Project:
        """
        새 프로젝트 생성
        
        Args:
            name: 프로젝트명
            description: 프로젝트 설명
            category: 카테고리
            favorite: 즐겨찾기 여부
        
        Returns:
            생성된 프로젝트
        """
        project_id = self.data_manager.get_next_project_id()
        project = Project(
            id=project_id,
            name=name,
            description=description,
            category=category,
            favorite=favorite
        )
        
        self.data_manager.save_project(project)
        return project
    
    def get_all_projects(self) -> List[Project]:
        """모든 프로젝트 반환"""
        return self.data_manager.get_all_projects()
    
    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """ID로 프로젝트 조회"""
        return self.data_manager.get_project_by_id(project_id)
    
    def update_project(self, project: Project) -> bool:
        """
        프로젝트 업데이트
        
        Args:
            project: 업데이트할 프로젝트
        
        Returns:
            성공 여부
        """
        try:
            project.update_timestamp()
            self.data_manager.save_project(project)
            return True
        except Exception:
            return False
    
    def delete_project(self, project_id: int) -> bool:
        """
        프로젝트 삭제
        
        Args:
            project_id: 삭제할 프로젝트 ID
        
        Returns:
            성공 여부
        """
        return self.data_manager.delete_project(project_id)
    
    # 검색 및 필터링 기능
    def search_projects(self, keyword: str) -> List[Project]:
        """
        프로젝트 검색
        
        Args:
            keyword: 검색 키워드
        
        Returns:
            검색 결과 프로젝트 목록
        """
        if not keyword.strip():
            return self.get_all_projects()
        
        keyword = keyword.lower().strip()
        all_projects = self.get_all_projects()
        
        results = []
        for project in all_projects:
            if (keyword in project.name.lower() or 
                keyword in project.description.lower() or
                keyword in project.category.lower()):
                results.append(project)
        
        return results
    
    def filter_projects_by_category(self, category: str) -> List[Project]:
        """
        카테고리별 프로젝트 필터링
        
        Args:
            category: 카테고리
        
        Returns:
            필터링된 프로젝트 목록
        """
        if not category or category == "전체":
            return self.get_all_projects()
        
        all_projects = self.get_all_projects()
        return [p for p in all_projects if p.category == category]
    
    def get_favorite_projects(self) -> List[Project]:
        """즐겨찾기 프로젝트 반환"""
        all_projects = self.get_all_projects()
        return [p for p in all_projects if p.favorite]
    
    def get_projects_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Project]:
        """
        날짜 범위별 프로젝트 필터링
        
        Args:
            start_date: 시작 날짜
            end_date: 종료 날짜
        
        Returns:
            필터링된 프로젝트 목록
        """
        all_projects = self.get_all_projects()
        results = []
        
        for project in all_projects:
            created_date = datetime.fromisoformat(project.created_at)
            if start_date <= created_date <= end_date:
                results.append(project)
        
        return results
    
    # 프로젝트 통계
    def get_project_statistics(self) -> Dict[str, Any]:
        """프로젝트 통계 반환"""
        all_projects = self.get_all_projects()
        
        total_projects = len(all_projects)
        favorite_projects = len([p for p in all_projects if p.favorite])
        total_actions = sum(p.get_action_count() for p in all_projects)
        
        # 카테고리별 통계
        category_stats = {}
        for project in all_projects:
            category = project.category
            if category not in category_stats:
                category_stats[category] = 0
            category_stats[category] += 1
        
        # 최근 프로젝트 (최근 7일)
        recent_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        recent_projects = len([
            p for p in all_projects 
            if datetime.fromisoformat(p.created_at) >= recent_date
        ])
        
        return {
            "total_projects": total_projects,
            "favorite_projects": favorite_projects,
            "total_actions": total_actions,
            "category_stats": category_stats,
            "recent_projects": recent_projects,
            "empty_projects": len([p for p in all_projects if p.is_empty()])
        }
    
    # 프로젝트 정렬
    def sort_projects(self, projects: List[Project], sort_by: str = "name", reverse: bool = False) -> List[Project]:
        """
        프로젝트 정렬
        
        Args:
            projects: 정렬할 프로젝트 목록
            sort_by: 정렬 기준 ("name", "created_at", "updated_at", "category", "actions")
            reverse: 역순 정렬 여부
        
        Returns:
            정렬된 프로젝트 목록
        """
        if sort_by == "name":
            return sorted(projects, key=lambda p: p.name.lower(), reverse=reverse)
        elif sort_by == "created_at":
            return sorted(projects, key=lambda p: p.created_at, reverse=reverse)
        elif sort_by == "updated_at":
            return sorted(projects, key=lambda p: p.updated_at, reverse=reverse)
        elif sort_by == "category":
            return sorted(projects, key=lambda p: p.category.lower(), reverse=reverse)
        elif sort_by == "actions":
            return sorted(projects, key=lambda p: p.get_action_count(), reverse=reverse)
        else:
            return projects
    
    # 프로젝트 검증
    def validate_project(self, project: Project) -> Dict[str, str]:
        """
        프로젝트 유효성 검사
        
        Args:
            project: 검사할 프로젝트
        
        Returns:
            오류 메시지 딕셔너리 (빈 딕셔너리면 유효함)
        """
        errors = {}
        
        if not project.name or not project.name.strip():
            errors["name"] = "프로젝트명은 필수입니다."
        elif len(project.name.strip()) > 100:
            errors["name"] = "프로젝트명은 100자 이하여야 합니다."
        
        if len(project.description) > 1000:
            errors["description"] = "설명은 1000자 이하여야 합니다."
        
        if not project.category or not project.category.strip():
            errors["category"] = "카테고리는 필수입니다."
        
        return errors
    
    # 프로젝트 복사
    def duplicate_project(self, project_id: int, new_name: str = None) -> Optional[Project]:
        """
        프로젝트 복사
        
        Args:
            project_id: 복사할 프로젝트 ID
            new_name: 새 프로젝트명 (None이면 원본명 + " (복사)")
        
        Returns:
            복사된 프로젝트
        """
        original_project = self.get_project_by_id(project_id)
        if not original_project:
            return None
        
        if new_name is None:
            new_name = f"{original_project.name} (복사)"
        
        # 새 프로젝트 생성
        new_project = self.create_project(
            name=new_name,
            description=original_project.description,
            category=original_project.category,
            favorite=False  # 복사본은 즐겨찾기 해제
        )
        
        # 액션 복사
        for action in original_project.actions:
            new_action = action.copy()
            new_action["id"] = self.data_manager.get_next_action_id()
            new_project.add_action(new_action)
        
        self.data_manager.save_project(new_project)
        return new_project
    
    # 프로젝트 내보내기/가져오기
    def export_project(self, project_id: int, export_path: str) -> bool:
        """프로젝트 내보내기"""
        return self.data_manager.export_project(project_id, export_path)
    
    def import_project(self, import_path: str) -> Optional[Project]:
        """프로젝트 가져오기"""
        return self.data_manager.import_project(import_path)
    
    # 카테고리 관리
    def get_all_categories(self) -> List[str]:
        """모든 카테고리 반환"""
        return self.data_manager.get_categories()
    
    def add_category(self, category: str) -> bool:
        """
        새 카테고리 추가
        
        Args:
            category: 추가할 카테고리명
        
        Returns:
            성공 여부
        """
        try:
            categories = self.get_all_categories()
            if category not in categories:
                categories.append(category)
                # 카테고리 목록 업데이트 (templates.json에 저장)
                templates_data = self.data_manager._load_json(self.data_manager.templates_file)
                templates_data["categories"] = categories
                self.data_manager._save_json(self.data_manager.templates_file, templates_data)
            return True
        except Exception:
            return False 