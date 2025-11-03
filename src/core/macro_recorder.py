"""
매크로 녹화 기능
마우스/키보드 이벤트를 실시간으로 녹화하여 액션으로 변환
"""
import time
import threading
from typing import List, Dict, Optional, Callable
from pynput import mouse, keyboard

from ..utils.data_manager import DataManager
from ..utils.logger import get_logger

# 로거 초기화
logger = get_logger(__name__)


class MacroRecorder:
    """매크로 녹화 클래스"""
    
    def __init__(self):
        """초기화"""
        self.is_recording = False
        self.recorded_actions = []
        self.start_time = None
        self.mouse_listener = None
        self.keyboard_listener = None
        self.data_manager = DataManager()
        
        # 마우스 상태
        self.last_mouse_position = None
        self.last_mouse_click_time = 0
        
        # 키보드 상태
        self.current_keys = set()
        self.last_key_time = 0
        
        # 콜백 함수들
        self.on_action_recorded = None
        self.on_recording_stopped = None
    
    def start_recording(self, on_action_recorded: Optional[Callable] = None,
                       on_recording_stopped: Optional[Callable] = None) -> bool:
        """
        녹화 시작

        Args:
            on_action_recorded: 액션 녹화 시 콜백
            on_recording_stopped: 녹화 중지 시 콜백

        Returns:
            성공 여부
        """
        if self.is_recording:
            logger.warning("이미 녹화 중입니다")
            return False

        logger.info("매크로 녹화 시작")
        self.is_recording = True
        self.recorded_actions = []
        self.start_time = time.time()
        self.on_action_recorded = on_action_recorded
        self.on_recording_stopped = on_recording_stopped

        try:
            # 마우스 리스너 시작
            self.mouse_listener = mouse.Listener(
                on_move=self._on_mouse_move,
                on_click=self._on_mouse_click,
                on_scroll=self._on_mouse_scroll
            )
            self.mouse_listener.start()
            logger.debug("마우스 리스너 시작됨")

            # 키보드 리스너 시작
            self.keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.keyboard_listener.start()
            logger.debug("키보드 리스너 시작됨")

            return True
        except Exception as e:
            logger.error(f"녹화 시작 오류: {str(e)}", exc_info=True)
            self.is_recording = False
            return False
    
    def stop_recording(self) -> List[Dict]:
        """
        녹화 중지

        Returns:
            녹화된 액션 목록
        """
        if not self.is_recording:
            logger.warning("녹화 중이 아닙니다")
            return []

        logger.info(f"매크로 녹화 중지 - 총 {len(self.recorded_actions)}개의 액션 녹화됨")
        self.is_recording = False

        try:
            # 리스너 중지
            if self.mouse_listener:
                self.mouse_listener.stop()
                self.mouse_listener = None
                logger.debug("마우스 리스너 중지됨")

            if self.keyboard_listener:
                self.keyboard_listener.stop()
                self.keyboard_listener = None
                logger.debug("키보드 리스너 중지됨")

            # 녹화 중지 콜백 호출
            if self.on_recording_stopped:
                self.on_recording_stopped(self.recorded_actions)

            return self.recorded_actions.copy()
        except Exception as e:
            logger.error(f"녹화 중지 오류: {str(e)}", exc_info=True)
            return self.recorded_actions.copy()
    
    def _on_mouse_move(self, x, y):
        """마우스 이동 이벤트"""
        if not self.is_recording:
            return
        
        current_time = time.time()
        
        # 마우스 이동은 너무 자주 기록하지 않도록 제한
        if (self.last_mouse_position is None or 
            abs(x - self.last_mouse_position[0]) > 10 or 
            abs(y - self.last_mouse_position[1]) > 10 or
            current_time - self.last_mouse_click_time > 0.5):
            
            action = {
                'action_type': 'mouse_move',
                'description': f'마우스 이동 ({x}, {y})',
                'parameters': {
                    'x': x,
                    'y': y,
                    'duration': 0.5
                },
                'timestamp': current_time - self.start_time
            }
            
            self._add_action(action)
            self.last_mouse_position = (x, y)
    
    def _on_mouse_click(self, x, y, button, pressed):
        """마우스 클릭 이벤트"""
        if not self.is_recording:
            return
        
        current_time = time.time()
        self.last_mouse_click_time = current_time
        
        if pressed:
            # 클릭 버튼 매핑
            button_map = {
                mouse.Button.left: 'left',
                mouse.Button.right: 'right',
                mouse.Button.middle: 'middle'
            }
            
            button_name = button_map.get(button, 'left')
            
            action = {
                'action_type': 'mouse_click',
                'description': f'마우스 {button_name} 클릭 ({x}, {y})',
                'parameters': {
                    'x': x,
                    'y': y,
                    'button': button_name,
                    'clicks': 1
                },
                'timestamp': current_time - self.start_time
            }
            
            self._add_action(action)
    
    def _on_mouse_scroll(self, x, y, dx, dy):
        """마우스 스크롤 이벤트"""
        if not self.is_recording:
            return
        
        current_time = time.time()
        
        # 스크롤 방향에 따른 키 입력으로 변환
        if dy > 0:
            key = 'up'
        else:
            key = 'down'
        
        action = {
            'action_type': 'key_combination',
            'description': f'스크롤 {key}',
            'parameters': {
                'keys': key
            },
            'timestamp': current_time - self.start_time
        }
        
        self._add_action(action)
    
    def _on_key_press(self, key):
        """키보드 누름 이벤트"""
        if not self.is_recording:
            return
        
        current_time = time.time()
        
        try:
            # 특수 키 처리
            if hasattr(key, 'char'):
                # 일반 문자 키
                char = key.char
                if char:
                    # 연속된 문자 입력은 하나의 액션으로 묶기
                    if (current_time - self.last_key_time < 0.1 and 
                        self.recorded_actions and 
                        self.recorded_actions[-1]['action_type'] == 'keyboard_type'):
                        
                        # 기존 액션에 문자 추가
                        self.recorded_actions[-1]['parameters']['text'] += char
                        self.recorded_actions[-1]['description'] = f"키보드 입력: {self.recorded_actions[-1]['parameters']['text']}"
                    else:
                        action = {
                            'action_type': 'keyboard_type',
                            'description': f'키보드 입력: {char}',
                            'parameters': {
                                'text': char,
                                'interval': 0.1
                            },
                            'timestamp': current_time - self.start_time
                        }
                        self._add_action(action)
            else:
                # 특수 키
                key_name = str(key).replace('Key.', '')

                # 일반적인 키 조합 처리
                if key_name in ['ctrl', 'alt', 'shift', 'cmd']:
                    self.current_keys.add(key_name)
                else:
                    # 단일 특수 키 - Delete, Backspace 등은 key_press로 기록
                    common_keys = ['delete', 'backspace', 'enter', 'tab', 'esc', 'space',
                                   'home', 'end', 'page_up', 'page_down',
                                   'up', 'down', 'left', 'right', 'insert']

                    # F1-F12 키도 포함
                    for i in range(1, 13):
                        common_keys.append(f'f{i}')

                    if key_name in common_keys:
                        # key_press 타입으로 기록
                        action = {
                            'action_type': 'key_press',
                            'description': f'키 입력: {key_name}',
                            'parameters': {
                                'key': key_name,
                                'count': 1
                            },
                            'timestamp': current_time - self.start_time
                        }
                        self._add_action(action)
                    else:
                        # 기타 특수 키는 key_combination으로 기록
                        action = {
                            'action_type': 'key_combination',
                            'description': f'키 조합: {key_name}',
                            'parameters': {
                                'keys': key_name
                            },
                            'timestamp': current_time - self.start_time
                        }
                        self._add_action(action)
            
            self.last_key_time = current_time
            
        except AttributeError:
            pass
    
    def _on_key_release(self, key):
        """키보드 놓음 이벤트"""
        if not self.is_recording:
            return
        
        try:
            # 특수 키 처리
            if hasattr(key, 'char'):
                pass  # 일반 문자 키는 놓음 이벤트 무시
            else:
                key_name = str(key).replace('Key.', '')
                
                # 키 조합 처리
                if key_name in ['ctrl', 'alt', 'shift', 'cmd']:
                    if key_name in self.current_keys:
                        self.current_keys.remove(key_name)
                        
                        # 키 조합이 완성되면 액션으로 기록
                        if len(self.current_keys) > 0:
                            current_time = time.time()
                            keys_str = '+'.join(sorted(self.current_keys))
                            
                            action = {
                                'action_type': 'key_combination',
                                'description': f'키 조합: {keys_str}',
                                'parameters': {
                                    'keys': keys_str
                                },
                                'timestamp': current_time - self.start_time
                            }
                            self._add_action(action)
                            self.current_keys.clear()
        
        except AttributeError:
            pass
    
    def _add_action(self, action: Dict):
        """액션 추가"""
        # 중복 액션 필터링
        if self._should_filter_action(action):
            return
        
        # 액션 순서 인덱스 추가
        action['order_index'] = len(self.recorded_actions) + 1
        
        # 이전 액션과의 시간 간격 계산
        if self.recorded_actions:
            prev_timestamp = self.recorded_actions[-1].get('timestamp', 0)
            current_timestamp = action.get('timestamp', 0)
            time_interval = current_timestamp - prev_timestamp
            
            # 시간 간격이 일정 값 이상이면 지연 액션 추가
            if time_interval > 0.5:  # 0.5초 이상 간격이면 지연 액션 추가
                delay_action = {
                    'action_type': 'delay',
                    'description': f'지연 {time_interval:.2f}초',
                    'parameters': {
                        'seconds': time_interval
                    },
                    'timestamp': prev_timestamp + time_interval / 2,
                    'order_index': len(self.recorded_actions) + 1
                }
                self.recorded_actions.append(delay_action)
                action['order_index'] = len(self.recorded_actions) + 1
        
        self.recorded_actions.append(action)
        
        # 콜백 호출
        if self.on_action_recorded:
            self.on_action_recorded(action)
    
    def _should_filter_action(self, action: Dict) -> bool:
        """액션 필터링 (중복 제거)"""
        if not self.recorded_actions:
            return False
        
        last_action = self.recorded_actions[-1]
        
        # 같은 타입의 연속된 마우스 이동 필터링
        if (action['action_type'] == 'mouse_move' and 
            last_action['action_type'] == 'mouse_move'):
            return True
        
        # 같은 타입의 연속된 키보드 입력 필터링 (이미 위에서 처리됨)
        if (action['action_type'] == 'keyboard_type' and 
            last_action['action_type'] == 'keyboard_type'):
            return True
        
        return False
    
    def get_recording_status(self) -> Dict:
        """녹화 상태 반환"""
        return {
            'is_recording': self.is_recording,
            'action_count': len(self.recorded_actions),
            'recording_time': time.time() - self.start_time if self.start_time else 0
        }
    
    def clear_recording(self):
        """녹화 데이터 초기화"""
        self.recorded_actions = []
        self.start_time = None
    
    def save_recording_as_project(self, project_name: str, description: str = "") -> Optional[int]:
        """
        녹화된 액션을 프로젝트로 저장
        
        Args:
            project_name: 프로젝트명
            description: 프로젝트 설명
        
        Returns:
            생성된 프로젝트 ID
        """
        if not self.recorded_actions:
            return None
        
        try:
            # 새 프로젝트 생성
            project_id = self.data_manager.get_next_project_id()
            
            # 액션에 ID 추가
            for i, action in enumerate(self.recorded_actions):
                action['id'] = self.data_manager.get_next_action_id()
                action['order_index'] = i + 1
            
            # 프로젝트 데이터 생성
            project_data = {
                'id': project_id,
                'name': project_name,
                'description': description,
                'category': '매크로 녹화',
                'favorite': False,
                'created_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
                'updated_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
                'actions': self.recorded_actions
            }
            
            # 프로젝트 저장
            from ..models.project import Project
            project = Project.from_dict(project_data)
            self.data_manager.save_project(project)
            
            return project_id
            
        except Exception as e:
            print(f"프로젝트 저장 오류: {str(e)}")
            return None
    
    def get_action_summary(self) -> Dict:
        """액션 요약 정보 반환"""
        if not self.recorded_actions:
            return {}
        
        action_types = {}
        for action in self.recorded_actions:
            action_type = action['action_type']
            action_types[action_type] = action_types.get(action_type, 0) + 1
        
        return {
            'total_actions': len(self.recorded_actions),
            'action_types': action_types,
            'recording_duration': self.recorded_actions[-1]['timestamp'] if self.recorded_actions else 0
        } 