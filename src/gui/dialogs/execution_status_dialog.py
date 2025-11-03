"""
실행 상태 다이얼로그
프로젝트 실행 상태를 실시간으로 표시하는 다이얼로그
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict
import time

from ...core.action_executor import ActionExecutor


class ExecutionStatusDialog:
    """실행 상태 다이얼로그 클래스"""

    def __init__(self, parent, action_executor: ActionExecutor):
        """
        초기화

        Args:
            parent: 부모 윈도우
            action_executor: 액션 실행 엔진
        """
        self.parent = parent
        self.action_executor = action_executor
        self.update_interval = 200  # 200ms마다 업데이트
        self.update_timer_id = None  # 타이머 ID 저장

        # 다이얼로그 생성
        self.dialog = tk.Toplevel(parent)
        self.dialog.transient(parent)

        self._setup_dialog()
        self._create_widgets()
        self._bind_events()

        # 다이얼로그를 화면 중앙에 배치
        self._center_dialog()

        # 초기 상태 업데이트
        self._update_status()

    def _setup_dialog(self):
        """다이얼로그 기본 설정"""
        self.dialog.title("실행 상태")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)

        # 포커스 설정
        self.dialog.focus_set()

    def _create_widgets(self):
        """위젯 생성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 제목
        title_label = ttk.Label(
            main_frame,
            text="실행 상태 모니터",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))

        # 상태 정보 프레임
        info_frame = ttk.LabelFrame(main_frame, text="실행 정보", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 실행 상태
        status_container = ttk.Frame(info_frame)
        status_container.pack(fill=tk.X, pady=5)

        ttk.Label(status_container, text="실행 상태:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.status_value = ttk.Label(status_container, text="확인 중...", font=("Arial", 10))
        self.status_value.pack(side=tk.LEFT, padx=(10, 0))

        # 현재 액션
        action_container = ttk.Frame(info_frame)
        action_container.pack(fill=tk.X, pady=5)

        ttk.Label(action_container, text="현재 액션:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.action_value = ttk.Label(action_container, text="-", font=("Arial", 10))
        self.action_value.pack(side=tk.LEFT, padx=(10, 0))

        # 진행률
        progress_container = ttk.Frame(info_frame)
        progress_container.pack(fill=tk.X, pady=5)

        ttk.Label(progress_container, text="진행률:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.progress_value = ttk.Label(progress_container, text="0%", font=("Arial", 10))
        self.progress_value.pack(side=tk.LEFT, padx=(10, 0))

        # 진행률 바
        self.progress_bar = ttk.Progressbar(
            info_frame,
            mode='determinate',
            length=400
        )
        self.progress_bar.pack(fill=tk.X, pady=10)

        # 실행 시간
        time_container = ttk.Frame(info_frame)
        time_container.pack(fill=tk.X, pady=5)

        ttk.Label(time_container, text="실행 시간:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.time_value = ttk.Label(time_container, text="00:00:00", font=("Arial", 10))
        self.time_value.pack(side=tk.LEFT, padx=(10, 0))

        # 예상 남은 시간
        remaining_container = ttk.Frame(info_frame)
        remaining_container.pack(fill=tk.X, pady=5)

        ttk.Label(remaining_container, text="예상 남은 시간:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.remaining_value = ttk.Label(remaining_container, text="-", font=("Arial", 10))
        self.remaining_value.pack(side=tk.LEFT, padx=(10, 0))

        # 일시정지 상태
        pause_container = ttk.Frame(info_frame)
        pause_container.pack(fill=tk.X, pady=5)

        ttk.Label(pause_container, text="일시정지:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.pause_value = ttk.Label(pause_container, text="아니오", font=("Arial", 10))
        self.pause_value.pack(side=tk.LEFT, padx=(10, 0))

        # 상세 정보 프레임
        detail_frame = ttk.LabelFrame(main_frame, text="상세 정보", padding="10")
        detail_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 상세 정보 텍스트
        self.detail_text = tk.Text(
            detail_frame,
            height=5,
            wrap=tk.WORD,
            font=("Consolas", 9)
        )
        self.detail_text.pack(fill=tk.BOTH, expand=True)
        self.detail_text.config(state=tk.DISABLED)

        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        # 새로고침 버튼
        self.refresh_button = ttk.Button(
            button_frame,
            text="새로고침",
            command=self._manual_refresh
        )
        self.refresh_button.pack(side=tk.LEFT, padx=(0, 5))

        # 닫기 버튼
        self.close_button = ttk.Button(
            button_frame,
            text="닫기",
            command=self._close
        )
        self.close_button.pack(side=tk.RIGHT)

    def _bind_events(self):
        """이벤트 바인딩"""
        self.dialog.protocol("WM_DELETE_WINDOW", self._close)

    def _center_dialog(self):
        """다이얼로그를 화면 중앙에 배치"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")

    def _update_status(self):
        """상태 업데이트"""
        try:
            # 실행 상태 가져오기
            status = self.action_executor.get_execution_status()

            # 실행 상태 표시
            if status['is_running']:
                if status['is_paused']:
                    self.status_value.config(text="일시정지됨", foreground="orange")
                else:
                    self.status_value.config(text="실행 중", foreground="green")
            else:
                self.status_value.config(text="중지됨", foreground="red")

            # 현재 액션 표시
            if status['is_running'] and status['total_actions'] > 0:
                action_index = status['current_action_index']
                total = status['total_actions']
                self.action_value.config(text=f"액션 #{action_index + 1} / {total}")
            else:
                self.action_value.config(text="-")

            # 진행률 표시
            if status['is_running'] and status['total_actions'] > 0:
                progress = status['progress_percent']
                self.progress_value.config(text=f"{progress:.1f}%")
                self.progress_bar['value'] = progress
            else:
                self.progress_value.config(text="0%")
                self.progress_bar['value'] = 0

            # 일시정지 상태
            self.pause_value.config(
                text="예" if status['is_paused'] else "아니오",
                foreground="orange" if status['is_paused'] else "black"
            )

            # 실행 시간 표시
            elapsed = status['elapsed_time']
            if elapsed > 0:
                hours = int(elapsed // 3600)
                minutes = int((elapsed % 3600) // 60)
                seconds = int(elapsed % 60)
                self.time_value.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            else:
                self.time_value.config(text="00:00:00")

            # 예상 남은 시간 표시
            remaining = status['estimated_remaining_time']
            if remaining > 0:
                hours = int(remaining // 3600)
                minutes = int((remaining % 3600) // 60)
                seconds = int(remaining % 60)
                self.remaining_value.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            else:
                self.remaining_value.config(text="-")

            # 상세 정보 업데이트
            self._update_details(status)

        except Exception as e:
            # 에러 발생 시에도 상태는 표시
            self.status_value.config(text="오류", foreground="red")
            self._log_detail(f"상태 업데이트 오류: {str(e)}")

        finally:
            # 다음 업데이트 예약 (에러 발생 시에도 계속 업데이트)
            # 다이얼로그가 존재하는 경우에만 타이머 예약
            try:
                self.update_timer_id = self.dialog.after(self.update_interval, self._update_status)
            except tk.TclError:
                # 다이얼로그가 이미 파괴된 경우 무시
                pass

    def _update_details(self, status: Dict):
        """상세 정보 업데이트"""
        details = []
        details.append(f"실행 중: {status['is_running']}")
        details.append(f"일시정지: {status['is_paused']}")
        details.append(f"중지 요청: {status['should_stop']}")
        details.append(f"현재 액션 인덱스: {status['current_action_index']}")
        details.append(f"총 액션 수: {status['total_actions']}")
        details.append(f"진행률: {status['progress_percent']:.2f}%")
        details.append(f"경과 시간: {status['elapsed_time']:.2f}초")
        details.append(f"예상 남은 시간: {status['estimated_remaining_time']:.2f}초")
        details.append(f"액션당 평균 시간: {status['average_action_time']:.2f}초")

        detail_text = "\n".join(details)

        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.insert(1.0, detail_text)
        self.detail_text.config(state=tk.DISABLED)

    def _log_detail(self, message: str):
        """상세 로그 추가"""
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.insert(tk.END, f"\n{message}")
        self.detail_text.see(tk.END)
        self.detail_text.config(state=tk.DISABLED)

    def _manual_refresh(self):
        """수동 새로고침"""
        # 현재 타이머 취소 후 즉시 업데이트
        if self.update_timer_id is not None:
            try:
                self.dialog.after_cancel(self.update_timer_id)
                self.update_timer_id = None
            except tk.TclError:
                pass
        self._update_status()

    def _close(self):
        """다이얼로그 닫기"""
        # 타이머 취소
        if self.update_timer_id is not None:
            try:
                self.dialog.after_cancel(self.update_timer_id)
                self.update_timer_id = None
            except tk.TclError:
                pass
        # 다이얼로그 파괴
        self.dialog.destroy()

    def show(self):
        """다이얼로그 표시"""
        self.dialog.wait_window()


def show_execution_status_dialog(parent, action_executor: ActionExecutor):
    """
    실행 상태 다이얼로그 표시

    Args:
        parent: 부모 윈도우
        action_executor: 액션 실행 엔진
    """
    dialog = ExecutionStatusDialog(parent, action_executor)
    dialog.show()
