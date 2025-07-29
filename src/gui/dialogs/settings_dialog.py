"""
설정 다이얼로그
사용자 설정 및 테마 관리를 위한 다이얼로그 창
"""
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from typing import Optional, Dict, Any

from ...models.settings import Settings, DefaultSettings
from ...utils.config import config
from ...utils.data_manager import DataManager


class SettingsDialog:
    """설정 다이얼로그 클래스"""
    
    def __init__(self, parent):
        """
        초기화
        
        Args:
            parent: 부모 윈도우
        """
        self.parent = parent
        self.data_manager = DataManager()
        self.current_settings = self.data_manager.get_settings()
        self.result = None
        
        # 다이얼로그 생성
        self.dialog = tk.Toplevel(parent)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._setup_dialog()
        self._create_widgets()
        self._load_settings()
        self._bind_events()
        
        # 다이얼로그를 화면 중앙에 배치
        self._center_dialog()
    
    def _setup_dialog(self):
        """다이얼로그 기본 설정"""
        self.dialog.title("설정")
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        
        # 모달 다이얼로그로 설정
        self.dialog.focus_set()
        self.dialog.wait_window()
    
    def _create_widgets(self):
        """위젯 생성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 노트북 (탭) 생성
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 일반 설정 탭
        self._create_general_tab()
        
        # 실행 설정 탭
        self._create_execution_tab()
        
        # 테마 설정 탭
        self._create_theme_tab()
        
        # 고급 설정 탭
        self._create_advanced_tab()
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 저장 버튼
        self.save_button = ttk.Button(
            button_frame,
            text="저장",
            command=self._save_settings,
            style="Accent.TButton"
        )
        self.save_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # 취소 버튼
        self.cancel_button = ttk.Button(
            button_frame,
            text="취소",
            command=self._cancel
        )
        self.cancel_button.pack(side=tk.RIGHT)
        
        # 기본값 복원 버튼
        self.reset_button = ttk.Button(
            button_frame,
            text="기본값 복원",
            command=self._reset_to_defaults
        )
        self.reset_button.pack(side=tk.LEFT)
    
    def _create_general_tab(self):
        """일반 설정 탭 생성"""
        general_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(general_frame, text="일반")
        
        # 언어 설정
        ttk.Label(general_frame, text="언어:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.language_var = tk.StringVar()
        self.language_combo = ttk.Combobox(
            general_frame,
            textvariable=self.language_var,
            values=["한국어", "English"],
            state="readonly",
            width=15
        )
        self.language_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 자동 저장 설정
        self.auto_save_var = tk.BooleanVar()
        self.auto_save_check = ttk.Checkbutton(
            general_frame,
            text="자동 저장 사용",
            variable=self.auto_save_var
        )
        self.auto_save_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 자동 저장 간격
        ttk.Label(general_frame, text="자동 저장 간격:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.auto_save_interval_var = tk.StringVar()
        self.auto_save_interval_combo = ttk.Combobox(
            general_frame,
            textvariable=self.auto_save_interval_var,
            values=["30초", "1분", "5분", "10분"],
            state="readonly",
            width=15
        )
        self.auto_save_interval_combo.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 로그 설정
        self.logging_var = tk.BooleanVar()
        self.logging_check = ttk.Checkbutton(
            general_frame,
            text="실행 로그 기록",
            variable=self.logging_var
        )
        self.logging_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 로그 레벨
        ttk.Label(general_frame, text="로그 레벨:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.log_level_var = tk.StringVar()
        self.log_level_combo = ttk.Combobox(
            general_frame,
            textvariable=self.log_level_var,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            state="readonly",
            width=15
        )
        self.log_level_combo.grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=5)
    
    def _create_execution_tab(self):
        """실행 설정 탭 생성"""
        execution_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(execution_frame, text="실행")
        
        # 실행 속도
        ttk.Label(execution_frame, text="기본 실행 속도:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.execution_speed_var = tk.StringVar()
        self.execution_speed_combo = ttk.Combobox(
            execution_frame,
            textvariable=self.execution_speed_var,
            values=["빠름", "보통", "느림"],
            state="readonly",
            width=15
        )
        self.execution_speed_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 기본 지연 시간
        ttk.Label(execution_frame, text="기본 지연 시간:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.default_delay_var = tk.StringVar()
        self.default_delay_combo = ttk.Combobox(
            execution_frame,
            textvariable=self.default_delay_var,
            values=["0.1초", "0.5초", "1.0초", "2.0초"],
            state="readonly",
            width=15
        )
        self.default_delay_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 안전 장치
        self.safety_failsafe_var = tk.BooleanVar()
        self.safety_failsafe_check = ttk.Checkbutton(
            execution_frame,
            text="안전 장치 사용 (ESC 키로 중단)",
            variable=self.safety_failsafe_var
        )
        self.safety_failsafe_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 실행 전 확인
        self.execution_confirm_var = tk.BooleanVar()
        self.execution_confirm_check = ttk.Checkbutton(
            execution_frame,
            text="실행 전 확인 다이얼로그 표시",
            variable=self.execution_confirm_var
        )
        self.execution_confirm_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 실행 완료 알림
        self.execution_notify_var = tk.BooleanVar()
        self.execution_notify_check = ttk.Checkbutton(
            execution_frame,
            text="실행 완료 시 알림 표시",
            variable=self.execution_notify_var
        )
        self.execution_notify_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
    
    def _create_theme_tab(self):
        """테마 설정 탭 생성"""
        theme_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(theme_frame, text="테마")
        
        # 테마 선택
        ttk.Label(theme_frame, text="테마:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.theme_var = tk.StringVar()
        self.theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=["라이트", "다크", "시스템"],
            state="readonly",
            width=15
        )
        self.theme_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 색상 설정
        ttk.Label(theme_frame, text="주요 색상:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.primary_color_var = tk.StringVar()
        self.primary_color_button = ttk.Button(
            theme_frame,
            text="색상 선택",
            command=self._choose_primary_color
        )
        self.primary_color_button.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 폰트 크기
        ttk.Label(theme_frame, text="폰트 크기:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.font_size_var = tk.StringVar()
        self.font_size_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.font_size_var,
            values=["작게", "보통", "크게"],
            state="readonly",
            width=15
        )
        self.font_size_combo.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 윈도우 크기
        ttk.Label(theme_frame, text="기본 윈도우 크기:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.window_size_var = tk.StringVar()
        self.window_size_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.window_size_var,
            values=["800x600", "1024x768", "1280x720", "1920x1080"],
            state="readonly",
            width=15
        )
        self.window_size_combo.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
    
    def _create_advanced_tab(self):
        """고급 설정 탭 생성"""
        advanced_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(advanced_frame, text="고급")
        
        # 백업 설정
        self.auto_backup_var = tk.BooleanVar()
        self.auto_backup_check = ttk.Checkbutton(
            advanced_frame,
            text="자동 백업 사용",
            variable=self.auto_backup_var
        )
        self.auto_backup_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 백업 간격
        ttk.Label(advanced_frame, text="백업 간격:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.backup_interval_var = tk.StringVar()
        self.backup_interval_combo = ttk.Combobox(
            advanced_frame,
            textvariable=self.backup_interval_var,
            values=["1일", "3일", "7일", "30일"],
            state="readonly",
            width=15
        )
        self.backup_interval_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 백업 보관 기간
        ttk.Label(advanced_frame, text="백업 보관 기간:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.backup_retention_var = tk.StringVar()
        self.backup_retention_combo = ttk.Combobox(
            advanced_frame,
            textvariable=self.backup_retention_var,
            values=["7일", "30일", "90일", "무제한"],
            state="readonly",
            width=15
        )
        self.backup_retention_combo.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 개발자 모드
        self.developer_mode_var = tk.BooleanVar()
        self.developer_mode_check = ttk.Checkbutton(
            advanced_frame,
            text="개발자 모드 (디버그 정보 표시)",
            variable=self.developer_mode_var
        )
        self.developer_mode_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 실험적 기능
        self.experimental_features_var = tk.BooleanVar()
        self.experimental_features_check = ttk.Checkbutton(
            advanced_frame,
            text="실험적 기능 사용",
            variable=self.experimental_features_var
        )
        self.experimental_features_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
    
    def _choose_primary_color(self):
        """주요 색상 선택"""
        color = colorchooser.askcolor(title="주요 색상 선택")
        if color[1]:
            self.primary_color_var.set(color[1])
    
    def _load_settings(self):
        """설정 로드"""
        # 일반 설정
        self.language_var.set(self.current_settings.language)
        self.auto_save_var.set(self.current_settings.auto_save)
        self.auto_save_interval_var.set(self._get_interval_display(self.current_settings.auto_save_interval))
        self.logging_var.set(self.current_settings.logging)
        self.log_level_var.set(self.current_settings.log_level)
        
        # 실행 설정
        self.execution_speed_var.set(self._get_speed_display(self.current_settings.execution_speed))
        self.default_delay_var.set(f"{self.current_settings.default_delay}초")
        self.safety_failsafe_var.set(self.current_settings.safety_failsafe)
        self.execution_confirm_var.set(self.current_settings.execution_confirm)
        self.execution_notify_var.set(self.current_settings.execution_notify)
        
        # 테마 설정
        self.theme_var.set(self._get_theme_display(self.current_settings.theme))
        self.primary_color_var.set(self.current_settings.primary_color)
        self.font_size_var.set(self._get_font_size_display(self.current_settings.font_size))
        self.window_size_var.set(self.current_settings.window_size)
        
        # 고급 설정
        self.auto_backup_var.set(self.current_settings.auto_backup)
        self.backup_interval_var.set(self._get_interval_display(self.current_settings.backup_interval))
        self.backup_retention_var.set(self._get_retention_display(self.current_settings.backup_retention))
        self.developer_mode_var.set(self.current_settings.developer_mode)
        self.experimental_features_var.set(self.current_settings.experimental_features)
    
    def _get_interval_display(self, seconds: int) -> str:
        """초를 표시 형식으로 변환"""
        if seconds < 60:
            return f"{seconds}초"
        elif seconds < 3600:
            return f"{seconds // 60}분"
        elif seconds < 86400:
            return f"{seconds // 3600}시간"
        else:
            return f"{seconds // 86400}일"
    
    def _get_speed_display(self, speed: str) -> str:
        """속도를 표시 형식으로 변환"""
        speed_map = {"fast": "빠름", "normal": "보통", "slow": "느림"}
        return speed_map.get(speed, "보통")
    
    def _get_theme_display(self, theme: str) -> str:
        """테마를 표시 형식으로 변환"""
        theme_map = {"light": "라이트", "dark": "다크", "system": "시스템"}
        return theme_map.get(theme, "라이트")
    
    def _get_font_size_display(self, size: str) -> str:
        """폰트 크기를 표시 형식으로 변환"""
        size_map = {"small": "작게", "normal": "보통", "large": "크게"}
        return size_map.get(size, "보통")
    
    def _get_retention_display(self, days: int) -> str:
        """보관 기간을 표시 형식으로 변환"""
        if days == -1:
            return "무제한"
        elif days < 30:
            return f"{days}일"
        else:
            return f"{days // 30}개월"
    
    def _bind_events(self):
        """이벤트 바인딩"""
        # Enter 키로 저장
        self.dialog.bind('<Return>', lambda e: self._save_settings())
        
        # Escape 키로 취소
        self.dialog.bind('<Escape>', lambda e: self._cancel())
    
    def _center_dialog(self):
        """다이얼로그를 화면 중앙에 배치"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def _save_settings(self):
        """설정 저장"""
        try:
            # 설정 값 수집
            new_settings = Settings(
                language=self._get_language_value(self.language_var.get()),
                auto_save=self.auto_save_var.get(),
                auto_save_interval=self._get_interval_value(self.auto_save_interval_var.get()),
                logging=self.logging_var.get(),
                log_level=self.log_level_var.get(),
                execution_speed=self._get_speed_value(self.execution_speed_var.get()),
                default_delay=float(self.default_delay_var.get().replace("초", "")),
                safety_failsafe=self.safety_failsafe_var.get(),
                execution_confirm=self.execution_confirm_var.get(),
                execution_notify=self.execution_notify_var.get(),
                theme=self._get_theme_value(self.theme_var.get()),
                primary_color=self.primary_color_var.get(),
                font_size=self._get_font_size_value(self.font_size_var.get()),
                window_size=self.window_size_var.get(),
                auto_backup=self.auto_backup_var.get(),
                backup_interval=self._get_interval_value(self.backup_interval_var.get()),
                backup_retention=self._get_retention_value(self.backup_retention_var.get()),
                developer_mode=self.developer_mode_var.get(),
                experimental_features=self.experimental_features_var.get()
            )
            
            # 설정 저장
            self.data_manager.save_settings(new_settings)
            
            messagebox.showinfo("성공", "설정이 저장되었습니다.")
            self.result = "saved"
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("오류", f"설정 저장 중 오류가 발생했습니다:\n{str(e)}")
    
    def _reset_to_defaults(self):
        """기본값으로 복원"""
        result = messagebox.askyesno(
            "기본값 복원",
            "모든 설정을 기본값으로 복원하시겠습니까?\n\n이 작업은 되돌릴 수 없습니다."
        )
        
        if result:
            try:
                # 기본 설정으로 복원
                default_settings = DefaultSettings.get_default_settings()
                self.data_manager.save_settings(default_settings)
                
                # UI 업데이트
                self.current_settings = default_settings
                self._load_settings()
                
                messagebox.showinfo("성공", "설정이 기본값으로 복원되었습니다.")
                
            except Exception as e:
                messagebox.showerror("오류", f"기본값 복원 중 오류가 발생했습니다:\n{str(e)}")
    
    def _cancel(self):
        """취소"""
        self.result = "cancelled"
        self.dialog.destroy()
    
    def _get_language_value(self, display: str) -> str:
        """언어 표시값을 실제값으로 변환"""
        language_map = {"한국어": "ko", "English": "en"}
        return language_map.get(display, "ko")
    
    def _get_interval_value(self, display: str) -> int:
        """간격 표시값을 실제값으로 변환"""
        if "초" in display:
            return int(display.replace("초", ""))
        elif "분" in display:
            return int(display.replace("분", "")) * 60
        elif "시간" in display:
            return int(display.replace("시간", "")) * 3600
        elif "일" in display:
            return int(display.replace("일", "")) * 86400
        return 300  # 기본값 5분
    
    def _get_speed_value(self, display: str) -> str:
        """속도 표시값을 실제값으로 변환"""
        speed_map = {"빠름": "fast", "보통": "normal", "느림": "slow"}
        return speed_map.get(display, "normal")
    
    def _get_theme_value(self, display: str) -> str:
        """테마 표시값을 실제값으로 변환"""
        theme_map = {"라이트": "light", "다크": "dark", "시스템": "system"}
        return theme_map.get(display, "light")
    
    def _get_font_size_value(self, display: str) -> str:
        """폰트 크기 표시값을 실제값으로 변환"""
        size_map = {"작게": "small", "보통": "normal", "크게": "large"}
        return size_map.get(display, "normal")
    
    def _get_retention_value(self, display: str) -> int:
        """보관 기간 표시값을 실제값으로 변환"""
        if display == "무제한":
            return -1
        elif "일" in display:
            return int(display.replace("일", ""))
        elif "개월" in display:
            return int(display.replace("개월", "")) * 30
        return 30  # 기본값 30일
    
    def get_result(self) -> Optional[str]:
        """결과 반환"""
        return self.result


def show_settings_dialog(parent) -> Optional[str]:
    """
    설정 다이얼로그 표시
    
    Args:
        parent: 부모 윈도우
    
    Returns:
        "saved", "cancelled" 또는 None
    """
    dialog = SettingsDialog(parent)
    return dialog.get_result() 