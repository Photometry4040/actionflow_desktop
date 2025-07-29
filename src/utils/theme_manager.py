"""
테마 관리 시스템
현대적인 UI 테마 및 색상 관리
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any
import json
import os
from datetime import datetime

from .config import config


class ThemeManager:
    """테마 관리 클래스"""
    
    def __init__(self):
        """초기화"""
        self.current_theme = "light"
        self.themes = {
            "light": {
                "name": "라이트 테마",
                "bg_primary": "#ffffff",
                "bg_secondary": "#f8f9fa",
                "bg_tertiary": "#e9ecef",
                "text_primary": "#212529",
                "text_secondary": "#6c757d",
                "accent_primary": "#0d6efd",
                "accent_secondary": "#6f42c1",
                "success": "#198754",
                "warning": "#ffc107",
                "error": "#dc3545",
                "border": "#dee2e6",
                "shadow": "#00000020"
            },
            "dark": {
                "name": "다크 테마",
                "bg_primary": "#1a1a1a",
                "bg_secondary": "#2d2d2d",
                "bg_tertiary": "#404040",
                "text_primary": "#ffffff",
                "text_secondary": "#b0b0b0",
                "accent_primary": "#0d6efd",
                "accent_secondary": "#6f42c1",
                "success": "#198754",
                "warning": "#ffc107",
                "error": "#dc3545",
                "border": "#404040",
                "shadow": "#00000040"
            },
            "blue": {
                "name": "블루 테마",
                "bg_primary": "#f8f9ff",
                "bg_secondary": "#e8f2ff",
                "bg_tertiary": "#d1e7ff",
                "text_primary": "#1a1a2e",
                "text_secondary": "#4a4a6a",
                "accent_primary": "#2563eb",
                "accent_secondary": "#3b82f6",
                "success": "#059669",
                "warning": "#d97706",
                "error": "#dc2626",
                "border": "#bfdbfe",
                "shadow": "#1e40af20"
            }
        }
        
        self._load_theme()
        self._setup_styles()
    
    def _load_theme(self):
        """테마 로드"""
        try:
            settings = config.get_settings()
            theme_name = getattr(settings, "theme", "light")
            if theme_name in self.themes:
                self.current_theme = theme_name
        except Exception as e:
            print(f"테마 로드 중 오류: {e}")
    
    def _setup_styles(self):
        """스타일 설정"""
        try:
            style = ttk.Style()
            theme = self.themes[self.current_theme]
            
            # 기본 스타일 설정
            style.configure(".",
                background=theme["bg_primary"],
                foreground=theme["text_primary"],
                fieldbackground=theme["bg_secondary"],
                troughcolor=theme["bg_tertiary"],
                selectbackground=theme["accent_primary"],
                selectforeground=theme["bg_primary"],
                borderwidth=1,
                relief="flat"
            )
            
            # 프레임 스타일
            style.configure("TFrame",
                background=theme["bg_primary"]
            )
            
            # 라벨 스타일
            style.configure("TLabel",
                background=theme["bg_primary"],
                foreground=theme["text_primary"]
            )
            
            # 버튼 스타일
            style.configure("TButton",
                background=theme["bg_secondary"],
                foreground=theme["text_primary"],
                borderwidth=1,
                relief="flat",
                padding=(10, 5)
            )
            
            style.map("TButton",
                background=[("active", theme["accent_primary"]), ("pressed", theme["accent_secondary"])],
                foreground=[("active", theme["bg_primary"]), ("pressed", theme["bg_primary"])]
            )
            
            # 강조 버튼 스타일
            style.configure("Accent.TButton",
                background=theme["accent_primary"],
                foreground=theme["bg_primary"],
                borderwidth=1,
                relief="flat",
                padding=(10, 5)
            )
            
            style.map("Accent.TButton",
                background=[("active", theme["accent_secondary"]), ("pressed", theme["accent_secondary"])]
            )
            
            # 엔트리 스타일
            style.configure("TEntry",
                background=theme["bg_secondary"],
                foreground=theme["text_primary"],
                borderwidth=1,
                relief="flat",
                padding=(5, 3)
            )
            
            # 콤보박스 스타일
            style.configure("TCombobox",
                background=theme["bg_secondary"],
                foreground=theme["text_primary"],
                borderwidth=1,
                relief="flat",
                padding=(5, 3)
            )
            
            # 트리뷰 스타일
            style.configure("Treeview",
                background=theme["bg_secondary"],
                foreground=theme["text_primary"],
                fieldbackground=theme["bg_secondary"],
                borderwidth=1,
                relief="flat"
            )
            
            style.configure("Treeview.Heading",
                background=theme["bg_tertiary"],
                foreground=theme["text_primary"],
                borderwidth=1,
                relief="flat"
            )
            
            # 노트북 스타일
            style.configure("TNotebook",
                background=theme["bg_primary"],
                borderwidth=1,
                relief="flat"
            )
            
            style.configure("TNotebook.Tab",
                background=theme["bg_secondary"],
                foreground=theme["text_primary"],
                borderwidth=1,
                relief="flat",
                padding=(10, 5)
            )
            
            style.map("TNotebook.Tab",
                background=[("selected", theme["accent_primary"]), ("active", theme["bg_tertiary"])],
                foreground=[("selected", theme["bg_primary"]), ("active", theme["text_primary"])]
            )
            
            # 라벨프레임 스타일
            style.configure("TLabelframe",
                background=theme["bg_primary"],
                foreground=theme["text_primary"],
                borderwidth=1,
                relief="flat"
            )
            
            style.configure("TLabelframe.Label",
                background=theme["bg_primary"],
                foreground=theme["text_primary"]
            )
            
            # 스크롤바 스타일
            style.configure("Vertical.TScrollbar",
                background=theme["bg_tertiary"],
                borderwidth=0,
                relief="flat",
                arrowcolor=theme["text_secondary"],
                troughcolor=theme["bg_secondary"]
            )
            
            style.map("Vertical.TScrollbar",
                background=[("active", theme["accent_primary"])]
            )
            
        except Exception as e:
            print(f"스타일 설정 중 오류: {e}")
    
    def apply_theme(self, theme_name: str):
        """
        테마 적용
        
        Args:
            theme_name: 테마 이름
        """
        if theme_name in self.themes:
            self.current_theme = theme_name
            self._setup_styles()
            
            # 설정 저장
            try:
                settings = config.get_settings()
                settings.theme = theme_name
                config.save_settings(settings)
            except Exception as e:
                print(f"테마 설정 저장 중 오류: {e}")
    
    def get_current_theme(self) -> Dict[str, Any]:
        """현재 테마 정보 반환"""
        return self.themes.get(self.current_theme, self.themes["light"])
    
    def get_theme_color(self, color_name: str) -> str:
        """테마 색상 반환"""
        theme = self.get_current_theme()
        return theme.get(color_name, "#000000")
    
    def get_available_themes(self) -> Dict[str, str]:
        """사용 가능한 테마 목록 반환"""
        return {name: theme["name"] for name, theme in self.themes.items()}
    
    def create_custom_theme(self, name: str, colors: Dict[str, str]):
        """
        커스텀 테마 생성
        
        Args:
            name: 테마 이름
            colors: 색상 딕셔너리
        """
        # 기본 색상과 병합
        base_colors = self.themes["light"].copy()
        base_colors.update(colors)
        base_colors["name"] = name
        
        self.themes[name] = base_colors
    
    def export_theme(self, theme_name: str, export_path: str) -> bool:
        """
        테마 내보내기
        
        Args:
            theme_name: 테마 이름
            export_path: 내보내기 경로
        
        Returns:
            성공 여부
        """
        try:
            if theme_name not in self.themes:
                return False
            
            theme_data = {
                "name": theme_name,
                "colors": self.themes[theme_name],
                "exported_at": str(datetime.now())
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"테마 내보내기 중 오류: {e}")
            return False
    
    def import_theme(self, import_path: str) -> bool:
        """
        테마 가져오기
        
        Args:
            import_path: 가져오기 파일 경로
        
        Returns:
            성공 여부
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            theme_name = theme_data.get("name")
            colors = theme_data.get("colors", {})
            
            if theme_name and colors:
                self.themes[theme_name] = colors
                return True
            
            return False
            
        except Exception as e:
            print(f"테마 가져오기 중 오류: {e}")
            return False


# 전역 테마 매니저 인스턴스
theme_manager = ThemeManager() 