"""
설정 데이터 모델
JSON 기반 데이터 저장을 위한 설정 클래스
"""
from typing import Dict, Any
from dataclasses import dataclass, asdict
import json


@dataclass
class Settings:
    """설정 데이터 모델"""
    
    # 실행 설정
    execution_speed: str = "normal"  # "fast", "normal", "slow"
    default_delay: float = 0.5
    safety_failsafe: bool = True
    
    # UI 설정
    theme: str = "light"  # "light", "dark"
    language: str = "ko"  # "ko", "en"
    window_width: int = 1200
    window_height: int = 800
    
    # 데이터 설정
    auto_save: bool = True
    auto_backup: bool = True
    backup_interval: int = 7  # 일
    
    # 고급 설정
    enable_logging: bool = True
    log_level: str = "INFO"  # "DEBUG", "INFO", "WARNING", "ERROR"
    max_history: int = 100

    # 최근 실행 프로젝트 (최대 10개)
    recent_projects: list = None

    def __post_init__(self):
        """초기화 후 처리"""
        if self.recent_projects is None:
            self.recent_projects = []
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return asdict(self)
    
    def to_json(self) -> str:
        """JSON 문자열로 변환"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Settings':
        """딕셔너리에서 설정 생성"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Settings':
        """JSON 문자열에서 설정 생성"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def get_execution_delay(self) -> float:
        """실행 속도에 따른 지연 시간 반환"""
        speed_delays = {
            "fast": 0.1,
            "normal": 0.5,
            "slow": 1.0
        }
        return speed_delays.get(self.execution_speed, self.default_delay)
    
    def is_dark_theme(self) -> bool:
        """다크 테마인지 확인"""
        return self.theme == "dark"
    
    def is_korean(self) -> bool:
        """한국어인지 확인"""
        return self.language == "ko"
    
    def update(self, **kwargs):
        """설정 업데이트"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get_theme_colors(self) -> Dict[str, str]:
        """테마 색상 반환"""
        if self.is_dark_theme():
            return {
                "primary": "#3b82f6",
                "success": "#10b981",
                "warning": "#f59e0b",
                "error": "#ef4444",
                "background": "#1f2937",
                "surface": "#374151",
                "text": "#f9fafb",
                "text_secondary": "#d1d5db"
            }
        else:
            return {
                "primary": "#2563eb",
                "success": "#16a34a",
                "warning": "#ca8a04",
                "error": "#dc2626",
                "background": "#ffffff",
                "surface": "#f8fafc",
                "text": "#1f2937",
                "text_secondary": "#6b7280"
            }

    def add_recent_project(self, project_id: int):
        """
        최근 실행 프로젝트 추가

        Args:
            project_id: 프로젝트 ID
        """
        if self.recent_projects is None:
            self.recent_projects = []

        # 이미 목록에 있으면 제거 (최근 항목으로 올리기 위해)
        if project_id in self.recent_projects:
            self.recent_projects.remove(project_id)

        # 맨 앞에 추가
        self.recent_projects.insert(0, project_id)

        # 최대 10개만 유지
        if len(self.recent_projects) > 10:
            self.recent_projects = self.recent_projects[:10]

    def get_recent_projects(self) -> list:
        """최근 실행 프로젝트 목록 반환"""
        if self.recent_projects is None:
            self.recent_projects = []
        return self.recent_projects

    def clear_recent_projects(self):
        """최근 실행 프로젝트 목록 초기화"""
        self.recent_projects = []


class DefaultSettings:
    """기본 설정값"""
    
    @staticmethod
    def get_default_settings() -> Settings:
        """기본 설정 반환"""
        return Settings()
    
    @staticmethod
    def get_minimal_settings() -> Settings:
        """최소 설정 반환"""
        return Settings(
            execution_speed="normal",
            default_delay=0.5,
            safety_failsafe=True,
            theme="light",
            language="ko",
            auto_save=True,
            enable_logging=False
        )
    
    @staticmethod
    def get_performance_settings() -> Settings:
        """성능 최적화 설정 반환"""
        return Settings(
            execution_speed="fast",
            default_delay=0.1,
            safety_failsafe=False,
            theme="light",
            language="ko",
            auto_save=False,
            enable_logging=False,
            max_history=50
        ) 