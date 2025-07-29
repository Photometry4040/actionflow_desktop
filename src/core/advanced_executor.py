"""
고급 매크로 실행 엔진
조건부 실행, 반복 설정, 스케줄링 등의 고급 기능
"""
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
import pyautogui
import pyperclip

from ..models.project import Project
from ..utils.config import config
from ..utils.history_manager import HistoryManager
from .action_executor import ActionExecutor


class AdvancedExecutor:
    """고급 매크로 실행 엔진 클래스"""
    
    def __init__(self):
        """초기화"""
        self.action_executor = ActionExecutor()
        self.history_manager = HistoryManager()
        self.is_running = False
        self.is_paused = False
        self.should_stop = False
        self.current_iteration = 0
        self.total_iterations = 1
        self.execution_thread = None
        
        # 콜백 함수들
        self.on_progress_callback = None
        self.on_complete_callback = None
        self.on_error_callback = None
        self.on_iteration_callback = None
    
    def execute_with_repeat(self, project: Project, repeat_count: int = 1,
                          repeat_interval: float = 1.0,
                          on_progress: Optional[Callable] = None,
                          on_complete: Optional[Callable] = None,
                          on_error: Optional[Callable] = None,
                          on_iteration: Optional[Callable] = None) -> bool:
        """
        반복 실행
        
        Args:
            project: 실행할 프로젝트
            repeat_count: 반복 횟수
            repeat_interval: 반복 간격 (초)
            on_progress: 진행 상황 콜백
            on_complete: 완료 콜백
            on_error: 오류 콜백
            on_iteration: 반복 완료 콜백
        
        Returns:
            성공 여부
        """
        if self.is_running:
            return False
        
        self.on_progress_callback = on_progress
        self.on_complete_callback = on_complete
        self.on_error_callback = on_error
        self.on_iteration_callback = on_iteration
        
        # 실행 스레드 시작
        self.execution_thread = threading.Thread(
            target=self._execute_with_repeat_thread,
            args=(project, repeat_count, repeat_interval)
        )
        self.execution_thread.daemon = True
        self.execution_thread.start()
        
        return True
    
    def _execute_with_repeat_thread(self, project: Project, repeat_count: int, repeat_interval: float):
        """반복 실행 스레드"""
        try:
            self.is_running = True
            self.is_paused = False
            self.should_stop = False
            self.current_iteration = 0
            self.total_iterations = repeat_count
            
            start_time = time.time()
            success_count = 0
            failed_count = 0
            
            for iteration in range(repeat_count):
                if self.should_stop:
                    break
                
                self.current_iteration = iteration + 1
                
                # 반복 시작 콜백
                self._call_callback(self.on_iteration_callback, iteration + 1, repeat_count)
                
                # 프로젝트 실행
                execution_start = time.time()
                success = self._execute_single_project(project)
                execution_duration = time.time() - execution_start
                
                # 실행 기록 추가
                status = "success" if success else "failed"
                error_message = None if success else "실행 중 오류 발생"
                
                self.history_manager.add_execution_record(
                    project_id=project.id,
                    project_name=project.name,
                    duration=execution_duration,
                    status=status,
                    total_actions=len(project.actions),
                    executed_actions=len(project.actions) if success else 0,
                    error_message=error_message,
                    execution_speed=config.get_execution_speed(),
                    notes=f"반복 실행 {iteration + 1}/{repeat_count}"
                )
                
                if success:
                    success_count += 1
                else:
                    failed_count += 1
                
                # 마지막 반복이 아니면 대기
                if iteration < repeat_count - 1 and not self.should_stop:
                    time.sleep(repeat_interval)
            
            total_duration = time.time() - start_time
            
            # 완료 콜백 호출
            result = {
                "total_iterations": repeat_count,
                "success_count": success_count,
                "failed_count": failed_count,
                "total_duration": total_duration,
                "success_rate": (success_count / repeat_count) * 100 if repeat_count > 0 else 0
            }
            
            if failed_count == 0:
                self._call_callback(self.on_complete_callback, result)
            else:
                self._call_callback(self.on_error_callback, f"{failed_count}번의 실행이 실패했습니다.")
            
        except Exception as e:
            error_msg = f"반복 실행 중 오류 발생: {str(e)}"
            self._call_callback(self.on_error_callback, error_msg)
        finally:
            self.is_running = False
            self.is_paused = False
            self.should_stop = False
    
    def _execute_single_project(self, project: Project) -> bool:
        """단일 프로젝트 실행"""
        try:
            # 액션 순서대로 정렬
            sorted_actions = sorted(project.actions, key=lambda x: x.get('order_index', 0))
            
            for action in sorted_actions:
                if self.should_stop:
                    return False
                
                # 일시정지 확인
                while self.is_paused and not self.should_stop:
                    time.sleep(0.1)
                
                if self.should_stop:
                    return False
                
                # 액션 실행
                success = self.action_executor.execute_single_action(action)
                if not success:
                    return False
            
            return True
            
        except Exception as e:
            print(f"프로젝트 실행 중 오류: {str(e)}")
            return False
    
    def execute_with_conditions(self, project: Project, conditions: Dict,
                              on_progress: Optional[Callable] = None,
                              on_complete: Optional[Callable] = None,
                              on_error: Optional[Callable] = None) -> bool:
        """
        조건부 실행
        
        Args:
            project: 실행할 프로젝트
            conditions: 실행 조건
            on_progress: 진행 상황 콜백
            on_complete: 완료 콜백
            on_error: 오류 콜백
        
        Returns:
            성공 여부
        """
        if self.is_running:
            return False
        
        # 조건 검사
        if not self._check_conditions(conditions):
            self._call_callback(on_error, "실행 조건을 만족하지 않습니다.")
            return False
        
        # 일반 실행으로 진행
        return self.action_executor.execute_project(
            project, on_progress, on_complete, on_error
        )
    
    def _check_conditions(self, conditions: Dict) -> bool:
        """실행 조건 검사"""
        try:
            # 시간 조건 검사
            if "time_condition" in conditions:
                time_cond = conditions["time_condition"]
                current_time = datetime.now()
                
                if "start_time" in time_cond:
                    start_time = datetime.strptime(time_cond["start_time"], "%H:%M")
                    if current_time.time() < start_time.time():
                        return False
                
                if "end_time" in time_cond:
                    end_time = datetime.strptime(time_cond["end_time"], "%H:%M")
                    if current_time.time() > end_time.time():
                        return False
            
            # 화면 조건 검사
            if "screen_condition" in conditions:
                screen_cond = conditions["screen_condition"]
                
                if "check_pixel" in screen_cond:
                    pixel_cond = screen_cond["check_pixel"]
                    x, y = pixel_cond["x"], pixel_cond["y"]
                    expected_color = pixel_cond["color"]
                    
                    try:
                        actual_color = pyautogui.pixel(x, y)
                        if actual_color != expected_color:
                            return False
                    except Exception:
                        return False
            
            # 파일 조건 검사
            if "file_condition" in conditions:
                file_cond = conditions["file_condition"]
                
                if "file_exists" in file_cond:
                    import os
                    if not os.path.exists(file_cond["file_exists"]):
                        return False
            
            return True
            
        except Exception as e:
            print(f"조건 검사 중 오류: {str(e)}")
            return False
    
    def schedule_execution(self, project: Project, schedule_time: datetime,
                          repeat_daily: bool = False,
                          on_progress: Optional[Callable] = None,
                          on_complete: Optional[Callable] = None,
                          on_error: Optional[Callable] = None) -> bool:
        """
        스케줄 실행
        
        Args:
            project: 실행할 프로젝트
            schedule_time: 예약 시간
            repeat_daily: 매일 반복 여부
            on_progress: 진행 상황 콜백
            on_complete: 완료 콜백
            on_error: 오류 콜백
        
        Returns:
            성공 여부
        """
        if self.is_running:
            return False
        
        # 스케줄 스레드 시작
        self.execution_thread = threading.Thread(
            target=self._schedule_execution_thread,
            args=(project, schedule_time, repeat_daily, on_progress, on_complete, on_error)
        )
        self.execution_thread.daemon = True
        self.execution_thread.start()
        
        return True
    
    def _schedule_execution_thread(self, project: Project, schedule_time: datetime,
                                 repeat_daily: bool, on_progress, on_complete, on_error):
        """스케줄 실행 스레드"""
        try:
            while not self.should_stop:
                current_time = datetime.now()
                
                # 실행 시간이 되었는지 확인
                if current_time >= schedule_time:
                    # 프로젝트 실행
                    success = self.action_executor.execute_project(
                        project, on_progress, on_complete, on_error
                    )
                    
                    if not repeat_daily:
                        break
                    
                    # 다음 실행 시간 계산 (24시간 후)
                    schedule_time += timedelta(days=1)
                
                # 1분마다 확인
                time.sleep(60)
            
        except Exception as e:
            error_msg = f"스케줄 실행 중 오류 발생: {str(e)}"
            self._call_callback(on_error, error_msg)
    
    def execute_with_retry(self, project: Project, max_retries: int = 3,
                          retry_interval: float = 5.0,
                          on_progress: Optional[Callable] = None,
                          on_complete: Optional[Callable] = None,
                          on_error: Optional[Callable] = None) -> bool:
        """
        재시도 실행
        
        Args:
            project: 실행할 프로젝트
            max_retries: 최대 재시도 횟수
            retry_interval: 재시도 간격 (초)
            on_progress: 진행 상황 콜백
            on_complete: 완료 콜백
            on_error: 오류 콜백
        
        Returns:
            성공 여부
        """
        if self.is_running:
            return False
        
        # 재시도 스레드 시작
        self.execution_thread = threading.Thread(
            target=self._execute_with_retry_thread,
            args=(project, max_retries, retry_interval, on_progress, on_complete, on_error)
        )
        self.execution_thread.daemon = True
        self.execution_thread.start()
        
        return True
    
    def _execute_with_retry_thread(self, project: Project, max_retries: int,
                                 retry_interval: float, on_progress, on_complete, on_error):
        """재시도 실행 스레드"""
        try:
            self.is_running = True
            
            for attempt in range(max_retries + 1):
                if self.should_stop:
                    break
                
                # 프로젝트 실행
                success = self.action_executor.execute_project(
                    project, on_progress, on_complete, on_error
                )
                
                if success:
                    # 성공하면 종료
                    break
                
                # 마지막 시도가 아니면 재시도
                if attempt < max_retries and not self.should_stop:
                    self._call_callback(on_progress, f"실행 실패. {retry_interval}초 후 재시도합니다... ({attempt + 1}/{max_retries})")
                    time.sleep(retry_interval)
            
            if not success:
                self._call_callback(on_error, f"최대 재시도 횟수({max_retries})를 초과했습니다.")
            
        except Exception as e:
            error_msg = f"재시도 실행 중 오류 발생: {str(e)}"
            self._call_callback(on_error, error_msg)
        finally:
            self.is_running = False
    
    def stop_execution(self):
        """실행 중지"""
        self.should_stop = True
        self.action_executor.stop_execution()
    
    def pause_execution(self):
        """실행 일시정지"""
        self.is_paused = True
        self.action_executor.pause_execution()
    
    def resume_execution(self):
        """실행 재개"""
        self.is_paused = False
        self.action_executor.resume_execution()
    
    def get_execution_status(self) -> Dict:
        """실행 상태 반환"""
        status = self.action_executor.get_execution_status()
        status.update({
            "current_iteration": self.current_iteration,
            "total_iterations": self.total_iterations,
            "is_advanced_execution": self.is_running
        })
        return status
    
    def _call_callback(self, callback: Optional[Callable], *args):
        """콜백 함수 호출"""
        if callback:
            try:
                callback(*args)
            except Exception as e:
                print(f"콜백 호출 오류: {str(e)}")
    
    def get_execution_history(self, project_id: Optional[int] = None, limit: int = 10) -> List:
        """실행 히스토리 조회"""
        return self.history_manager.get_execution_records(project_id, limit)
    
    def get_execution_statistics(self, project_id: Optional[int] = None) -> Dict:
        """실행 통계 조회"""
        return self.history_manager.get_execution_statistics(project_id) 