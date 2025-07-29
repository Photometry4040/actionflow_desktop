"""
액션 다이얼로그
액션 생성 및 편집을 위한 다이얼로그 창
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
import pyautogui

from ...models.action import Action, ActionTypes, ActionFactory
from ...utils.data_manager import DataManager


class ActionDialog:
    """액션 다이얼로그 클래스"""
    
    def __init__(self, parent, action: Optional[Dict] = None, project_id: int = None):
        """
        초기화
        
        Args:
            parent: 부모 윈도우
            action: 편집할 액션 (None이면 새 액션 생성)
            project_id: 프로젝트 ID (새 액션 생성 시 필요)
        """
        self.parent = parent
        self.action = action
        self.project_id = project_id
        self.data_manager = DataManager()
        self.result = None
        
        # 다이얼로그 생성
        self.dialog = tk.Toplevel(parent)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._setup_dialog()
        self._create_widgets()
        self._load_action_data()
        self._bind_events()
        
        # 다이얼로그를 화면 중앙에 배치
        self._center_dialog()
    
    def _setup_dialog(self):
        """다이얼로그 기본 설정"""
        if self.action:
            self.dialog.title("액션 편집")
        else:
            self.dialog.title("새 액션 추가")
        
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        
        # 모달 다이얼로그로 설정
        self.dialog.focus_set()
    
    def _create_widgets(self):
        """위젯 생성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 액션 정보 섹션
        info_frame = ttk.LabelFrame(main_frame, text="액션 정보", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 액션 타입
        ttk.Label(info_frame, text="액션 타입 *:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.action_type_var = tk.StringVar()
        self.action_type_combo = ttk.Combobox(
            info_frame, 
            textvariable=self.action_type_var, 
            width=30,
            state="readonly"
        )
        self.action_type_combo['values'] = [
            "마우스 이동",
            "마우스 클릭", 
            "키보드 입력",
            "지연 시간",
            "복사",
            "붙여넣기",
            "키 조합"
        ]
        self.action_type_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # 설명
        ttk.Label(info_frame, text="설명:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.desc_var = tk.StringVar()
        self.desc_entry = ttk.Entry(info_frame, textvariable=self.desc_var, width=40)
        self.desc_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # 그리드 가중치 설정
        info_frame.columnconfigure(1, weight=1)
        
        # 파라미터 섹션
        self.param_frame = ttk.LabelFrame(main_frame, text="파라미터", padding="10")
        self.param_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 파라미터 위젯들을 동적으로 생성
        self.param_widgets = {}
        self._create_parameter_widgets()
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 좌표 추출 버튼 (마우스 액션에서만 표시)
        self.coord_button = ttk.Button(
            button_frame,
            text="좌표 추출",
            command=self._extract_coordinates
        )
        self.coord_button.pack(side=tk.LEFT)
        
        # 저장 버튼
        self.save_button = ttk.Button(
            button_frame, 
            text="저장", 
            command=self._save_action,
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
    
    def _create_parameter_widgets(self):
        """파라미터 위젯 생성"""
        # 기존 위젯들 제거
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        self.param_widgets.clear()
        
        # 액션 타입에 따른 파라미터 위젯 생성
        action_type = self.action_type_var.get()
        
        if action_type == "마우스 이동":
            self._create_mouse_move_widgets()
        elif action_type == "마우스 클릭":
            self._create_mouse_click_widgets()
        elif action_type == "키보드 입력":
            self._create_keyboard_widgets()
        elif action_type == "지연 시간":
            self._create_delay_widgets()
        elif action_type == "복사":
            self._create_clipboard_widgets()
        elif action_type == "붙여넣기":
            self._create_clipboard_widgets()
        elif action_type == "키 조합":
            self._create_key_combination_widgets()
    
    def _create_mouse_move_widgets(self):
        """마우스 이동 파라미터 위젯"""
        # X 좌표
        ttk.Label(self.param_frame, text="X 좌표:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.param_widgets['x'] = ttk.Entry(self.param_frame, width=10)
        self.param_widgets['x'].grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Y 좌표
        ttk.Label(self.param_frame, text="Y 좌표:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        self.param_widgets['y'] = ttk.Entry(self.param_frame, width=10)
        self.param_widgets['y'].grid(row=0, column=3, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 이동 방식
        ttk.Label(self.param_frame, text="이동 방식:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.param_widgets['duration'] = ttk.Entry(self.param_frame, width=10)
        self.param_widgets['duration'].insert(0, "0.5")
        self.param_widgets['duration'].grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        ttk.Label(self.param_frame, text="초").grid(row=1, column=2, sticky=tk.W, padx=(5, 0), pady=5)
    
    def _create_mouse_click_widgets(self):
        """마우스 클릭 파라미터 위젯"""
        # X 좌표
        ttk.Label(self.param_frame, text="X 좌표:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.param_widgets['x'] = ttk.Entry(self.param_frame, width=10)
        self.param_widgets['x'].grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Y 좌표
        ttk.Label(self.param_frame, text="Y 좌표:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        self.param_widgets['y'] = ttk.Entry(self.param_frame, width=10)
        self.param_widgets['y'].grid(row=0, column=3, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 클릭 버튼
        ttk.Label(self.param_frame, text="버튼:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.param_widgets['button'] = ttk.Combobox(
            self.param_frame, 
            values=["left", "right", "middle"],
            width=10,
            state="readonly"
        )
        self.param_widgets['button'].set("left")
        self.param_widgets['button'].grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 클릭 횟수
        ttk.Label(self.param_frame, text="클릭 횟수:").grid(row=1, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        self.param_widgets['clicks'] = ttk.Entry(self.param_frame, width=10)
        self.param_widgets['clicks'].insert(0, "1")
        self.param_widgets['clicks'].grid(row=1, column=3, sticky=tk.W, padx=(10, 0), pady=5)
    
    def _create_keyboard_widgets(self):
        """키보드 입력 파라미터 위젯"""
        # 입력할 텍스트
        ttk.Label(self.param_frame, text="입력할 텍스트:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.param_widgets['text'] = tk.Text(self.param_frame, height=4, width=40)
        self.param_widgets['text'].grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # 입력 속도
        ttk.Label(self.param_frame, text="입력 속도:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.param_widgets['interval'] = ttk.Entry(self.param_frame, width=10)
        self.param_widgets['interval'].insert(0, "0.1")
        self.param_widgets['interval'].grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        ttk.Label(self.param_frame, text="초").grid(row=1, column=2, sticky=tk.W, padx=(5, 0), pady=5)
    
    def _create_delay_widgets(self):
        """지연 시간 파라미터 위젯"""
        # 지연 시간
        ttk.Label(self.param_frame, text="지연 시간:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.param_widgets['seconds'] = ttk.Entry(self.param_frame, width=10)
        self.param_widgets['seconds'].insert(0, "1.0")
        self.param_widgets['seconds'].grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        ttk.Label(self.param_frame, text="초").grid(row=0, column=2, sticky=tk.W, padx=(5, 0), pady=5)
    
    def _create_clipboard_widgets(self):
        """클립보드 파라미터 위젯"""
        action_type = self.action_type_var.get()
        
        if action_type == "복사":
            # 복사할 텍스트
            ttk.Label(self.param_frame, text="복사할 텍스트:").grid(row=0, column=0, sticky=tk.W, pady=5)
            self.param_widgets['text'] = tk.Text(self.param_frame, height=4, width=40)
            self.param_widgets['text'].grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        else:  # 붙여넣기
            # 붙여넣기 방식
            ttk.Label(self.param_frame, text="붙여넣기 방식:").grid(row=0, column=0, sticky=tk.W, pady=5)
            self.param_widgets['method'] = ttk.Combobox(
                self.param_frame,
                values=["Ctrl+V", "마우스 우클릭"],
                width=15,
                state="readonly"
            )
            self.param_widgets['method'].set("Ctrl+V")
            self.param_widgets['method'].grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
    
    def _create_key_combination_widgets(self):
        """키 조합 파라미터 위젯"""
        # 키 조합
        ttk.Label(self.param_frame, text="키 조합:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.param_widgets['keys'] = ttk.Entry(self.param_frame, width=30)
        self.param_widgets['keys'].insert(0, "ctrl+c")
        self.param_widgets['keys'].grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # 예시
        ttk.Label(self.param_frame, text="예시: ctrl+c, ctrl+v, alt+tab", 
                 font=("", 9), foreground="gray").grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
    
    def _load_action_data(self):
        """액션 데이터 로드"""
        if self.action:
            # 기존 액션 데이터 로드
            action_type = self.action.get('action_type', '')
            self.action_type_var.set(self._get_action_type_display_name(action_type))
            self.desc_var.set(self.action.get('description', ''))
            
            # 파라미터 로드
            parameters = self.action.get('parameters', {})
            self._load_parameters(parameters)
        else:
            # 새 액션 기본값 설정
            self.action_type_var.set("마우스 이동")
            self.desc_var.set("")
            self._create_parameter_widgets()
    
    def _load_parameters(self, parameters: Dict):
        """파라미터 값 로드"""
        for key, value in parameters.items():
            if key in self.param_widgets:
                widget = self.param_widgets[key]
                if isinstance(widget, tk.Text):
                    widget.delete(1.0, tk.END)
                    widget.insert(1.0, str(value))
                elif isinstance(widget, ttk.Combobox):
                    widget.set(str(value))
                else:
                    widget.delete(0, tk.END)
                    widget.insert(0, str(value))
    
    def _get_action_type_display_name(self, action_type: str) -> str:
        """액션 타입을 표시명으로 변환"""
        type_map = {
            'mouse_move': '마우스 이동',
            'mouse_click': '마우스 클릭',
            'keyboard_type': '키보드 입력',
            'delay': '지연 시간',
            'clipboard_copy': '복사',
            'clipboard_paste': '붙여넣기',
            'key_combination': '키 조합'
        }
        return type_map.get(action_type, action_type)
    
    def _get_action_type_internal_name(self, display_name: str) -> str:
        """표시명을 액션 타입으로 변환"""
        type_map = {
            '마우스 이동': 'mouse_move',
            '마우스 클릭': 'mouse_click',
            '키보드 입력': 'keyboard_type',
            '지연 시간': 'delay',
            '복사': 'clipboard_copy',
            '붙여넣기': 'clipboard_paste',
            '키 조합': 'key_combination'
        }
        return type_map.get(display_name, display_name)
    
    def _bind_events(self):
        """이벤트 바인딩"""
        # 액션 타입 변경 시 파라미터 위젯 업데이트
        self.action_type_combo.bind('<<ComboboxSelected>>', lambda e: self._create_parameter_widgets())
        
        # Enter 키로 저장
        self.dialog.bind('<Return>', lambda e: self._save_action())
        
        # Escape 키로 취소
        self.dialog.bind('<Escape>', lambda e: self._cancel())
        
        # 설명 입력 필드에 포커스
        self.desc_entry.focus_set()
    
    def _center_dialog(self):
        """다이얼로그를 화면 중앙에 배치"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def _extract_coordinates(self):
        """좌표 추출"""
        action_type = self.action_type_var.get()
        if "마우스" in action_type:
            # 3초 대기 후 현재 마우스 위치 추출
            self.dialog.withdraw()  # 다이얼로그 숨기기
            
            countdown_window = tk.Toplevel(self.parent)
            countdown_window.title("좌표 추출")
            countdown_window.geometry("300x150")
            countdown_window.transient(self.parent)
            countdown_window.grab_set()
            
            # 카운트다운 레이블
            countdown_label = ttk.Label(countdown_window, text="3초 후 마우스 위치를 추출합니다...", font=("", 12))
            countdown_label.pack(pady=20)
            
            def countdown(count):
                if count > 0:
                    countdown_label.config(text=f"{count}초 후 마우스 위치를 추출합니다...")
                    countdown_window.after(1000, countdown, count - 1)
                else:
                    # 마우스 위치 추출
                    x, y = pyautogui.position()
                    
                    # 파라미터 위젯에 좌표 설정
                    if 'x' in self.param_widgets:
                        self.param_widgets['x'].delete(0, tk.END)
                        self.param_widgets['x'].insert(0, str(x))
                    if 'y' in self.param_widgets:
                        self.param_widgets['y'].delete(0, tk.END)
                        self.param_widgets['y'].insert(0, str(y))
                    
                    countdown_window.destroy()
                    self.dialog.deiconify()  # 다이얼로그 다시 표시
                    
                    messagebox.showinfo("좌표 추출", f"마우스 위치: ({x}, {y})")
            
            countdown(3)
        else:
            messagebox.showinfo("알림", "마우스 관련 액션에서만 좌표 추출이 가능합니다.")
    
    def _validate_input(self) -> bool:
        """입력 검증"""
        # 액션 타입 검증
        if not self.action_type_var.get():
            messagebox.showerror("오류", "액션 타입을 선택해주세요.")
            self.action_type_combo.focus_set()
            return False
        
        # 설명 검증
        description = self.desc_var.get().strip()
        if len(description) > 200:
            messagebox.showerror("오류", "설명은 200자 이하여야 합니다.")
            self.desc_entry.focus_set()
            return False
        
        # 파라미터 검증
        action_type = self.action_type_var.get()
        if not self._validate_parameters(action_type):
            return False
        
        return True
    
    def _validate_parameters(self, action_type: str) -> bool:
        """파라미터 검증"""
        try:
            if action_type == "마우스 이동":
                x = int(self.param_widgets['x'].get())
                y = int(self.param_widgets['y'].get())
                duration = float(self.param_widgets['duration'].get())
                if duration < 0:
                    raise ValueError("이동 시간은 0 이상이어야 합니다.")
                
            elif action_type == "마우스 클릭":
                x = int(self.param_widgets['x'].get())
                y = int(self.param_widgets['y'].get())
                clicks = int(self.param_widgets['clicks'].get())
                if clicks < 1:
                    raise ValueError("클릭 횟수는 1 이상이어야 합니다.")
                
            elif action_type == "키보드 입력":
                text = self.param_widgets['text'].get(1.0, tk.END).strip()
                if not text:
                    raise ValueError("입력할 텍스트를 입력해주세요.")
                interval = float(self.param_widgets['interval'].get())
                if interval < 0:
                    raise ValueError("입력 속도는 0 이상이어야 합니다.")
                
            elif action_type == "지연 시간":
                seconds = float(self.param_widgets['seconds'].get())
                if seconds < 0:
                    raise ValueError("지연 시간은 0 이상이어야 합니다.")
                
            elif action_type == "복사":
                text = self.param_widgets['text'].get(1.0, tk.END).strip()
                if not text:
                    raise ValueError("복사할 텍스트를 입력해주세요.")
                
            elif action_type == "키 조합":
                keys = self.param_widgets['keys'].get().strip()
                if not keys:
                    raise ValueError("키 조합을 입력해주세요.")
            
            return True
            
        except ValueError as e:
            messagebox.showerror("오류", str(e))
            return False
        except Exception as e:
            messagebox.showerror("오류", f"파라미터 검증 중 오류가 발생했습니다:\n{str(e)}")
            return False
    
    def _collect_parameters(self) -> Dict:
        """파라미터 수집"""
        action_type = self.action_type_var.get()
        parameters = {}
        
        if action_type == "마우스 이동":
            parameters['x'] = int(self.param_widgets['x'].get())
            parameters['y'] = int(self.param_widgets['y'].get())
            parameters['duration'] = float(self.param_widgets['duration'].get())
            
        elif action_type == "마우스 클릭":
            parameters['x'] = int(self.param_widgets['x'].get())
            parameters['y'] = int(self.param_widgets['y'].get())
            parameters['button'] = self.param_widgets['button'].get()
            parameters['clicks'] = int(self.param_widgets['clicks'].get())
            
        elif action_type == "키보드 입력":
            parameters['text'] = self.param_widgets['text'].get(1.0, tk.END).strip()
            parameters['interval'] = float(self.param_widgets['interval'].get())
            
        elif action_type == "지연 시간":
            parameters['seconds'] = float(self.param_widgets['seconds'].get())
            
        elif action_type == "복사":
            parameters['text'] = self.param_widgets['text'].get(1.0, tk.END).strip()
            
        elif action_type == "붙여넣기":
            parameters['method'] = self.param_widgets['method'].get()
            
        elif action_type == "키 조합":
            parameters['keys'] = self.param_widgets['keys'].get().strip()
        
        return parameters
    
    def _save_action(self):
        """액션 저장"""
        if not self._validate_input():
            return
        
        try:
            # 액션 데이터 수집
            action_type = self._get_action_type_internal_name(self.action_type_var.get())
            description = self.desc_var.get().strip()
            parameters = self._collect_parameters()
            
            if self.action:
                # 기존 액션 업데이트
                self.action['action_type'] = action_type
                self.action['description'] = description
                self.action['parameters'] = parameters
                
                messagebox.showinfo("성공", "액션이 수정되었습니다.")
            else:
                # 새 액션 생성
                action_id = self.data_manager.get_next_action_id()
                order_index = self.data_manager.get_next_action_order(self.project_id)
                
                new_action = {
                    'id': action_id,
                    'order_index': order_index,
                    'action_type': action_type,
                    'description': description,
                    'parameters': parameters
                }
                
                # 액션을 프로젝트에 저장
                self.data_manager.save_action(self.project_id, new_action)
                self.action = new_action
                messagebox.showinfo("성공", "새 액션이 추가되었습니다.")
            
            self.result = "saved"
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("오류", f"액션 저장 중 오류가 발생했습니다:\n{str(e)}")
    
    def _cancel(self):
        """취소"""
        self.result = "cancelled"
        self.dialog.destroy()
    
    def get_result(self) -> Optional[Dict]:
        """결과 반환"""
        return self.action if self.result == "saved" else None


def show_action_dialog(parent, action: Optional[Dict] = None, project_id: int = None) -> Optional[Dict]:
    """
    액션 다이얼로그 표시
    
    Args:
        parent: 부모 윈도우
        action: 편집할 액션 (None이면 새 액션 생성)
        project_id: 프로젝트 ID (새 액션 생성 시 필요)
    
    Returns:
        저장된 액션 딕셔너리 또는 None
    """
    dialog = ActionDialog(parent, action, project_id)
    dialog.dialog.wait_window()
    return dialog.get_result() 