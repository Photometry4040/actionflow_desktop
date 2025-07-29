"""
프로젝트 다이얼로그
프로젝트 생성 및 편집을 위한 다이얼로그 창
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
from datetime import datetime

from ...models.project import Project
from ...utils.data_manager import DataManager


class ProjectDialog:
    """프로젝트 다이얼로그 클래스"""
    
    def __init__(self, parent, project: Optional[Project] = None):
        """
        초기화
        
        Args:
            parent: 부모 윈도우
            project: 편집할 프로젝트 (None이면 새 프로젝트 생성)
        """
        self.parent = parent
        self.project = project
        self.data_manager = DataManager()
        self.result = None
        
        # 다이얼로그 생성
        self.dialog = tk.Toplevel(parent)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._setup_dialog()
        self._create_widgets()
        self._load_project_data()
        self._bind_events()
        
        # 다이얼로그를 화면 중앙에 배치
        self._center_dialog()
    
    def _setup_dialog(self):
        """다이얼로그 기본 설정"""
        if self.project:
            self.dialog.title("프로젝트 편집")
        else:
            self.dialog.title("새 프로젝트 생성")
        
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # 모달 다이얼로그로 설정
        self.dialog.focus_set()
    
    def _create_widgets(self):
        """위젯 생성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 프로젝트 정보 섹션
        info_frame = ttk.LabelFrame(main_frame, text="프로젝트 정보", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 프로젝트명
        ttk.Label(info_frame, text="프로젝트명 *:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(info_frame, textvariable=self.name_var, width=40)
        self.name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # 설명
        ttk.Label(info_frame, text="설명:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.desc_text = tk.Text(info_frame, height=4, width=40)
        self.desc_text.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # 카테고리
        ttk.Label(info_frame, text="카테고리:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(info_frame, textvariable=self.category_var, width=37)
        self.category_combo['values'] = self.data_manager.get_categories()
        self.category_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # 즐겨찾기
        self.favorite_var = tk.BooleanVar()
        self.favorite_check = ttk.Checkbutton(
            info_frame, 
            text="즐겨찾기에 추가", 
            variable=self.favorite_var
        )
        self.favorite_check.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 그리드 가중치 설정
        info_frame.columnconfigure(1, weight=1)
        
        # 프로젝트 통계 섹션 (편집 모드에서만 표시)
        if self.project:
            stats_frame = ttk.LabelFrame(main_frame, text="프로젝트 통계", padding="10")
            stats_frame.pack(fill=tk.X, pady=(0, 10))
            
            # 액션 수
            ttk.Label(stats_frame, text=f"액션 수: {self.project.get_action_count()}개").pack(anchor=tk.W)
            
            # 생성일
            created_date = datetime.fromisoformat(self.project.created_at).strftime("%Y-%m-%d %H:%M")
            ttk.Label(stats_frame, text=f"생성일: {created_date}").pack(anchor=tk.W)
            
            # 수정일
            updated_date = datetime.fromisoformat(self.project.updated_at).strftime("%Y-%m-%d %H:%M")
            ttk.Label(stats_frame, text=f"수정일: {updated_date}").pack(anchor=tk.W)
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 저장 버튼
        self.save_button = ttk.Button(
            button_frame, 
            text="저장", 
            command=self._save_project,
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
        
        # 삭제 버튼 (편집 모드에서만 표시)
        if self.project:
            self.delete_button = ttk.Button(
                button_frame, 
                text="삭제", 
                command=self._delete_project,
                style="Danger.TButton"
            )
            self.delete_button.pack(side=tk.LEFT)
    
    def _load_project_data(self):
        """프로젝트 데이터 로드"""
        if self.project:
            # 기존 프로젝트 데이터 로드
            self.name_var.set(self.project.name)
            self.desc_text.delete(1.0, tk.END)
            self.desc_text.insert(1.0, self.project.description)
            self.category_var.set(self.project.category)
            self.favorite_var.set(self.project.favorite)
        else:
            # 새 프로젝트 기본값 설정
            self.name_var.set("")
            self.desc_text.delete(1.0, tk.END)
            self.category_var.set("기타")
            self.favorite_var.set(False)
    
    def _bind_events(self):
        """이벤트 바인딩"""
        # Enter 키로 저장
        self.dialog.bind('<Return>', lambda e: self._save_project())
        
        # Escape 키로 취소
        self.dialog.bind('<Escape>', lambda e: self._cancel())
        
        # 프로젝트명 입력 필드에 포커스
        self.name_entry.focus_set()
    
    def _center_dialog(self):
        """다이얼로그를 화면 중앙에 배치"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def _validate_input(self) -> bool:
        """입력 검증"""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("오류", "프로젝트명을 입력해주세요.")
            self.name_entry.focus_set()
            return False
        
        if len(name) > 100:
            messagebox.showerror("오류", "프로젝트명은 100자 이하여야 합니다.")
            self.name_entry.focus_set()
            return False
        
        description = self.desc_text.get(1.0, tk.END).strip()
        if len(description) > 1000:
            messagebox.showerror("오류", "설명은 1000자 이하여야 합니다.")
            self.desc_text.focus_set()
            return False
        
        return True
    
    def _save_project(self):
        """프로젝트 저장"""
        if not self._validate_input():
            return
        
        try:
            # 프로젝트 데이터 수집
            name = self.name_var.get().strip()
            description = self.desc_text.get(1.0, tk.END).strip()
            category = self.category_var.get().strip() or "기타"
            favorite = self.favorite_var.get()
            
            if self.project:
                # 기존 프로젝트 업데이트
                self.project.name = name
                self.project.description = description
                self.project.category = category
                self.project.favorite = favorite
                self.project.update_timestamp()
                
                self.data_manager.save_project(self.project)
                messagebox.showinfo("성공", "프로젝트가 수정되었습니다.")
            else:
                # 새 프로젝트 생성
                project_id = self.data_manager.get_next_project_id()
                new_project = Project(
                    id=project_id,
                    name=name,
                    description=description,
                    category=category,
                    favorite=favorite
                )
                
                self.data_manager.save_project(new_project)
                messagebox.showinfo("성공", "새 프로젝트가 생성되었습니다.")
            
            self.result = "saved"
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("오류", f"프로젝트 저장 중 오류가 발생했습니다:\n{str(e)}")
    
    def _delete_project(self):
        """프로젝트 삭제"""
        if not self.project:
            return
        
        # 삭제 확인
        result = messagebox.askyesno(
            "프로젝트 삭제", 
            f"프로젝트 '{self.project.name}'을(를) 삭제하시겠습니까?\n\n이 작업은 되돌릴 수 없습니다."
        )
        
        if result:
            try:
                self.data_manager.delete_project(self.project.id)
                messagebox.showinfo("성공", "프로젝트가 삭제되었습니다.")
                self.result = "deleted"
                self.dialog.destroy()
            except Exception as e:
                messagebox.showerror("오류", f"프로젝트 삭제 중 오류가 발생했습니다:\n{str(e)}")
    
    def _cancel(self):
        """취소"""
        self.result = "cancelled"
        self.dialog.destroy()
    
    def get_result(self) -> Optional[str]:
        """결과 반환"""
        return self.result


def show_project_dialog(parent, project: Optional[Project] = None) -> Optional[str]:
    """
    프로젝트 다이얼로그 표시
    
    Args:
        parent: 부모 윈도우
        project: 편집할 프로젝트 (None이면 새 프로젝트 생성)
    
    Returns:
        "saved", "deleted", "cancelled" 또는 None
    """
    dialog = ProjectDialog(parent, project)
    dialog.dialog.wait_window()
    return dialog.get_result() 