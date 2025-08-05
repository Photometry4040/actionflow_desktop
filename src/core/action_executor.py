"""
액션 실행 엔진
마우스/키보드 제어 및 액션 실행을 담당하는 핵심 모듈
"""
import time
import threading
from typing import Dict, List, Optional, Callable
import pyautogui
import pyperclip

from ..models.project import Project
from ..utils.config import config


class ActionExecutor:
    """액션 실행 엔진 클래스"""
    
    def __init__(self):
        """초기화"""
        self.is_running = False
        self.is_paused = False
        self.should_stop = False
        self.current_action_index = 0
        self.execution_thread = None
        self.on_progress_callback = None
        self.on_complete_callback = None
        self.on_error_callback = None
        
        # 안전 장치 설정
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # ESC 키로 중단 설정 (macOS에서는 관리자 권한 필요하므로 제거)
        # keyboard.on_press_key('esc', self._emergency_stop)
    
    def execute_project(self, project: Project, 
                       on_progress: Optional[Callable] = None,
                       on_complete: Optional[Callable] = None,
                       on_error: Optional[Callable] = None) -> bool:
        """
        프로젝트 실행
        
        Args:
            project: 실행할 프로젝트
            on_progress: 진행 상황 콜백 (action_index, total_actions)
            on_complete: 완료 콜백
            on_error: 오류 콜백 (error_message)
        
        Returns:
            성공 여부
        """
        if self.is_running:
            return False
        
        self.on_progress_callback = on_progress
        self.on_complete_callback = on_complete
        self.on_error_callback = on_error
        
        # 실행 스레드 시작
        self.execution_thread = threading.Thread(
            target=self._execute_project_thread,
            args=(project,)
        )
        self.execution_thread.daemon = True
        self.execution_thread.start()
        
        return True
    
    def _execute_project_thread(self, project: Project):
        """프로젝트 실행 스레드"""
        try:
            self.is_running = True
            self.is_paused = False
            self.should_stop = False
            self.current_action_index = 0
            
            actions = project.actions
            total_actions = len(actions)
            
            if total_actions == 0:
                self._call_callback(self.on_complete_callback)
                return
            
            # 액션 순서대로 정렬
            sorted_actions = sorted(actions, key=lambda x: x.get('order_index', 0))
            
            for i, action in enumerate(sorted_actions):
                if self.should_stop:
                    break
                
                # 일시정지 확인
                while self.is_paused and not self.should_stop:
                    time.sleep(0.1)
                
                if self.should_stop:
                    break
                
                # 현재 액션 인덱스 업데이트
                self.current_action_index = i
                
                # 진행 상황 콜백 호출
                action_description = action.get('description', f'액션 {i+1}')
                self._call_callback(self.on_progress_callback, i+1, total_actions, action_description)
                
                # 액션 실행
                success = self._execute_action(action)
                if not success:
                    error_msg = f"액션 실행 실패: {action.get('description', '알 수 없는 액션')}"
                    self._call_callback(self.on_error_callback, error_msg)
                    return
            
            # 완료 콜백 호출
            if not self.should_stop:
                self._call_callback(self.on_complete_callback, True, "모든 액션이 성공적으로 실행되었습니다.")
            else:
                self._call_callback(self.on_complete_callback, False, "실행이 중단되었습니다.")
                
        except Exception as e:
            error_msg = f"실행 중 오류 발생: {str(e)}"
            self._call_callback(self.on_error_callback, error_msg)
        finally:
            self.is_running = False
            self.is_paused = False
            self.should_stop = False
            self.current_action_index = 0
    
    def _execute_action(self, action: Dict) -> bool:
        """
        개별 액션 실행
        
        Args:
            action: 실행할 액션
        
        Returns:
            성공 여부
        """
        try:
            action_type = action.get('action_type', '')
            parameters = action.get('parameters', {})
            
            # 기본 지연 시간
            default_delay = config.get_execution_delay()
            
            if action_type == 'mouse_move':
                return self._execute_mouse_move(parameters)
            elif action_type == 'mouse_click':
                return self._execute_mouse_click(parameters)
            elif action_type == 'keyboard_type':
                return self._execute_keyboard_type(parameters)
            elif action_type == 'delay':
                return self._execute_delay(parameters)
            elif action_type == 'clipboard_copy':
                return self._execute_clipboard_copy(parameters)
            elif action_type == 'clipboard_paste':
                return self._execute_clipboard_paste(parameters)
            elif action_type == 'key_combination':
                return self._execute_key_combination(parameters)
            else:
                print(f"알 수 없는 액션 타입: {action_type}")
                return False
                
        except Exception as e:
            print(f"액션 실행 오류: {str(e)}")
            return False
    
    def _execute_mouse_move(self, parameters: Dict) -> bool:
        """마우스 이동 실행"""
        try:
            x = parameters.get('x', 0)
            y = parameters.get('y', 0)
            duration = parameters.get('duration', 0.5)
            
            pyautogui.moveTo(x, y, duration=duration)
            return True
        except Exception as e:
            print(f"마우스 이동 오류: {str(e)}")
            return False
    
    def _execute_mouse_click(self, parameters: Dict) -> bool:
        """마우스 클릭 실행"""
        try:
            x = parameters.get('x', 0)
            y = parameters.get('y', 0)
            button = parameters.get('button', 'left')
            clicks = parameters.get('clicks', 1)
            
            pyautogui.click(x, y, clicks=clicks, button=button)
            return True
        except Exception as e:
            print(f"마우스 클릭 오류: {str(e)}")
            return False
    
    def _execute_keyboard_type(self, parameters: Dict) -> bool:
        """키보드 입력 실행"""
        try:
            text = parameters.get('text', '')
            interval = parameters.get('interval', 0.1)
            
            pyautogui.write(text, interval=interval)
            return True
        except Exception as e:
            print(f"키보드 입력 오류: {str(e)}")
            return False
    
    def _execute_delay(self, parameters: Dict) -> bool:
        """지연 시간 실행"""
        try:
            seconds = parameters.get('seconds', 1.0)
            time.sleep(seconds)
            return True
        except Exception as e:
            print(f"지연 시간 오류: {str(e)}")
            return False
    
    def _execute_clipboard_copy(self, parameters: Dict) -> bool:
        """클립보드 복사 실행"""
        try:
            text = parameters.get('text', '')
            pyperclip.copy(text)
            return True
        except Exception as e:
            print(f"클립보드 복사 오류: {str(e)}")
            return False
    
    def _execute_clipboard_paste(self, parameters: Dict) -> bool:
        """클립보드 붙여넣기 실행"""
        try:
            method = parameters.get('method', 'Ctrl+V')
            
            if method == 'Ctrl+V':
                pyautogui.hotkey('ctrl', 'v')
            elif method == '마우스 우클릭':
                # 현재 마우스 위치에서 우클릭 후 붙여넣기
                pyautogui.rightClick()
                time.sleep(0.1)
                pyautogui.press('v')
            
            return True
        except Exception as e:
            print(f"클립보드 붙여넣기 오류: {str(e)}")
            return False
    
    def _execute_key_combination(self, parameters: Dict) -> bool:
        """키 조합 실행"""
        try:
            keys = parameters.get('keys', '')
            
            # 키 조합 파싱 (예: "ctrl+c" -> ['ctrl', 'c'])
            key_list = keys.split('+')
            pyautogui.hotkey(*key_list)
            
            return True
        except Exception as e:
            print(f"키 조합 오류: {str(e)}")
            return False
    
    def stop_execution(self):
        """실행 중지"""
        self.should_stop = True
        self.is_paused = False
    
    def pause_execution(self):
        """실행 일시정지"""
        if self.is_running:
            self.is_paused = True
    
    def resume_execution(self):
        """실행 재개"""
        self.is_paused = False
    
    def _emergency_stop(self, e):
        """긴급 중지 (ESC 키)"""
        if self.is_running:
            self.stop_execution()
            print("ESC 키로 실행이 중단되었습니다.")
    
    def _call_callback(self, callback: Optional[Callable], *args):
        """콜백 함수 호출"""
        if callback:
            try:
                callback(*args)
            except Exception as e:
                print(f"콜백 호출 오류: {str(e)}")
    
    def get_execution_status(self) -> Dict:
        """실행 상태 반환"""
        return {
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'current_action_index': self.current_action_index,
            'should_stop': self.should_stop
        }
    
    def execute_single_action(self, action: Dict) -> bool:
        """
        단일 액션 실행 (테스트용)
        
        Args:
            action: 실행할 액션
        
        Returns:
            성공 여부
        """
        return self._execute_action(action)
    
    def get_mouse_position(self) -> tuple:
        """현재 마우스 위치 반환"""
        return pyautogui.position()
    
    def get_screen_size(self) -> tuple:
        """화면 크기 반환"""
        return pyautogui.size() 