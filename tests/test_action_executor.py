"""
ActionExecutor 테스트
액션 디스패치, 에러 처리, 실행 제어 로직 테스트
pyautogui, pyperclip, pynput을 모킹하여 GUI 없이 실행
"""
import pytest
import sys
import os
import time
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# pyautogui 등 GUI 의존 모듈을 import 전에 sys.modules에 모킹
_mock_pyautogui = MagicMock()
_mock_pyautogui.FAILSAFE = True
_mock_pyautogui.PAUSE = 0.1
_mock_pyautogui.position.return_value = (500, 500)
_mock_pyautogui.size.return_value = (1920, 1080)

_mock_pyperclip = MagicMock()
_mock_pyperclip.paste.return_value = ''

_mock_pynput_keyboard = MagicMock()

sys.modules.setdefault('pyautogui', _mock_pyautogui)
sys.modules.setdefault('pyperclip', _mock_pyperclip)
sys.modules.setdefault('pynput', MagicMock())
sys.modules.setdefault('pynput.keyboard', _mock_pynput_keyboard)
sys.modules.setdefault('cv2', MagicMock())
sys.modules.setdefault('PIL', MagicMock())
sys.modules.setdefault('PIL.Image', MagicMock())

# 모듈 import - 위의 mock들을 사용하게 됨
import src.core.action_executor as ae_module
from src.core.action_executor import ActionExecutor


@pytest.fixture
def executor():
    """모킹된 의존성으로 ActionExecutor 생성"""
    with patch.object(ae_module, 'ImageRecognizer', MagicMock()), \
         patch.object(ae_module, 'DataConnector', MagicMock()), \
         patch.object(ae_module, 'DataManager', MagicMock()), \
         patch.object(ae_module, 'logger', MagicMock()):
        ex = ActionExecutor()
        yield ex


@pytest.fixture
def mock_pag():
    """pyautogui mock 접근 및 리셋"""
    # ae_module이 참조하는 pyautogui를 직접 가져옴
    mock = ae_module.pyautogui
    mock.reset_mock()
    mock.FAILSAFE = True
    mock.PAUSE = 0.1
    return mock


@pytest.fixture
def mock_clip():
    """pyperclip mock 접근 및 리셋"""
    mock = ae_module.pyperclip
    mock.reset_mock()
    mock.paste.return_value = ''
    return mock


class TestActionDispatch:
    """액션 디스패치 테스트 - 각 action_type이 올바른 메서드 호출"""

    @pytest.mark.parametrize("action_type,method_name", [
        ('mouse_move', '_execute_mouse_move'),
        ('mouse_click', '_execute_mouse_click'),
        ('keyboard_type', '_execute_keyboard_type'),
        ('delay', '_execute_delay'),
        ('clipboard_copy', '_execute_clipboard_copy'),
        ('clipboard_paste', '_execute_clipboard_paste'),
        ('key_combination', '_execute_key_combination'),
        ('key_press', '_execute_key_press'),
        ('image_click', '_execute_image_click'),
        ('wait_for_image', '_execute_wait_for_image'),
        ('find_image', '_execute_find_image'),
        ('excel_load_data', '_execute_excel_load_data'),
    ])
    def test_dispatch_routes_correctly(self, executor, action_type, method_name):
        """각 action_type이 올바른 내부 메서드로 라우팅"""
        with patch.object(executor, method_name, return_value=True) as mock_method:
            action = {'action_type': action_type, 'parameters': {}}
            result = executor._execute_action(action)
            mock_method.assert_called_once()
            assert result is True

    def test_unknown_action_type_returns_false(self, executor):
        """알 수 없는 action_type은 False 반환"""
        action = {'action_type': 'nonexistent_type', 'parameters': {}}
        result = executor._execute_action(action)
        assert result is False


class TestMouseActions:
    """마우스 액션 테스트"""

    def test_mouse_move(self, executor, mock_pag):
        """마우스 이동"""
        result = executor._execute_mouse_move({'x': 100, 'y': 200, 'duration': 0.3})
        mock_pag.moveTo.assert_called_once_with(100, 200, duration=0.3)
        assert result is True

    def test_mouse_click(self, executor, mock_pag):
        """마우스 클릭"""
        result = executor._execute_mouse_click({'x': 100, 'y': 200, 'button': 'left', 'clicks': 1})
        mock_pag.click.assert_called_once_with(100, 200, clicks=1, button='left')
        assert result is True

    def test_mouse_move_exception(self, executor, mock_pag):
        """마우스 이동 중 예외 발생 시 False"""
        mock_pag.moveTo.side_effect = Exception("test error")
        result = executor._execute_mouse_move({'x': 0, 'y': 0})
        assert result is False
        mock_pag.moveTo.side_effect = None


class TestKeyboardActions:
    """키보드 액션 테스트"""

    def test_key_press(self, executor, mock_pag):
        """단일 키 입력"""
        result = executor._execute_key_press({'key': 'enter', 'count': 3})
        assert mock_pag.press.call_count == 3
        assert result is True

    def test_key_press_empty_key(self, executor):
        """빈 키 입력은 False"""
        result = executor._execute_key_press({'key': '', 'count': 1})
        assert result is False

    def test_key_combination(self, executor, mock_pag):
        """키 조합"""
        result = executor._execute_key_combination({'keys': 'ctrl+c'})
        mock_pag.hotkey.assert_called_once_with('ctrl', 'c')
        assert result is True


