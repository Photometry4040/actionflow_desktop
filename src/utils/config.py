"""
설정 관리 유틸리티
애플리케이션 설정 및 환경 변수 관리
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from .data_manager import DataManager
from ..models.settings import Settings, DefaultSettings
from datetime import datetime


class Config:
    """설정 관리 클래스"""
    
    def __init__(self):
        """초기화"""
        self.data_manager = DataManager()
        self._settings = None
        self._load_settings()
    
    def _load_settings(self):
        """설정 로드"""
        try:
            self._settings = self.data_manager.get_settings()
        except Exception as e:
            print(f"설정 로드 오류: {e}")
            self._settings = DefaultSettings.get_default_settings()
    
    def get_settings(self) -> Settings:
        """설정 반환"""
        return self._settings
    
    def update_settings(self, **kwargs):
        """설정 업데이트"""
        self._settings.update(**kwargs)
        self.data_manager.save_settings(self._settings)
    
    def reset_settings(self):
        """설정 초기화"""
        self._settings = DefaultSettings.get_default_settings()
        self.data_manager.save_settings(self._settings)
    
    # 애플리케이션 경로
    @staticmethod
    def get_app_root() -> Path:
        """애플리케이션 루트 경로 반환"""
        if getattr(sys, 'frozen', False):
            # PyInstaller로 빌드된 경우
            return Path(sys._MEIPASS)
        else:
            # 개발 환경
            return Path(__file__).parent.parent.parent
    
    @staticmethod
    def get_data_directory() -> Path:
        """데이터 디렉토리 경로 반환"""
        app_root = Config.get_app_root()
        return app_root / "data"
    
    @staticmethod
    def get_resources_directory() -> Path:
        """리소스 디렉토리 경로 반환"""
        app_root = Config.get_app_root()
        return app_root / "src" / "resources"
    
    @staticmethod
    def get_icons_directory() -> Path:
        """아이콘 디렉토리 경로 반환"""
        resources_dir = Config.get_resources_directory()
        return resources_dir / "icons"
    
    @staticmethod
    def get_themes_directory() -> Path:
        """테마 디렉토리 경로 반환"""
        resources_dir = Config.get_resources_directory()
        return resources_dir / "themes"
    
    @staticmethod
    def get_templates_directory() -> Path:
        """템플릿 디렉토리 경로 반환"""
        resources_dir = Config.get_resources_directory()
        return resources_dir / "templates"
    
    # 환경 설정
    @staticmethod
    def is_development() -> bool:
        """개발 환경인지 확인"""
        return not getattr(sys, 'frozen', False)
    
    @staticmethod
    def is_production() -> bool:
        """프로덕션 환경인지 확인"""
        return getattr(sys, 'frozen', False)
    
    @staticmethod
    def get_platform() -> str:
        """플랫폼 정보 반환"""
        return sys.platform
    
    @staticmethod
    def is_windows() -> bool:
        """Windows인지 확인"""
        return sys.platform.startswith('win')
    
    @staticmethod
    def is_macos() -> bool:
        """macOS인지 확인"""
        return sys.platform.startswith('darwin')
    
    @staticmethod
    def is_linux() -> bool:
        """Linux인지 확인"""
        return sys.platform.startswith('linux')
    
    # 애플리케이션 정보
    @staticmethod
    def get_app_name() -> str:
        """애플리케이션 이름 반환"""
        return "ActionFlow Desktop Automator"
    
    @staticmethod
    def get_app_version() -> str:
        """애플리케이션 버전 반환"""
        return "1.0.0"
    
    @staticmethod
    def get_app_description() -> str:
        """애플리케이션 설명 반환"""
        return "로컬 PC용 반복 업무 자동화 도구"
    
    # UI 설정
    def get_window_title(self) -> str:
        """윈도우 제목 반환"""
        return f"{self.get_app_name()} v{self.get_app_version()}"
    
    def get_window_size(self) -> tuple:
        """윈도우 크기 반환"""
        settings = self.get_settings()
        return (settings.window_width, settings.window_height)
    
    def get_theme_colors(self) -> Dict[str, str]:
        """테마 색상 반환"""
        settings = self.get_settings()
        return settings.get_theme_colors()
    
    def is_dark_theme(self) -> bool:
        """다크 테마인지 확인"""
        settings = self.get_settings()
        return settings.is_dark_theme()
    
    def is_korean(self) -> bool:
        """한국어인지 확인"""
        settings = self.get_settings()
        return settings.is_korean()
    
    # 실행 설정
    def get_execution_delay(self) -> float:
        """실행 지연 시간 반환"""
        settings = self.get_settings()
        return settings.get_execution_delay()
    
    def is_safety_failsafe_enabled(self) -> bool:
        """안전 장치 활성화 여부 반환"""
        settings = self.get_settings()
        return settings.safety_failsafe
    
    def is_auto_save_enabled(self) -> bool:
        """자동 저장 활성화 여부 반환"""
        settings = self.get_settings()
        return settings.auto_save
    
    def is_logging_enabled(self) -> bool:
        """로깅 활성화 여부 반환"""
        settings = self.get_settings()
        return settings.enable_logging
    
    def get_log_level(self) -> str:
        """로그 레벨 반환"""
        settings = self.get_settings()
        return settings.log_level
    
    # 파일 경로 설정
    def get_user_data_directory(self) -> Path:
        """사용자 데이터 디렉토리 반환"""
        if self.is_windows():
            return Path(os.environ.get('APPDATA', '')) / "ActionFlow"
        elif self.is_macos():
            return Path.home() / "Library" / "Application Support" / "ActionFlow"
        else:
            return Path.home() / ".config" / "ActionFlow"
    
    def get_log_directory(self) -> Path:
        """로그 디렉토리 반환"""
        log_dir = self.get_user_data_directory() / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
    
    def get_backup_directory(self) -> Path:
        """백업 디렉토리 반환"""
        backup_dir = self.get_user_data_directory() / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir
    
    # 로깅 설정
    def get_log_file_path(self) -> Path:
        """로그 파일 경로 반환"""
        if not self.is_logging_enabled():
            return None
        
        log_dir = self.get_log_directory()
        timestamp = datetime.now().strftime("%Y%m%d")
        return log_dir / f"actionflow_{timestamp}.log"
    
    # 성능 설정
    def get_max_history(self) -> int:
        """최대 히스토리 개수 반환"""
        settings = self.get_settings()
        return settings.max_history
    
    def get_backup_interval(self) -> int:
        """백업 간격 반환"""
        settings = self.get_settings()
        return settings.backup_interval
    
    # 검증 메서드
    def validate_settings(self) -> bool:
        """설정 유효성 검사"""
        settings = self.get_settings()
        
        # 필수 설정 검사
        if not settings.execution_speed in ["fast", "normal", "slow"]:
            return False
        
        if settings.default_delay < 0:
            return False
        
        if not settings.theme in ["light", "dark"]:
            return False
        
        if not settings.language in ["ko", "en"]:
            return False
        
        return True
    
    def fix_settings(self):
        """설정 수정 (잘못된 값들을 기본값으로 변경)"""
        settings = self.get_settings()
        
        # 실행 속도 수정
        if not settings.execution_speed in ["fast", "normal", "slow"]:
            settings.execution_speed = "normal"
        
        # 지연 시간 수정
        if settings.default_delay < 0:
            settings.default_delay = 0.5
        
        # 테마 수정
        if not settings.theme in ["light", "dark"]:
            settings.theme = "light"
        
        # 언어 수정
        if not settings.language in ["ko", "en"]:
            settings.language = "ko"
        
        # 윈도우 크기 수정
        if settings.window_width < 800:
            settings.window_width = 1200
        if settings.window_height < 600:
            settings.window_height = 800
        
        # 설정 저장
        self.data_manager.save_settings(settings)


# 전역 설정 인스턴스
config = Config() 