# -*- coding: utf-8 -*-
"""
실행 로그 뷰어 다이얼로그
액션 실행 로그 및 통계를 표시하는 다이얼로그
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import List, Dict, Optional


def show_execution_log_dialog(parent, action_executor):
    """
    실행 로그 뷰어 다이얼로그 표시

    Args:
        parent: 부모 윈도우
        action_executor: ActionExecutor 인스턴스
    """
    dialog = ExecutionLogDialog(parent, action_executor)
    dialog.show()


class ExecutionLogDialog:
    """실행 로그 뷰어 다이얼로그"""

    def __init__(self, parent, action_executor):
        """초기화"""
        self.parent = parent
        self.action_executor = action_executor
        self.window = None

    def show(self):
        """다이얼로그 표시"""
        # 윈도우 생성
        self.window = tk.Toplevel(self.parent)
        self.window.title("실행 로그 뷰어")
        self.window.geometry("900x600")
        self.window.transient(self.parent)
        self.window.grab_set()

        # 메인 프레임
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 통계 프레임
        self._create_statistics_frame(main_frame)

        # 로그 목록 프레임
        self._create_log_frame(main_frame)

        # 버튼 프레임
        self._create_button_frame(main_frame)

        # 데이터 로드
        self._load_data()

    def _create_statistics_frame(self, parent):
        """통계 프레임 생성"""
        stats_frame = ttk.LabelFrame(parent, text="실행 통계", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        # 통계 라벨들
        self.stats_labels = {}

        # 첫 번째 줄
        row1 = ttk.Frame(stats_frame)
        row1.pack(fill=tk.X, pady=2)

        ttk.Label(row1, text="총 액션 수:", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
        self.stats_labels['total'] = ttk.Label(row1, text="0개", font=("Arial", 9))
        self.stats_labels['total'].pack(side=tk.LEFT, padx=5)

        ttk.Label(row1, text="성공:", font=("Arial", 9, "bold"), foreground="green").pack(side=tk.LEFT, padx=5)
        self.stats_labels['success'] = ttk.Label(row1, text="0개", font=("Arial", 9), foreground="green")
        self.stats_labels['success'].pack(side=tk.LEFT, padx=5)

        ttk.Label(row1, text="실패:", font=("Arial", 9, "bold"), foreground="red").pack(side=tk.LEFT, padx=5)
        self.stats_labels['failed'] = ttk.Label(row1, text="0개", font=("Arial", 9), foreground="red")
        self.stats_labels['failed'].pack(side=tk.LEFT, padx=5)

        # 두 번째 줄
        row2 = ttk.Frame(stats_frame)
        row2.pack(fill=tk.X, pady=2)

        ttk.Label(row2, text="총 실행 시간:", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
        self.stats_labels['total_time'] = ttk.Label(row2, text="0.000초", font=("Arial", 9))
        self.stats_labels['total_time'].pack(side=tk.LEFT, padx=5)

        ttk.Label(row2, text="평균 시간:", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
        self.stats_labels['avg_time'] = ttk.Label(row2, text="0.000초", font=("Arial", 9))
        self.stats_labels['avg_time'].pack(side=tk.LEFT, padx=5)

        ttk.Label(row2, text="최소:", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
        self.stats_labels['min_time'] = ttk.Label(row2, text="0.000초", font=("Arial", 9))
        self.stats_labels['min_time'].pack(side=tk.LEFT, padx=5)

        ttk.Label(row2, text="최대:", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
        self.stats_labels['max_time'] = ttk.Label(row2, text="0.000초", font=("Arial", 9))
        self.stats_labels['max_time'].pack(side=tk.LEFT, padx=5)

    def _create_log_frame(self, parent):
        """로그 목록 프레임 생성"""
        log_frame = ttk.LabelFrame(parent, text="실행 로그", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 로그 트리뷰
        columns = ("index", "time", "action", "status", "exec_time", "retry", "error")
        self.log_tree = ttk.Treeview(log_frame, columns=columns, show="headings", height=15)

        # 컬럼 설정
        self.log_tree.heading("index", text="번호")
        self.log_tree.heading("time", text="시간")
        self.log_tree.heading("action", text="액션")
        self.log_tree.heading("status", text="상태")
        self.log_tree.heading("exec_time", text="실행시간")
        self.log_tree.heading("retry", text="재시도")
        self.log_tree.heading("error", text="오류 메시지")

        self.log_tree.column("index", width=50, anchor='center')
        self.log_tree.column("time", width=150, anchor='center')
        self.log_tree.column("action", width=200)
        self.log_tree.column("status", width=80, anchor='center')
        self.log_tree.column("exec_time", width=100, anchor='center')
        self.log_tree.column("retry", width=80, anchor='center')
        self.log_tree.column("error", width=200)

        # 스크롤바
        scrollbar_y = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_tree.yview)
        scrollbar_x = ttk.Scrollbar(log_frame, orient=tk.HORIZONTAL, command=self.log_tree.xview)
        self.log_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # 배치
        self.log_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # 태그 색상 설정
        self.log_tree.tag_configure('success', foreground='green')
        self.log_tree.tag_configure('failed', foreground='red')

    def _create_button_frame(self, parent):
        """버튼 프레임 생성"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="새로고침", command=self._load_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="로그 내보내기", command=self._export_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="닫기", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)

    def _load_data(self):
        """데이터 로드 및 표시"""
        # 통계 로드
        stats = self.action_executor.get_execution_statistics()
        self.stats_labels['total'].config(text=f"{stats['total_actions']}개")
        self.stats_labels['success'].config(text=f"{stats['successful_actions']}개")
        self.stats_labels['failed'].config(text=f"{stats['failed_actions']}개")
        self.stats_labels['total_time'].config(text=f"{stats['total_execution_time']:.3f}초")
        self.stats_labels['avg_time'].config(text=f"{stats['average_execution_time']:.3f}초")
        self.stats_labels['min_time'].config(text=f"{stats['min_execution_time']:.3f}초")
        self.stats_labels['max_time'].config(text=f"{stats['max_execution_time']:.3f}초")

        # 로그 목록 초기화
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)

        # 로그 로드
        logs = self.action_executor.get_execution_log()
        for log in logs:
            # 시간 포맷팅
            timestamp = datetime.fromtimestamp(log['timestamp']).strftime('%Y-%m-%d %H:%M:%S')

            # 상태에 따라 태그 설정
            tag = 'success' if log['status'] == 'success' else 'failed'

            # 행 추가
            self.log_tree.insert("", "end", values=(
                log['action_index'] + 1,
                timestamp,
                log['description'][:30] + '...' if len(log['description']) > 30 else log['description'],
                log['status'],
                f"{log['execution_time']:.3f}초",
                f"{log['retry_count']}회" if log['retry_count'] > 0 else "-",
                log.get('error', '')[:50] if log.get('error') else ""
            ), tags=(tag,))

    def _export_log(self):
        """로그 내보내기"""
        # 파일 선택 다이얼로그
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")],
            title="로그 내보내기"
        )

        if not file_path:
            return

        try:
            import csv

            logs = self.action_executor.get_execution_log()

            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # 헤더
                writer.writerow(['번호', '시간', '액션 ID', '액션 타입', '설명', '상태', '실행시간', '재시도', '오류'])

                # 데이터
                for log in logs:
                    timestamp = datetime.fromtimestamp(log['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                    writer.writerow([
                        log['action_index'] + 1,
                        timestamp,
                        log['action_id'],
                        log['action_type'],
                        log['description'],
                        log['status'],
                        f"{log['execution_time']:.3f}",
                        log['retry_count'],
                        log.get('error', '')
                    ])

            messagebox.showinfo("성공", f"로그가 저장되었습니다:\n{file_path}")

        except Exception as e:
            messagebox.showerror("오류", f"로그 내보내기 중 오류가 발생했습니다:\n{str(e)}")