class TestDelayAction:
    """지연 액션 테스트"""

    def test_delay(self, executor):
        """지연 시간 실행"""
        with patch('time.sleep') as mock_sleep:
            result = executor._execute_delay({'seconds': 2.0})
            mock_sleep.assert_called_once_with(2.0)
            assert result is True


class TestClipboardActions:
    """클립보드 액션 테스트"""

    def test_clipboard_copy(self, executor, mock_clip):
        """클립보드 복사"""
        result = executor._execute_clipboard_copy({'text': '복사할 텍스트'})
        mock_clip.copy.assert_called_once_with('복사할 텍스트')
        assert result is True

    def test_clipboard_paste(self, executor, mock_pag):
        """클립보드 붙여넣기"""
        result = executor._execute_clipboard_paste({'method': 'Ctrl+V'})
        mock_pag.hotkey.assert_called_once_with('ctrl', 'v')
        assert result is True


class TestErrorHandling:
    """에러 처리 전략 테스트"""

    def test_error_handling_ignore_continues(self, executor):
        """on_error='ignore' → 실패해도 계속 진행"""
        action = {
            'action_type': 'mouse_click',
            'description': '실패 액션',
            'id': 1,
            'parameters': {},
            'error_handling': {
                'retry_count': 0,
                'retry_delay': 0,
                'timeout': None,
                'on_error': 'ignore',
            }
        }
        with patch.object(executor, '_execute_action', return_value=False):
            success, should_continue = executor._execute_action_with_error_handling(action)
            assert success is False
            assert should_continue is True

    def test_error_handling_stop_halts(self, executor):
        """on_error='stop' → 실패 시 중단"""
        action = {
            'action_type': 'mouse_click',
            'description': '실패 액션',
            'id': 1,
            'parameters': {},
            'error_handling': {
                'retry_count': 0,
                'retry_delay': 0,
                'timeout': None,
                'on_error': 'stop',
            }
        }
        with patch.object(executor, '_execute_action', return_value=False):
            success, should_continue = executor._execute_action_with_error_handling(action)
            assert success is False
            assert should_continue is False

    def test_error_handling_retry(self, executor):
        """retry 설정 시 재시도 후 성공"""
        action = {
            'action_type': 'mouse_click',
            'description': '재시도 액션',
            'id': 1,
            'parameters': {},
            'error_handling': {
                'retry_count': 2,
                'retry_delay': 0,
                'timeout': None,
                'on_error': 'retry',
            }
        }
        with patch.object(executor, '_execute_action', side_effect=[False, False, True]):
            success, should_continue = executor._execute_action_with_error_handling(action)
            assert success is True
            assert should_continue is True

    def test_error_handling_retry_all_fail(self, executor):
        """retry 설정이지만 모두 실패"""
        action = {
            'action_type': 'mouse_click',
            'description': '재시도 실패',
            'id': 1,
            'parameters': {},
            'error_handling': {
                'retry_count': 1,
                'retry_delay': 0,
                'timeout': None,
                'on_error': 'retry',
            }
        }
        with patch.object(executor, '_execute_action', return_value=False):
            success, should_continue = executor._execute_action_with_error_handling(action)
            assert success is False
            assert should_continue is False


class TestExecutionControl:
    """실행 제어 테스트"""

    def test_stop_execution(self, executor):
        executor.is_running = True
        executor.is_paused = True
        executor.stop_execution()
        assert executor.should_stop is True
        assert executor.is_paused is False

    def test_pause_execution(self, executor):
        executor.is_running = True
        executor.pause_execution()
        assert executor.is_paused is True

    def test_pause_when_not_running(self, executor):
        executor.is_running = False
        executor.pause_execution()
        assert executor.is_paused is False

    def test_resume_execution(self, executor):
        executor.is_paused = True
        executor.resume_execution()
        assert executor.is_paused is False


class TestExecutionStatus:
    """실행 상태 보고 테스트"""

    def test_status_structure(self, executor):
        status = executor.get_execution_status()
        required_keys = {
            'is_running', 'is_paused', 'current_action_index',
            'total_actions', 'should_stop', 'progress_percent',
            'elapsed_time', 'estimated_remaining_time', 'average_action_time'
        }
        assert required_keys.issubset(status.keys())

    def test_status_idle(self, executor):
        status = executor.get_execution_status()
        assert status['is_running'] is False
        assert status['progress_percent'] == 0.0

    def test_status_running(self, executor):
        executor.is_running = True
        executor.total_actions = 10
        executor.current_action_index = 4
        executor.start_time = time.time() - 5

        status = executor.get_execution_status()
        assert status['is_running'] is True
        assert status['progress_percent'] == 50.0
        assert status['elapsed_time'] >= 4.9

    def test_execute_single_action(self, executor):
        with patch.object(executor, '_execute_action', return_value=True) as mock:
            result = executor.execute_single_action({'action_type': 'delay', 'parameters': {'seconds': 0}})
            mock.assert_called_once()
            assert result is True
