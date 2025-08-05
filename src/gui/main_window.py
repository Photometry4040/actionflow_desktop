"""
메인 윈도우
ActionFlow Desktop Automator의 메인 GUI 창
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from typing import Optional, Dict, List
import sys

from ..utils.config import config
from ..utils.data_manager import DataManager
from ..core.project_manager import ProjectManager
from ..core.action_executor import ActionExecutor
from ..core.macro_recorder import MacroRecorder
from ..core.code_generator import CodeGenerator
from ..utils.backup_manager import BackupManager
from .dialogs.project_dialog import show_project_dialog
from .dialogs.action_dialog import show_action_dialog
from .dialogs.settings_dialog import show_settings_dialog


class MainWindow:
    """메인 윈도우 클래스"""
    
    def __init__(self):
        """초기화"""
        self.root = tk.Tk()
        self.data_manager = DataManager()
        self.project_manager = ProjectManager()
        self.action_executor = ActionExecutor()
        self.macro_recorder = MacroRecorder()
        self.code_generator = CodeGenerator()
        self.backup_manager = BackupManager()
        self.current_project = None
        
        self._setup_window()
        self._create_menu()
        self._create_toolbar()
        self._create_main_content()
        self._create_status_bar()
        self._apply_theme()
        
        # 윈도우 이벤트 바인딩
        self._bind_events()
        
        # 초기 데이터 로드
        self._refresh_project_list()
    
    def _setup_window(self):
        """윈도우 설정"""
        # 기본 설정
        self.root.title(config.get_window_title())
        width, height = config.get_window_size()
        self.root.geometry(f"{width}x{height}")
        
        # 윈도우 최소 크기 설정
        self.root.minsize(800, 600)
        
        # 윈도우 아이콘 설정 (나중에 추가)
        # self.root.iconbitmap('path/to/icon.ico')
        
        # 윈도우를 화면 중앙에 배치
        self._center_window()
    
    def _center_window(self):
        """윈도우를 화면 중앙에 배치"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_menu(self):
        """메뉴바 생성"""
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # 파일 메뉴
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="파일", menu=self.file_menu)
        self.file_menu.add_command(label="새 프로젝트", command=self._new_project, accelerator="Ctrl+N")
        self.file_menu.add_command(label="프로젝트 열기", command=self._open_project, accelerator="Ctrl+O")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="프로젝트 저장", command=self._save_project, accelerator="Ctrl+S")
        self.file_menu.add_command(label="다른 이름으로 저장", command=self._save_project_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="프로젝트 내보내기", command=self._export_project)
        self.file_menu.add_command(label="프로젝트 가져오기", command=self._import_project)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="종료", command=self._quit_app, accelerator="Ctrl+Q")
        
        # 편집 메뉴
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="편집", menu=self.edit_menu)
        self.edit_menu.add_command(label="실행 취소", command=self._undo, accelerator="Ctrl+Z")
        self.edit_menu.add_command(label="다시 실행", command=self._redo, accelerator="Ctrl+Y")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="복사", command=self._copy, accelerator="Ctrl+C")
        self.edit_menu.add_command(label="붙여넣기", command=self._paste, accelerator="Ctrl+V")
        self.edit_menu.add_command(label="삭제", command=self._delete, accelerator="Del")
        
        # 실행 메뉴
        self.run_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="실행", menu=self.run_menu)
        self.run_menu.add_command(label="프로젝트 실행", command=self._run_project, accelerator="F5")
        self.run_menu.add_command(label="선택된 액션 실행", command=self._run_selected_action, accelerator="F6")
        self.run_menu.add_separator()
        self.run_menu.add_command(label="실행 중지", command=self._stop_execution, accelerator="Esc")
        self.run_menu.add_command(label="실행 일시정지", command=self._pause_execution, accelerator="F7")
        
        # 도구 메뉴
        self.tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="도구", menu=self.tools_menu)
        self.tools_menu.add_command(label="매크로 녹화", command=self._start_recording)
        self.tools_menu.add_command(label="좌표 추출", command=self._extract_coordinates)
        self.tools_menu.add_separator()
        self.tools_menu.add_command(label="코드 생성", command=self._generate_code)
        self.tools_menu.add_command(label="템플릿 관리", command=self._manage_templates)
        
        # 설정 메뉴
        self.settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="설정", menu=self.settings_menu)
        self.settings_menu.add_command(label="일반 설정", command=self._open_settings)
        self.settings_menu.add_command(label="테마 설정", command=self._open_theme_settings)
        self.settings_menu.add_separator()
        self.settings_menu.add_command(label="데이터 백업", command=self._backup_data)
        self.settings_menu.add_command(label="데이터 복원", command=self._restore_data)
        
        # 도움말 메뉴
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="도움말", menu=self.help_menu)
        self.help_menu.add_command(label="사용자 가이드", command=self._show_user_guide)
        self.help_menu.add_command(label="단축키", command=self._show_shortcuts)
        self.help_menu.add_separator()
        self.help_menu.add_command(label="정보", command=self._show_about)
    
    def _create_toolbar(self):
        """툴바 생성"""
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        # 프로젝트 관련 버튼
        ttk.Button(self.toolbar, text="새 프로젝트", command=self._new_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="프로젝트 열기", command=self._open_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="저장", command=self._save_project).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # 실행 관련 버튼
        self.run_button = ttk.Button(self.toolbar, text="실행", command=self._run_project)
        self.run_button.pack(side=tk.LEFT, padx=2)
        
        self.stop_button = ttk.Button(self.toolbar, text="중지", command=self._stop_execution)
        self.stop_button.pack(side=tk.LEFT, padx=2)
        
        self.pause_button = ttk.Button(self.toolbar, text="일시정지", command=self._pause_execution)
        self.pause_button.pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # 도구 관련 버튼
        self.record_button = ttk.Button(self.toolbar, text="녹화 시작", command=self._start_recording)
        self.record_button.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(self.toolbar, text="좌표 추출", command=self._extract_coordinates).pack(side=tk.LEFT, padx=2)
    
    def _create_main_content(self):
        """메인 콘텐츠 영역 생성"""
        # 메인 프레임
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 왼쪽 패널 (프로젝트 목록)
        self.left_panel = ttk.Frame(self.main_frame, width=300)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        self.left_panel.pack_propagate(False)
        
        # 프로젝트 목록 제목
        ttk.Label(self.left_panel, text="프로젝트 목록", font=("Arial", 12, "bold")).pack(pady=(0, 5))
        
        # 프로젝트 목록 트리뷰
        self.project_tree = ttk.Treeview(self.left_panel, columns=("name", "actions"), show="tree headings")
        self.project_tree.heading("#0", text="프로젝트")
        self.project_tree.heading("name", text="이름")
        self.project_tree.heading("actions", text="액션 수")
        self.project_tree.column("#0", width=150)
        self.project_tree.column("name", width=100)
        self.project_tree.column("actions", width=50)
        self.project_tree.pack(fill=tk.BOTH, expand=True)
        
        # 프로젝트 목록 스크롤바
        project_scrollbar = ttk.Scrollbar(self.left_panel, orient=tk.VERTICAL, command=self.project_tree.yview)
        project_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.project_tree.configure(yscrollcommand=project_scrollbar.set)
        
        # 오른쪽 패널 (프로젝트 상세)
        self.right_panel = ttk.Frame(self.main_frame)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 프로젝트 정보 프레임
        self.project_info_frame = ttk.LabelFrame(self.right_panel, text="프로젝트 정보")
        self.project_info_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 프로젝트 정보 라벨들
        self.project_name_label = ttk.Label(self.project_info_frame, text="프로젝트명: 선택되지 않음")
        self.project_name_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.project_desc_label = ttk.Label(self.project_info_frame, text="설명: ")
        self.project_desc_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.project_actions_label = ttk.Label(self.project_info_frame, text="액션 수: 0개")
        self.project_actions_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # 액션 목록 프레임
        self.action_frame = ttk.LabelFrame(self.right_panel, text="액션 목록")
        self.action_frame.pack(fill=tk.BOTH, expand=True)
        
        # 액션 목록 트리뷰
        self.action_tree = ttk.Treeview(self.action_frame, columns=("order", "type", "description"), show="tree headings")
        self.action_tree.heading("#0", text="순서")
        self.action_tree.heading("order", text="번호")
        self.action_tree.heading("type", text="타입")
        self.action_tree.heading("description", text="설명")
        self.action_tree.column("#0", width=50)
        self.action_tree.column("order", width=50)
        self.action_tree.column("type", width=100)
        self.action_tree.column("description", width=300)
        self.action_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 액션 목록 스크롤바
        action_scrollbar = ttk.Scrollbar(self.action_frame, orient=tk.VERTICAL, command=self.action_tree.yview)
        action_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.action_tree.configure(yscrollcommand=action_scrollbar.set)
        
        # 액션 버튼 프레임
        self.action_buttons_frame = ttk.Frame(self.action_frame)
        self.action_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(self.action_buttons_frame, text="액션 추가", command=self._add_action).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.action_buttons_frame, text="액션 편집", command=self._edit_action).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.action_buttons_frame, text="액션 삭제", command=self._delete_action).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.action_buttons_frame, text="위로", command=self._move_action_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.action_buttons_frame, text="아래로", command=self._move_action_down).pack(side=tk.LEFT, padx=2)
    
    def _create_status_bar(self):
        """상태바 생성"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 상태 메시지
        self.status_label = ttk.Label(self.status_bar, text="준비")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # 진행률 바
        self.progress_bar = ttk.Progressbar(self.status_bar, mode='determinate', length=200)
        self.progress_bar.pack(side=tk.LEFT, padx=5)
        
        # 실행 상태
        self.execution_status = ttk.Label(self.status_bar, text="실행 중지됨")
        self.execution_status.pack(side=tk.RIGHT, padx=5)
        
        # 저작권 표시
        self.copyright_label = ttk.Label(self.status_bar, text="© 2025 Photometry4040", 
                                        font=('Arial', 8), foreground='gray')
        self.copyright_label.pack(side=tk.RIGHT, padx=10)
    
    def _apply_theme(self):
        """테마 적용"""
        colors = config.get_theme_colors()
        
        # 스타일 설정
        style = ttk.Style()
        style.theme_use('clam')  # 기본 테마
        
        # 색상 설정
        style.configure('TFrame', background=colors['background'])
        style.configure('TLabel', background=colors['background'], foreground=colors['text'])
        style.configure('TButton', background=colors['primary'])
        style.configure('Treeview', background=colors['surface'], foreground=colors['text'])
        style.configure('Treeview.Heading', background=colors['surface'], foreground=colors['text'])
    
    def _bind_events(self):
        """이벤트 바인딩"""
        # 윈도우 이벤트
        self.root.protocol("WM_DELETE_WINDOW", self._quit_app)
        self.root.bind('<Control-n>', lambda e: self._new_project())
        self.root.bind('<Control-o>', lambda e: self._open_project())
        self.root.bind('<Control-s>', lambda e: self._save_project())
        self.root.bind('<Control-q>', lambda e: self._quit_app())
        self.root.bind('<F5>', lambda e: self._run_project())
        self.root.bind('<Escape>', lambda e: self._stop_execution())
        
        # 트리뷰 이벤트
        self.project_tree.bind('<<TreeviewSelect>>', self._on_project_select)
        self.action_tree.bind('<<TreeviewSelect>>', self._on_action_select)
        self.action_tree.bind('<Double-1>', self._on_action_double_click)
    
    # 메뉴 이벤트 핸들러들
    def _new_project(self):
        """새 프로젝트 생성"""
        result = show_project_dialog(self.root)
        if result == "saved":
            self._refresh_project_list()
    
    def _open_project(self):
        """프로젝트 열기"""
        # 현재 선택된 프로젝트가 있으면 편집
        if self.current_project:
            result = show_project_dialog(self.root, self.current_project)
            if result == "saved":
                self._refresh_project_list()
                self._update_project_info()
            elif result == "deleted":
                self._refresh_project_list()
                self.current_project = None
                self._clear_project_info()
        else:
            messagebox.showinfo("알림", "편집할 프로젝트를 선택해주세요.")
    
    def _save_project(self):
        """프로젝트 저장"""
        if self.current_project:
            if self.project_manager.update_project(self.current_project):
                messagebox.showinfo("성공", "프로젝트가 저장되었습니다.")
                self._refresh_project_list()
            else:
                messagebox.showerror("오류", "프로젝트 저장에 실패했습니다.")
        else:
            messagebox.showinfo("알림", "저장할 프로젝트를 선택해주세요.")
    
    def _save_project_as(self):
        """다른 이름으로 저장"""
        if self.current_project:
            # 프로젝트 복사 후 새 이름으로 저장
            new_name = f"{self.current_project.name} (복사)"
            duplicated = self.project_manager.duplicate_project(self.current_project.id, new_name)
            if duplicated:
                messagebox.showinfo("성공", f"프로젝트가 '{new_name}'으로 복사되었습니다.")
                self._refresh_project_list()
            else:
                messagebox.showerror("오류", "프로젝트 복사에 실패했습니다.")
        else:
            messagebox.showinfo("알림", "복사할 프로젝트를 선택해주세요.")
    
    def _export_project(self):
        """프로젝트 내보내기"""
        if self.current_project:
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="프로젝트 내보내기"
            )
            if file_path:
                if self.project_manager.export_project(self.current_project.id, file_path):
                    messagebox.showinfo("성공", "프로젝트가 내보내기되었습니다.")
                else:
                    messagebox.showerror("오류", "프로젝트 내보내기에 실패했습니다.")
        else:
            messagebox.showinfo("알림", "내보낼 프로젝트를 선택해주세요.")
    
    def _import_project(self):
        """프로젝트 가져오기"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="프로젝트 가져오기"
        )
        if file_path:
            imported_project = self.project_manager.import_project(file_path)
            if imported_project:
                messagebox.showinfo("성공", f"프로젝트 '{imported_project.name}'이(가) 가져와졌습니다.")
                self._refresh_project_list()
            else:
                messagebox.showerror("오류", "프로젝트 가져오기에 실패했습니다.")
    
    def _quit_app(self):
        """애플리케이션 종료"""
        if messagebox.askokcancel("종료", "정말로 종료하시겠습니까?"):
            self.root.quit()
            sys.exit()
    
    def _undo(self):
        """실행 취소"""
        messagebox.showinfo("실행 취소", "실행 취소 기능은 Phase 2에서 구현됩니다.")
    
    def _redo(self):
        """다시 실행"""
        messagebox.showinfo("다시 실행", "다시 실행 기능은 Phase 2에서 구현됩니다.")
    
    def _copy(self):
        """복사"""
        messagebox.showinfo("복사", "복사 기능은 Phase 2에서 구현됩니다.")
    
    def _paste(self):
        """붙여넣기"""
        messagebox.showinfo("붙여넣기", "붙여넣기 기능은 Phase 2에서 구현됩니다.")
    
    def _delete(self):
        """삭제"""
        messagebox.showinfo("삭제", "삭제 기능은 Phase 2에서 구현됩니다.")
    
    def _run_project(self):
        """프로젝트 실행"""
        if not self.current_project:
            messagebox.showinfo("알림", "실행할 프로젝트를 선택해주세요.")
            return
        
        if not self.current_project.actions:
            messagebox.showinfo("알림", "실행할 액션이 없습니다.")
            return
        
        # 실행 확인
        result = messagebox.askyesno(
            "프로젝트 실행",
            f"프로젝트 '{self.current_project.name}'을(를) 실행하시겠습니까?\n\n"
            f"총 {len(self.current_project.actions)}개의 액션이 실행됩니다.\n"
            "ESC 키로 언제든지 중단할 수 있습니다."
        )
        
        if result:
            # 실행 시작
            success = self.action_executor.execute_project(
                project=self.current_project,
                on_progress=self._on_execution_progress,
                on_complete=self._on_execution_complete,
                on_error=self._on_execution_error
            )
            
            if success:
                # UI 업데이트
                self._update_execution_buttons()
                messagebox.showinfo("실행 시작", "프로젝트 실행이 시작되었습니다.")
            else:
                messagebox.showerror("오류", "이미 실행 중입니다.")
    
    def _run_selected_action(self):
        """선택된 액션 실행"""
        if not self.current_project:
            messagebox.showinfo("알림", "액션을 선택할 프로젝트를 선택해주세요.")
            return
        
        # 선택된 액션 확인
        selection = self.action_tree.selection()
        if not selection:
            messagebox.showinfo("알림", "실행할 액션을 선택해주세요.")
            return
        
        # 선택된 액션 찾기
        item = selection[0]
        tags = self.action_tree.item(item, "tags")
        
        for tag in tags:
            if tag.startswith("action_"):
                action_id = int(tag.split("_")[1])
                action = self.current_project.get_action_by_id(action_id)
                
                if action:
                    # 단일 액션 실행
                    success = self.action_executor.execute_single_action(action)
                    if success:
                        messagebox.showinfo("실행 완료", f"액션 '{action.get('description', '')}' 실행이 완료되었습니다.")
                    else:
                        messagebox.showerror("실행 실패", f"액션 '{action.get('description', '')}' 실행에 실패했습니다.")
                break
    
    def _stop_execution(self):
        """실행 중지"""
        if self.action_executor.is_running:
            self.action_executor.stop_execution()
            messagebox.showinfo("실행 중지", "실행이 중지되었습니다.")
            self._update_execution_buttons()
        else:
            messagebox.showinfo("알림", "실행 중인 프로젝트가 없습니다.")
    
    def _pause_execution(self):
        """실행 일시정지"""
        status = self.action_executor.get_execution_status()
        
        if status['is_running']:
            if status['is_paused']:
                # 재개
                self.action_executor.resume_execution()
                messagebox.showinfo("실행 재개", "실행이 재개되었습니다.")
            else:
                # 일시정지
                self.action_executor.pause_execution()
                messagebox.showinfo("실행 일시정지", "실행이 일시정지되었습니다.")
            
            self._update_execution_buttons()
        else:
            messagebox.showinfo("알림", "실행 중인 프로젝트가 없습니다.")
    
    def _start_recording(self):
        """매크로 녹화 시작"""
        if self.macro_recorder.is_recording:
            # 녹화 중지
            recorded_actions = self.macro_recorder.stop_recording()
            
            if recorded_actions:
                # 녹화 결과 표시
                self._show_recording_result(recorded_actions)
            else:
                messagebox.showinfo("녹화 완료", "녹화된 액션이 없습니다.")
        else:
            # 녹화 시작
            success = self.macro_recorder.start_recording(
                on_action_recorded=self._on_action_recorded,
                on_recording_stopped=self._on_recording_stopped
            )
            
            if success:
                messagebox.showinfo("녹화 시작", "매크로 녹화가 시작되었습니다.\n\n마우스 클릭과 키보드 입력이 기록됩니다.\n다시 클릭하면 녹화가 중지됩니다.")
                self._update_recording_button()
            else:
                messagebox.showerror("오류", "이미 녹화 중입니다.")
    
    def _extract_coordinates(self):
        """좌표 추출"""
        messagebox.showinfo("좌표 추출", "좌표 추출 기능은 Phase 3에서 구현됩니다.")
    
    def _generate_code(self):
        """코드 생성"""
        if not self.current_project:
            messagebox.showwarning("경고", "코드 생성을 위해 프로젝트를 선택해주세요.")
            return
        
        try:
            # 파일 저장 다이얼로그
            file_path = filedialog.asksaveasfilename(
                title="Python 스크립트 저장",
                defaultextension=".py",
                filetypes=[("Python 파일", "*.py"), ("모든 파일", "*.*")],
                initialname=f"{self.current_project.name.lower().replace(' ', '_')}.py"
            )
            
            if file_path:
                # 코드 생성
                success = self.code_generator.generate_executable_script(self.current_project, file_path)
                
                if success:
                    messagebox.showinfo("성공", f"Python 스크립트가 생성되었습니다:\n{file_path}")
                    
                    # 코드 통계 표시
                    stats = self.code_generator.get_code_statistics(self.current_project)
                    stats_message = f"""
코드 생성 통계:
- 총 액션 수: {stats['total_actions']}개
- 예상 코드 라인 수: {stats['estimated_lines']}줄
- 복잡도: {stats['complexity']}

액션 타입별 분포:
"""
                    for action_type, count in stats['action_types'].items():
                        stats_message += f"- {action_type}: {count}개\n"
                    
                    messagebox.showinfo("코드 통계", stats_message)
                else:
                    messagebox.showerror("오류", "코드 생성 중 오류가 발생했습니다.")
                    
        except Exception as e:
            messagebox.showerror("오류", f"코드 생성 중 오류가 발생했습니다:\n{str(e)}")
    
    def _manage_templates(self):
        """템플릿 관리"""
        try:
            # 템플릿 관리 다이얼로그
            template_window = tk.Toplevel(self.root)
            template_window.title("템플릿 관리")
            template_window.geometry("700x500")
            template_window.transient(self.root)
            template_window.grab_set()
            
            # 메인 프레임
            main_frame = ttk.Frame(template_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 템플릿 목록 프레임
            list_frame = ttk.LabelFrame(main_frame, text="템플릿 목록")
            list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # 템플릿 트리뷰
            template_tree = ttk.Treeview(list_frame, columns=("name", "description", "actions"), show="headings")
            template_tree.heading("name", text="템플릿 이름")
            template_tree.heading("description", text="설명")
            template_tree.heading("actions", text="액션 수")
            template_tree.column("name", width=200)
            template_tree.column("description", width=300)
            template_tree.column("actions", width=100)
            template_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 기본 템플릿들 추가
            default_templates = [
                {
                    "name": "웹 로그인 기본",
                    "description": "웹사이트 로그인 기본 템플릿",
                    "actions": [
                        {"action_type": "mouse_move", "description": "로그인 버튼으로 이동", "parameters": {"x": 500, "y": 300}},
                        {"action_type": "mouse_click", "description": "로그인 버튼 클릭", "parameters": {"x": 500, "y": 300, "button": "left", "clicks": 1}},
                        {"action_type": "delay", "description": "페이지 로딩 대기", "parameters": {"seconds": 2.0}}
                    ]
                },
                {
                    "name": "데이터 입력 기본",
                    "description": "반복적인 데이터 입력 템플릿",
                    "actions": [
                        {"action_type": "keyboard_type", "description": "데이터 입력", "parameters": {"text": "샘플 데이터", "interval": 0.1}},
                        {"action_type": "key_combination", "description": "Tab 키로 다음 필드 이동", "parameters": {"keys": "tab"}},
                        {"action_type": "delay", "description": "입력 완료 대기", "parameters": {"seconds": 0.5}}
                    ]
                },
                {
                    "name": "복사/붙여넣기",
                    "description": "클립보드 복사/붙여넣기 템플릿",
                    "actions": [
                        {"action_type": "key_combination", "description": "전체 선택", "parameters": {"keys": "ctrl+a"}},
                        {"action_type": "key_combination", "description": "복사", "parameters": {"keys": "ctrl+c"}},
                        {"action_type": "delay", "description": "복사 완료 대기", "parameters": {"seconds": 0.5}},
                        {"action_type": "key_combination", "description": "붙여넣기", "parameters": {"keys": "ctrl+v"}}
                    ]
                }
            ]
            
            # 템플릿 목록에 추가
            for template in default_templates:
                template_tree.insert("", "end", values=(
                    template["name"],
                    template["description"],
                    len(template["actions"])
                ), tags=(template,))
            
            # 버튼 프레임
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(10, 0))
            
            def apply_template():
                selection = template_tree.selection()
                if not selection:
                    messagebox.showwarning("경고", "적용할 템플릿을 선택해주세요.")
                    return
                
                if not self.current_project:
                    messagebox.showwarning("경고", "템플릿을 적용할 프로젝트를 선택해주세요.")
                    return
                
                item = selection[0]
                template = template_tree.item(item, "tags")[0]
                
                # 템플릿 액션들을 현재 프로젝트에 추가
                for action in template["actions"]:
                    action_id = self.data_manager.get_next_action_id()
                    order_index = self.data_manager.get_next_action_order(self.current_project.id)
                    
                    new_action = {
                        'id': action_id,
                        'order_index': order_index,
                        'action_type': action['action_type'],
                        'description': action['description'],
                        'parameters': action['parameters']
                    }
                    
                    self.current_project.actions.append(new_action)
                
                # 프로젝트 저장
                self.project_manager.update_project(self.current_project)
                
                # UI 새로고침
                self._refresh_action_list()
                
                messagebox.showinfo("성공", f"템플릿 '{template['name']}'이 프로젝트에 적용되었습니다.")
                template_window.destroy()
            
            def close_template():
                template_window.destroy()
            
            ttk.Button(button_frame, text="템플릿 적용", command=apply_template).pack(side=tk.RIGHT, padx=5)
            ttk.Button(button_frame, text="닫기", command=close_template).pack(side=tk.RIGHT)
            
        except Exception as e:
            messagebox.showerror("오류", f"템플릿 관리 중 오류가 발생했습니다:\n{str(e)}")
    
    def _open_settings(self):
        """설정 열기"""
        try:
            result = show_settings_dialog(self.root)
            if result == "saved":
                # 설정이 변경되었으므로 테마 재적용
                self._apply_theme()
                messagebox.showinfo("성공", "설정이 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"설정 다이얼로그 열기 중 오류가 발생했습니다:\n{str(e)}")
    
    def _open_theme_settings(self):
        """테마 설정"""
        messagebox.showinfo("테마 설정", "테마 설정 기능은 Phase 3에서 구현됩니다.")
    
    def _backup_data(self):
        """데이터 백업"""
        try:
            # 백업 이름 입력
            backup_name = simpledialog.askstring(
                "백업 생성",
                "백업 이름을 입력하세요 (빈 값이면 자동 생성):",
                parent=self.root
            )
            
            # 백업 생성
            backup_file = self.backup_manager.create_backup(backup_name, include_settings=True)
            
            if backup_file:
                messagebox.showinfo("성공", f"백업이 생성되었습니다:\n{backup_file}")
                
                # 백업 통계 표시
                stats = self.backup_manager.get_backup_statistics()
                stats_message = f"""
백업 통계:
- 총 백업 수: {stats['total_backups']}개
- 총 크기: {stats['total_size_mb']}MB
- 백업 디렉토리: {stats['backup_directory']}
"""
                messagebox.showinfo("백업 통계", stats_message)
            else:
                messagebox.showerror("오류", "백업 생성 중 오류가 발생했습니다.")
                
        except Exception as e:
            messagebox.showerror("오류", f"백업 생성 중 오류가 발생했습니다:\n{str(e)}")
    
    def _restore_data(self):
        """데이터 복원"""
        try:
            # 백업 목록 가져오기
            backups = self.backup_manager.get_backup_list()
            
            if not backups:
                messagebox.showinfo("알림", "복원할 백업이 없습니다.")
                return
            
            # 백업 선택 다이얼로그
            backup_window = tk.Toplevel(self.root)
            backup_window.title("백업 복원")
            backup_window.geometry("600x400")
            backup_window.transient(self.root)
            backup_window.grab_set()
            
            # 백업 목록 표시
            ttk.Label(backup_window, text="복원할 백업을 선택하세요:", font=("Arial", 12, "bold")).pack(pady=10)
            
            # 백업 목록 트리뷰
            backup_tree = ttk.Treeview(backup_window, columns=("name", "date", "size"), show="headings")
            backup_tree.heading("name", text="백업 이름")
            backup_tree.heading("date", text="생성일")
            backup_tree.heading("size", text="크기")
            backup_tree.column("name", width=200)
            backup_tree.column("date", width=150)
            backup_tree.column("size", width=100)
            backup_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # 백업 목록에 추가
            for backup in backups:
                backup_tree.insert("", "end", values=(
                    backup['backup_name'],
                    backup['created_at'][:19].replace('T', ' '),
                    f"{backup['file_size_mb']}MB"
                ), tags=(backup['filepath'],))
            
            # 버튼 프레임
            button_frame = ttk.Frame(backup_window)
            button_frame.pack(fill=tk.X, padx=10, pady=10)
            
            def restore_selected():
                selection = backup_tree.selection()
                if not selection:
                    messagebox.showwarning("경고", "복원할 백업을 선택해주세요.")
                    return
                
                item = selection[0]
                backup_file = backup_tree.item(item, "tags")[0]
                
                # 확인 다이얼로그
                result = messagebox.askyesno(
                    "백업 복원 확인",
                    f"선택한 백업을 복원하시겠습니까?\n\n백업: {backup['backup_name']}\n\n주의: 현재 데이터가 백업으로 덮어써집니다."
                )
                
                if result:
                    # 백업 복원
                    success = self.backup_manager.restore_backup(backup_file, restore_settings=True)
                    
                    if success:
                        messagebox.showinfo("성공", "백업이 성공적으로 복원되었습니다.\n애플리케이션을 재시작해주세요.")
                        backup_window.destroy()
                        self.root.quit()
                    else:
                        messagebox.showerror("오류", "백업 복원 중 오류가 발생했습니다.")
            
            def cancel_restore():
                backup_window.destroy()
            
            ttk.Button(button_frame, text="복원", command=restore_selected).pack(side=tk.RIGHT, padx=5)
            ttk.Button(button_frame, text="취소", command=cancel_restore).pack(side=tk.RIGHT)
            
        except Exception as e:
            messagebox.showerror("오류", f"백업 복원 중 오류가 발생했습니다:\n{str(e)}")
    
    def _show_user_guide(self):
        """사용자 가이드 표시"""
        messagebox.showinfo("사용자 가이드", "사용자 가이드는 Phase 4에서 구현됩니다.")
    
    def _show_shortcuts(self):
        """단축키 표시"""
        shortcuts = """
        주요 단축키:
        Ctrl+N: 새 프로젝트
        Ctrl+O: 프로젝트 열기
        Ctrl+S: 프로젝트 저장
        Ctrl+Q: 종료
        F5: 프로젝트 실행
        Esc: 실행 중지
        """
        messagebox.showinfo("단축키", shortcuts)
    
    def _show_about(self):
        """정보 표시"""
        about_text = f"""
        {config.get_app_name()}
        버전: {config.get_app_version()}
        
        {config.get_app_description()}
        
        JSON 기반 데이터 저장
        단일 .exe 파일 배포 가능
        
        제작자: Photometry4040
        © 2025 Photometry4040. All rights reserved.
        
        배포 시 반드시 저작권 표시를 명기해주세요.
        """
        messagebox.showinfo("정보", about_text)
    
    # 트리뷰 이벤트 핸들러들
    def _on_project_select(self, event):
        """프로젝트 선택 이벤트"""
        selection = self.project_tree.selection()
        if selection:
            # 선택된 항목의 태그에서 프로젝트 ID 추출
            item = selection[0]
            tags = self.project_tree.item(item, "tags")
            
            for tag in tags:
                if tag.startswith("project_"):
                    project_id = int(tag.split("_")[1])
                    self.current_project = self.project_manager.get_project_by_id(project_id)
                    self._update_project_info()
                    self._refresh_action_list()
                    break
    
    def _on_action_select(self, event):
        """액션 선택 이벤트"""
        selection = self.action_tree.selection()
        if selection:
            # 선택된 액션 정보 표시
            pass
    
    def _on_action_double_click(self, event):
        """액션 더블클릭 이벤트"""
        self._edit_action()
    
    def _refresh_project_list(self):
        """프로젝트 목록 새로고침"""
        # 기존 항목 삭제
        for item in self.project_tree.get_children():
            self.project_tree.delete(item)
        
        # 프로젝트 목록 로드
        projects = self.project_manager.get_all_projects()
        
        # 트리뷰에 추가
        for project in projects:
            # 즐겨찾기 아이콘
            icon = "⭐" if project.favorite else "📁"
            
            self.project_tree.insert(
                "", 
                "end", 
                text=f"{icon} {project.name}",
                values=(project.name, project.get_action_count()),
                tags=(f"project_{project.id}",)
            )
        
        # 상태바 업데이트
        stats = self.project_manager.get_project_statistics()
        self.status_label.config(text=f"총 {stats['total_projects']}개 프로젝트, {stats['total_actions']}개 액션")
    
    def _update_project_info(self):
        """프로젝트 정보 업데이트"""
        if self.current_project:
            self.project_name_label.config(text=f"프로젝트명: {self.current_project.name}")
            self.project_desc_label.config(text=f"설명: {self.current_project.description}")
            self.project_actions_label.config(text=f"액션 수: {self.current_project.get_action_count()}개")
        else:
            self._clear_project_info()
    
    def _clear_project_info(self):
        """프로젝트 정보 초기화"""
        self.project_name_label.config(text="프로젝트명: 선택되지 않음")
        self.project_desc_label.config(text="설명: ")
        self.project_actions_label.config(text="액션 수: 0개")
        
        # 액션 목록도 초기화
        self._refresh_action_list()
    
    def _refresh_action_list(self):
        """액션 목록 새로고침"""
        # 기존 항목 삭제
        for item in self.action_tree.get_children():
            self.action_tree.delete(item)
        
        if self.current_project:
            # 액션 목록 로드
            actions = self.current_project.actions
            
            # 순서대로 정렬
            sorted_actions = sorted(actions, key=lambda x: x.get('order_index', 0))
            
            # 트리뷰에 추가
            for action in sorted_actions:
                action_type = action.get('action_type', 'unknown')
                description = action.get('description', '')
                
                # 액션 타입별 아이콘
                icon_map = {
                    'mouse_move': '🖱️',
                    'mouse_click': '👆',
                    'keyboard_type': '⌨️',
                    'delay': '⏱️',
                    'clipboard_copy': '📋',
                    'clipboard_paste': '📋'
                }
                icon = icon_map.get(action_type, '⚙️')
                
                self.action_tree.insert(
                    "",
                    "end",
                    text=f"{action.get('order_index', 0)}",
                    values=(
                        action.get('order_index', 0),
                        action_type,
                        description
                    ),
                    tags=(f"action_{action.get('id', 0)}",)
                )
    
    # 액션 관련 메서드들
    def _add_action(self):
        """액션 추가"""
        if not self.current_project:
            messagebox.showinfo("알림", "액션을 추가할 프로젝트를 선택해주세요.")
            return
        
        result = show_action_dialog(self.root, project_id=self.current_project.id)
        if result:
            # 새 액션을 프로젝트에 추가
            self.current_project.add_action(result)
            self.data_manager.save_project(self.current_project)
            
            # UI 업데이트
            self._refresh_action_list()
            self._update_project_info()
            self._refresh_project_list()
    
    def _edit_action(self):
        """액션 편집"""
        if not self.current_project:
            messagebox.showinfo("알림", "편집할 프로젝트를 선택해주세요.")
            return
        
        # 선택된 액션 확인
        selection = self.action_tree.selection()
        if not selection:
            messagebox.showinfo("알림", "편집할 액션을 선택해주세요.")
            return
        
        # 선택된 액션 찾기
        item = selection[0]
        tags = self.action_tree.item(item, "tags")
        
        for tag in tags:
            if tag.startswith("action_"):
                action_id = int(tag.split("_")[1])
                action = self.current_project.get_action_by_id(action_id)
                
                if action:
                    result = show_action_dialog(self.root, action, self.current_project.id)
                    if result:
                        # 액션 업데이트
                        self.current_project.update_action(action_id, result)
                        self.data_manager.save_project(self.current_project)
                        
                        # UI 업데이트
                        self._refresh_action_list()
                        self._update_project_info()
                        self._refresh_project_list()
                break
    
    def _delete_action(self):
        """액션 삭제"""
        if not self.current_project:
            messagebox.showinfo("알림", "삭제할 프로젝트를 선택해주세요.")
            return
        
        # 선택된 액션 확인
        selection = self.action_tree.selection()
        if not selection:
            messagebox.showinfo("알림", "삭제할 액션을 선택해주세요.")
            return
        
        # 선택된 액션 찾기
        item = selection[0]
        tags = self.action_tree.item(item, "tags")
        
        for tag in tags:
            if tag.startswith("action_"):
                action_id = int(tag.split("_")[1])
                action = self.current_project.get_action_by_id(action_id)
                
                if action:
                    # 삭제 확인
                    result = messagebox.askyesno(
                        "액션 삭제", 
                        f"액션 '{action.get('description', '')}'을(를) 삭제하시겠습니까?"
                    )
                    
                    if result:
                        # 액션 삭제
                        self.current_project.remove_action(action_id)
                        self.data_manager.save_project(self.current_project)
                        
                        # UI 업데이트
                        self._refresh_action_list()
                        self._update_project_info()
                        self._refresh_project_list()
                break
    
    def _move_action_up(self):
        """액션 위로 이동"""
        if not self.current_project:
            return
        
        # 선택된 액션 확인
        selection = self.action_tree.selection()
        if not selection:
            return
        
        # 선택된 액션 찾기
        item = selection[0]
        tags = self.action_tree.item(item, "tags")
        
        for tag in tags:
            if tag.startswith("action_"):
                action_id = int(tag.split("_")[1])
                
                # 액션 순서 변경
                if self.current_project.move_action_up(action_id):
                    self.data_manager.save_project(self.current_project)
                    
                    # UI 업데이트
                    self._refresh_action_list()
                    self._update_project_info()
                    self._refresh_project_list()
                    
                    # 이동된 항목 선택
                    self._select_action_by_id(action_id)
                break
    
    def _move_action_down(self):
        """액션 아래로 이동"""
        if not self.current_project:
            return
        
        # 선택된 액션 확인
        selection = self.action_tree.selection()
        if not selection:
            return
        
        # 선택된 액션 찾기
        item = selection[0]
        tags = self.action_tree.item(item, "tags")
        
        for tag in tags:
            if tag.startswith("action_"):
                action_id = int(tag.split("_")[1])
                
                # 액션 순서 변경
                if self.current_project.move_action_down(action_id):
                    self.data_manager.save_project(self.current_project)
                    
                    # UI 업데이트
                    self._refresh_action_list()
                    self._update_project_info()
                    self._refresh_project_list()
                    
                    # 이동된 항목 선택
                    self._select_action_by_id(action_id)
                break
    
    def _select_action_by_id(self, action_id: int):
        """액션 ID로 항목 선택"""
        for item in self.action_tree.get_children():
            tags = self.action_tree.item(item, "tags")
            for tag in tags:
                if tag.startswith("action_") and int(tag.split("_")[1]) == action_id:
                    self.action_tree.selection_set(item)
                    self.action_tree.see(item)
                    return
    
    # 실행 콜백 메서드들
    def _on_execution_progress(self, current_action: int, total_actions: int, action_description: str):
        """실행 진행 상황 콜백"""
        # 상태바 업데이트
        progress_text = f"실행 중... ({current_action}/{total_actions}) {action_description}"
        self.status_label.config(text=progress_text)
        
        # 진행률 표시
        progress_percent = (current_action / total_actions) * 100
        self.progress_bar['value'] = progress_percent
        
        # UI 업데이트
        self.root.update_idletasks()
    
    def _on_execution_complete(self, success: bool, message: str):
        """실행 완료 콜백"""
        # 상태바 초기화
        self.status_label.config(text="준비")
        self.progress_bar['value'] = 0
        
        # 실행 버튼 상태 업데이트
        self._update_execution_buttons()
        
        # 완료 메시지 표시
        if success:
            messagebox.showinfo("실행 완료", f"프로젝트 실행이 완료되었습니다.\n\n{message}")
        else:
            messagebox.showerror("실행 실패", f"프로젝트 실행에 실패했습니다.\n\n{message}")
    
    def _on_execution_error(self, error_message: str):
        """실행 오류 콜백"""
        # 상태바 초기화
        self.status_label.config(text="오류 발생")
        self.progress_bar['value'] = 0
        
        # 실행 버튼 상태 업데이트
        self._update_execution_buttons()
        
        # 오류 메시지 표시
        messagebox.showerror("실행 오류", f"실행 중 오류가 발생했습니다:\n\n{error_message}")
    
    def _on_action_recorded(self, action: Dict):
        """액션 녹화 콜백"""
        # 상태바 업데이트
        action_type = action.get('action_type', '')
        self.status_label.config(text=f"액션 녹화됨: {action_type}")
        
        # UI 업데이트
        self.root.update_idletasks()
    
    def _on_recording_stopped(self, recorded_actions: List[Dict]):
        """녹화 중지 콜백"""
        # 상태바 초기화
        self.status_label.config(text="녹화 완료")
        
        # 녹화 버튼 상태 업데이트
        self._update_recording_button()
    
    def _update_execution_buttons(self):
        """실행 버튼 상태 업데이트"""
        is_running = self.action_executor.is_running
        status = self.action_executor.get_execution_status()
        
        # 실행 버튼
        if hasattr(self, 'run_button'):
            self.run_button.config(state='disabled' if is_running else 'normal')
        
        # 중지 버튼
        if hasattr(self, 'stop_button'):
            self.stop_button.config(state='normal' if is_running else 'disabled')
        
        # 일시정지/재개 버튼
        if hasattr(self, 'pause_button'):
            if is_running:
                self.pause_button.config(
                    text="재개" if status.get('is_paused', False) else "일시정지",
                    state='normal'
                )
            else:
                self.pause_button.config(text="일시정지", state='disabled')
    
    def _update_recording_button(self):
        """녹화 버튼 상태 업데이트"""
        is_recording = self.macro_recorder.is_recording
        
        if hasattr(self, 'record_button'):
            if is_recording:
                self.record_button.config(text="녹화 중지", style="Danger.TButton")
            else:
                self.record_button.config(text="녹화 시작", style="Normal.TButton")
    
    def _show_recording_result(self, recorded_actions: List[Dict]):
        """녹화 결과 표시"""
        if not recorded_actions:
            messagebox.showinfo("녹화 결과", "녹화된 액션이 없습니다.")
            return
        
        # 녹화 결과를 현재 프로젝트에 추가할지 확인
        result = messagebox.askyesno(
            "녹화 완료",
            f"총 {len(recorded_actions)}개의 액션이 녹화되었습니다.\n\n"
            "현재 프로젝트에 추가하시겠습니까?"
        )
        
        if result and self.current_project:
            # 녹화된 액션들을 프로젝트에 추가
            for action in recorded_actions:
                action_id = self.data_manager.get_next_action_id()
                order_index = self.data_manager.get_next_action_order(self.current_project.id)
                
                new_action = {
                    'id': action_id,
                    'order_index': order_index,
                    'action_type': action['action_type'],
                    'description': action['description'],
                    'parameters': action['parameters']
                }
                
                self.data_manager.save_action(self.current_project.id, new_action)
            
            # UI 업데이트
            self._refresh_action_list()
            self._update_project_info()
            self._refresh_project_list()
            
            messagebox.showinfo("추가 완료", f"{len(recorded_actions)}개의 액션이 프로젝트에 추가되었습니다.")
    
    def run(self):
        """애플리케이션 실행"""
        self.root.mainloop() 