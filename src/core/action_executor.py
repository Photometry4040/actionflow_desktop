"""
액션 실행 엔진
마우스/키보드 제어 및 액션 실행을 담당하는 핵심 모듈
"""
import time
import threading
from typing import Dict, List, Optional, Callable
import pyautogui
import pyperclip
from pynput import keyboard

from ..models.project import Project
from ..utils.config import config
from ..utils.logger import get_logger
from .image_recognizer import ImageRecognizer
from .data_connector import DataConnector

# 로거 초기화
logger = get_logger(__name__)


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

        # 진행 상태 추적 변수
        self.total_actions = 0
        self.start_time = None
        self.action_start_times = []  # 각 액션 실행 시작 시간

        # 이미지 인식 및 데이터 연동 모듈 초기화
        self.image_recognizer = ImageRecognizer()
        self.data_connector = DataConnector()

        # Excel 루프 처리를 위한 결과 저장 리스트
        self.excel_results = []

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
            logger.info(f"프로젝트 실행 시작: {project.name} (ID: {project.id})")
            self.is_running = True
            self.is_paused = False
            self.should_stop = False
            self.current_action_index = 0

            actions = project.actions
            total_actions = len(actions)
            self.total_actions = total_actions
            self.start_time = time.time()
            self.action_start_times = []

            logger.info(f"총 {total_actions}개의 액션 실행 예정")

            if total_actions == 0:
                logger.warning("실행할 액션이 없습니다")
                self._call_callback(self.on_complete_callback)
                return

            # 액션 순서대로 정렬
            sorted_actions = sorted(actions, key=lambda x: x.get('order_index', 0))

            for i, action in enumerate(sorted_actions):
                if self.should_stop:
                    logger.info("사용자 요청으로 실행 중단")
                    break

                # 일시정지 확인
                while self.is_paused and not self.should_stop:
                    time.sleep(0.1)

                if self.should_stop:
                    logger.info("사용자 요청으로 실행 중단")
                    break

                # 현재 액션 인덱스 업데이트
                self.current_action_index = i

                # 액션 시작 시간 기록
                action_start_time = time.time()
                self.action_start_times.append(action_start_time)

                # 진행 상황 콜백 호출
                action_description = action.get('description', f'액션 {i+1}')
                logger.debug(f"액션 실행 중 ({i+1}/{total_actions}): {action_description}")
                self._call_callback(self.on_progress_callback, i+1, total_actions, action_description)

                # 액션 실행
                try:
                    success = self._execute_action(action)
                    if not success:
                        error_msg = f"액션 실행 실패: {action.get('description', '알 수 없는 액션')}"
                        logger.error(error_msg)
                        self._call_callback(self.on_error_callback, error_msg)
                        return
                except Exception as action_error:
                    error_msg = f"액션 실행 중 예외 발생: {action.get('description', '알 수 없는 액션')} - {str(action_error)}"
                    logger.error(error_msg, exc_info=True)
                    self._call_callback(self.on_error_callback, error_msg)
                    return

            # 완료 콜백 호출
            if not self.should_stop:
                logger.info("프로젝트 실행 완료")
                self._call_callback(self.on_complete_callback, True, "모든 액션이 성공적으로 실행되었습니다.")
            else:
                logger.warning("프로젝트 실행 중단됨")
                self._call_callback(self.on_complete_callback, False, "실행이 중단되었습니다.")

        except Exception as e:
            error_msg = f"실행 중 오류 발생: {str(e)}"
            logger.critical(error_msg, exc_info=True)
            self._call_callback(self.on_error_callback, error_msg)
        finally:
            logger.debug("실행 스레드 종료")
            self.is_running = False
            self.is_paused = False
            self.should_stop = False
            self.current_action_index = 0
            self.total_actions = 0
            self.start_time = None
            self.action_start_times = []
    
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
            elif action_type == 'image_click':
                return self._execute_image_click(parameters)
            elif action_type == 'wait_for_image':
                return self._execute_wait_for_image(parameters)
            elif action_type == 'find_image':
                return self._execute_find_image(parameters)
            elif action_type == 'wait_for_any_image':
                return self._execute_wait_for_any_image(parameters)
            elif action_type == 'excel_load_data':
                return self._execute_excel_load_data(parameters)
            elif action_type == 'excel_loop_start':
                return self._execute_excel_loop_start(parameters)
            elif action_type == 'excel_loop_end':
                return self._execute_excel_loop_end(parameters)
            elif action_type == 'excel_get_cell':
                return self._execute_excel_get_cell(parameters)
            elif action_type == 'excel_save_results':
                return self._execute_excel_save_results(parameters)
            else:
                logger.warning(f"알 수 없는 액션 타입: {action_type}")
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

            logger.debug(f"마우스 이동: ({x}, {y}), 지속시간: {duration}초")
            pyautogui.moveTo(x, y, duration=duration)
            return True
        except Exception as e:
            logger.error(f"마우스 이동 오류: {str(e)}", exc_info=True)
            return False

    def _execute_mouse_click(self, parameters: Dict) -> bool:
        """마우스 클릭 실행"""
        try:
            x = parameters.get('x', 0)
            y = parameters.get('y', 0)
            button = parameters.get('button', 'left')
            clicks = parameters.get('clicks', 1)

            logger.debug(f"마우스 클릭: ({x}, {y}), 버튼: {button}, 클릭 수: {clicks}")
            pyautogui.click(x, y, clicks=clicks, button=button)
            return True
        except Exception as e:
            logger.error(f"마우스 클릭 오류: {str(e)}", exc_info=True)
            return False
    
    def _execute_keyboard_type(self, parameters: Dict) -> bool:
        """키보드 입력 실행"""
        text = parameters.get('text', '')
        interval = parameters.get('interval', 0.1)

        # 텍스트가 비어있지 않은지 확인
        if not text:
            logger.warning("키보드 입력 오류: 입력할 텍스트가 없습니다")
            return False

        logger.debug(f"키보드 입력 시도: '{text[:20]}...' (길이: {len(text)})")

        try:
            
            # 방법 1: 클립보드를 통한 입력 (가장 안정적)
            try:
                logger.debug("방법 1: 클립보드를 통한 입력 시도")
                # 현재 클립보드 내용 저장
                original_clipboard = pyperclip.paste()

                # 텍스트를 클립보드에 복사
                pyperclip.copy(text)
                time.sleep(0.1)

                # Ctrl+V로 붙여넣기 (fail-safe 방지를 위해 안전한 방법 사용)
                try:
                    pyautogui.hotkey('ctrl', 'v')
                except Exception as hotkey_error:
                    logger.debug(f"pyautogui hotkey 실패, pynput으로 대체: {str(hotkey_error)}")
                    # fail-safe 발생 시 pynput 사용
                    controller = keyboard.Controller()
                    controller.press(keyboard.Key.ctrl)
                    controller.press('v')
                    controller.release('v')
                    controller.release(keyboard.Key.ctrl)

                time.sleep(interval)

                # 원래 클립보드 내용 복원
                pyperclip.copy(original_clipboard)

                logger.info(f"키보드 입력 성공 (클립보드 방식): {len(text)}자")
                return True
            except Exception as clipboard_error:
                logger.warning(f"클립보드 방식 실패, 직접 입력으로 대체: {str(clipboard_error)}")
                
                # 방법 2: pynput을 사용한 직접 입력
                try:
                    logger.debug("방법 2: pynput을 사용한 직접 입력 시도")
                    controller = keyboard.Controller()
                    failed_chars = []

                    for char in text:
                        try:
                            controller.type(char)
                            time.sleep(interval)
                        except Exception as char_error:
                            logger.debug(f"문자 '{char}' 입력 오류: {str(char_error)}")
                            failed_chars.append(char)
                            # 특수 문자의 경우 pyautogui로 대체
                            try:
                                pyautogui.press(char)
                                time.sleep(interval)
                            except Exception as press_error:
                                logger.warning(f"문자 '{char}'를 입력할 수 없습니다: {str(press_error)}")
                                continue

                    if failed_chars:
                        logger.warning(f"일부 문자 입력 실패: {failed_chars[:10]}")

                    logger.info(f"키보드 입력 성공 (pynput 방식): {len(text) - len(failed_chars)}/{len(text)}자")
                    return True

                except Exception as pynput_error:
                    logger.warning(f"pynput 오류, pyautogui로 대체: {str(pynput_error)}")

                    # 방법 3: pyautogui로 대체 (fail-safe 비활성화)
                    try:
                        logger.debug("방법 3: pyautogui 직접 입력 시도 (fail-safe 임시 비활성화)")
                        # 임시로 fail-safe 비활성화
                        original_failsafe = pyautogui.FAILSAFE
                        pyautogui.FAILSAFE = False

                        failed_chars = []
                        for char in text:
                            try:
                                pyautogui.write(char, interval=0)
                                time.sleep(interval)
                            except Exception as char_error:
                                logger.debug(f"문자 '{char}' 입력 오류: {str(char_error)}")
                                try:
                                    pyautogui.press(char)
                                    time.sleep(interval)
                                except Exception as press_error:
                                    logger.warning(f"문자 '{char}'를 입력할 수 없습니다: {str(press_error)}")
                                    failed_chars.append(char)
                                    continue

                        # fail-safe 복원
                        pyautogui.FAILSAFE = original_failsafe

                        if failed_chars:
                            logger.error(f"입력 실패한 문자: {failed_chars[:10]}")

                        success_count = len(text) - len(failed_chars)
                        if success_count > 0:
                            logger.info(f"키보드 입력 부분 성공 (pyautogui 방식): {success_count}/{len(text)}자")
                            return True
                        else:
                            logger.error("키보드 입력 완전 실패")
                            return False

                    except Exception as e:
                        logger.error(f"pyautogui 방식도 실패: {str(e)}", exc_info=True)
                        return False

            return True
        except Exception as e:
            logger.error(f"키보드 입력 오류: {str(e)}", exc_info=True)
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
    
    def _execute_image_click(self, parameters: Dict) -> bool:
        """이미지 클릭 실행"""
        try:
            template_path = parameters.get('template_path', '')
            confidence = parameters.get('confidence', 0.8)
            timeout = parameters.get('timeout', 0)
            button = parameters.get('button', 'left')
            clicks = parameters.get('clicks', 1)

            logger.debug(f"이미지 클릭 시도: {template_path}, 신뢰도: {confidence}")

            success = self.image_recognizer.click_image(
                template_path=template_path,
                confidence=confidence,
                timeout=timeout,
                button=button,
                clicks=clicks
            )

            if success:
                logger.info(f"이미지 클릭 성공: {template_path}")
            else:
                logger.warning(f"이미지를 찾지 못해 클릭 실패: {template_path}")

            return success
        except Exception as e:
            logger.error(f"이미지 클릭 오류: {str(e)}", exc_info=True)
            return False

    def _execute_wait_for_image(self, parameters: Dict) -> bool:
        """이미지 대기 실행"""
        try:
            template_path = parameters.get('template_path', '')
            confidence = parameters.get('confidence', 0.8)
            timeout = parameters.get('timeout', 10.0)

            logger.debug(f"이미지 대기 시작: {template_path}, 타임아웃: {timeout}초")

            found, location = self.image_recognizer.wait_for_image(
                template_path=template_path,
                confidence=confidence,
                timeout=timeout
            )

            if found:
                logger.info(f"이미지 발견: {template_path} at {location}")
            else:
                logger.warning(f"이미지 대기 타임아웃: {template_path}")

            return found
        except Exception as e:
            logger.error(f"이미지 대기 오류: {str(e)}", exc_info=True)
            return False

    def _execute_find_image(self, parameters: Dict) -> bool:
        """이미지 찾기 실행"""
        try:
            template_path = parameters.get('template_path', '')
            confidence = parameters.get('confidence', 0.8)

            logger.debug(f"이미지 찾기: {template_path}")

            found, location = self.image_recognizer.find_on_screen(
                template_path=template_path,
                confidence=confidence
            )

            if found:
                logger.info(f"이미지 발견: {template_path} at {location}")
            else:
                logger.debug(f"이미지를 찾지 못함: {template_path}")

            return found
        except Exception as e:
            logger.error(f"이미지 찾기 오류: {str(e)}", exc_info=True)
            return False

    def _execute_wait_for_any_image(self, parameters: Dict) -> bool:
        """여러 이미지 중 하나 대기 실행"""
        try:
            template_paths = parameters.get('template_paths', [])
            confidence = parameters.get('confidence', 0.8)
            timeout = parameters.get('timeout', 10.0)

            logger.debug(f"여러 이미지 중 하나 대기: {len(template_paths)}개")

            start_time = time.time()
            while time.time() - start_time < timeout:
                found, index, location = self.image_recognizer.find_any(
                    template_paths=template_paths,
                    confidence=confidence
                )

                if found:
                    logger.info(f"이미지 발견: {template_paths[index]} at {location}")
                    return True

                time.sleep(0.5)

            logger.warning("여러 이미지 중 하나도 찾지 못함 (타임아웃)")
            return False
        except Exception as e:
            logger.error(f"여러 이미지 대기 오류: {str(e)}", exc_info=True)
            return False

    def _execute_excel_load_data(self, parameters: Dict) -> bool:
        """Excel/CSV 데이터 로드 실행"""
        try:
            file_path = parameters.get('file_path', '')
            sheet_name = parameters.get('sheet_name', None)
            encoding = parameters.get('encoding', 'utf-8')

            logger.debug(f"Excel/CSV 데이터 로드: {file_path}")

            success = self.data_connector.load_data(
                file_path=file_path,
                sheet_name=sheet_name,
                encoding=encoding
            )

            if success:
                info = self.data_connector.get_data_info()
                logger.info(f"데이터 로드 성공: {info['rows']}행, 컬럼: {info['columns']}")
            else:
                logger.error(f"데이터 로드 실패: {file_path}")

            return success
        except Exception as e:
            logger.error(f"Excel 데이터 로드 오류: {str(e)}", exc_info=True)
            return False

    def _execute_excel_loop_start(self, parameters: Dict) -> bool:
        """Excel 루프 시작 실행"""
        try:
            filter_condition = parameters.get('filter_condition', None)

            logger.debug("Excel 루프 시작")

            success = self.data_connector.start_loop(filter_condition=filter_condition)

            if success:
                total_rows = self.data_connector.get_total_rows()
                logger.info(f"Excel 루프 시작: {total_rows}행 처리 예정")
                # 결과 저장 리스트 초기화
                self.excel_results = []
            else:
                logger.error("Excel 루프 시작 실패")

            return success
        except Exception as e:
            logger.error(f"Excel 루프 시작 오류: {str(e)}", exc_info=True)
            return False

    def _execute_excel_loop_end(self, parameters: Dict) -> bool:
        """Excel 루프 종료 실행"""
        try:
            logger.debug("Excel 루프 종료")

            success = self.data_connector.end_loop()

            if success:
                logger.info("Excel 루프 종료 성공")

            return success
        except Exception as e:
            logger.error(f"Excel 루프 종료 오류: {str(e)}", exc_info=True)
            return False

    def _execute_excel_get_cell(self, parameters: Dict) -> bool:
        """Excel 셀 값 가져오기 실행"""
        try:
            column_name = parameters.get('column_name', '')
            variable_name = parameters.get('variable_name', '')
            default_value = parameters.get('default_value', None)

            logger.debug(f"Excel 셀 값 가져오기: {column_name}")

            value = self.data_connector.get_column_value(
                column_name=column_name,
                default=default_value
            )

            if value is not None:
                logger.info(f"셀 값 가져오기 성공: {column_name} = {value}")
                # 변수에 저장 (향후 변수 시스템 구현 시 사용)
                # self.variables[variable_name] = value
            else:
                logger.warning(f"셀 값을 가져오지 못함: {column_name}")

            return True
        except Exception as e:
            logger.error(f"Excel 셀 값 가져오기 오류: {str(e)}", exc_info=True)
            return False

    def _execute_excel_save_results(self, parameters: Dict) -> bool:
        """Excel/CSV 결과 저장 실행"""
        try:
            output_path = parameters.get('output_path', '')
            append = parameters.get('append', False)

            logger.debug(f"Excel/CSV 결과 저장: {output_path}")

            success = self.data_connector.save_data(
                data=self.excel_results,
                output_path=output_path,
                append=append
            )

            if success:
                logger.info(f"결과 저장 성공: {len(self.excel_results)}행 저장됨")
                # 결과 리스트 초기화
                self.excel_results = []
            else:
                logger.error(f"결과 저장 실패: {output_path}")

            return success
        except Exception as e:
            logger.error(f"Excel 결과 저장 오류: {str(e)}", exc_info=True)
            return False

    def _call_callback(self, callback: Optional[Callable], *args):
        """콜백 함수 호출"""
        if callback:
            try:
                callback(*args)
            except Exception as e:
                print(f"콜백 호출 오류: {str(e)}")
    
    def get_execution_status(self) -> Dict:
        """
        실행 상태 반환

        Returns:
            실행 상태 정보 딕셔너리:
            {
                'is_running': bool,  # 실행 중 여부
                'is_paused': bool,  # 일시정지 여부
                'current_action_index': int,  # 현재 액션 인덱스
                'total_actions': int,  # 총 액션 수
                'should_stop': bool,  # 중지 요청 여부
                'progress_percent': float,  # 진행률 (0-100)
                'elapsed_time': float,  # 경과 시간 (초)
                'estimated_remaining_time': float,  # 예상 남은 시간 (초)
                'average_action_time': float  # 액션당 평균 실행 시간 (초)
            }
        """
        status = {
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'current_action_index': self.current_action_index,
            'total_actions': self.total_actions,
            'should_stop': self.should_stop,
            'progress_percent': 0.0,
            'elapsed_time': 0.0,
            'estimated_remaining_time': 0.0,
            'average_action_time': 0.0
        }

        # 진행률 계산 (현재 실행 중인 액션 포함)
        if self.total_actions > 0:
            if self.is_running:
                # current_action_index는 0부터 시작하므로 +1 필요
                # 예: 10개 중 첫 번째 액션 실행 시 (0 + 1) / 10 = 10%
                status['progress_percent'] = ((self.current_action_index + 1) / self.total_actions) * 100
            else:
                # 실행이 중지된 경우 마지막 완료된 액션까지만 계산
                status['progress_percent'] = (self.current_action_index / self.total_actions) * 100

        # 경과 시간 계산
        if self.start_time is not None:
            status['elapsed_time'] = time.time() - self.start_time

        # 평균 액션 실행 시간 계산
        if len(self.action_start_times) > 1:
            # 각 액션 간 시간 차이 계산
            time_diffs = []
            for i in range(1, len(self.action_start_times)):
                time_diffs.append(self.action_start_times[i] - self.action_start_times[i-1])

            if time_diffs:
                status['average_action_time'] = sum(time_diffs) / len(time_diffs)

                # 예상 남은 시간 계산
                remaining_actions = self.total_actions - self.current_action_index - 1
                if remaining_actions > 0:
                    status['estimated_remaining_time'] = status['average_action_time'] * remaining_actions

        return status
    
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