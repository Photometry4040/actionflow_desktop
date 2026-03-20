"""
A/B 비교 테스트
동일 기능의 두 변형을 병렬로 실행하여 올바른 동작을 검증하는 패턴
pytest.mark.parametrize를 활용하여 Variant A/B 비교
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# pyautogui 등 GUI 모듈 선행 모킹
_mock_pag = MagicMock()
_mock_pag.FAILSAFE = True
_mock_pag.PAUSE = 0.1
sys.modules.setdefault('pyautogui', _mock_pag)
sys.modules.setdefault('pyperclip', MagicMock())
sys.modules.setdefault('pynput', MagicMock())
sys.modules.setdefault('pynput.keyboard', MagicMock())
sys.modules.setdefault('cv2', MagicMock())
sys.modules.setdefault('PIL', MagicMock())
sys.modules.setdefault('PIL.Image', MagicMock())

from src.models.settings import Settings
from src.models.action import Action, ActionFactory
from src.models.project import Project


# ============================================================
# A/B 테스트 1: Settings 직렬화 견고성
# Variant A: 깨끗한 데이터로 from_dict
# Variant B: extra 키 포함 데이터로 from_dict
# 결과: 동일한 Settings 객체
# ============================================================

class TestABSettingsSerialization:
    """Settings 직렬화 A/B 비교"""

    @pytest.mark.parametrize("variant,extra_data", [
        ("A_clean", {}),
        ("B_extra_keys", {"unknown_x": 1, "deprecated_y": "old", "future_z": True}),
    ])
    def test_from_dict_produces_same_settings(self, variant, extra_data):
        """A/B: extra 키 유무와 관계없이 동일한 Settings 생성"""
        base = Settings(theme="dark", language="en").to_dict()
        base.update(extra_data)

        result = Settings.from_dict(base)
        assert result.theme == "dark"
        assert result.language == "en"
        assert result.execution_speed == "normal"

    @pytest.mark.parametrize("variant,input_data", [
        ("A_complete", Settings().to_dict()),
        ("B_minimal", {}),
        ("C_partial", {"theme": "dark"}),
    ])
    def test_from_dict_always_returns_valid_settings(self, variant, input_data):
        """A/B/C: 어떤 입력이든 유효한 Settings 반환"""
        result = Settings.from_dict(input_data)
        assert isinstance(result, Settings)
        assert result.execution_speed in ("fast", "normal", "slow")
        assert result.theme in ("light", "dark")


# ============================================================
# A/B 테스트 2: 실행 속도별 지연 시간
# ============================================================

class TestABExecutionSpeed:
    """실행 속도 A/B 비교"""

    @pytest.mark.parametrize("variant,speed,expected_delay", [
        ("A_fast", "fast", 0.1),
        ("B_normal", "normal", 0.5),
        ("C_slow", "slow", 1.0),
    ])
    def test_execution_delay(self, variant, speed, expected_delay):
        """A/B/C: 실행 속도 설정에 따른 지연 시간 정확성"""
        settings = Settings(execution_speed=speed)
        assert settings.get_execution_delay() == expected_delay

    @pytest.mark.parametrize("variant,speed_a,speed_b", [
        ("fast_vs_normal", "fast", "normal"),
        ("normal_vs_slow", "normal", "slow"),
    ])
    def test_speed_ordering(self, variant, speed_a, speed_b):
        """A/B: 빠른 속도가 항상 느린 속도보다 작은 지연"""
        a = Settings(execution_speed=speed_a).get_execution_delay()
        b = Settings(execution_speed=speed_b).get_execution_delay()
        assert a < b


# ============================================================
# A/B 테스트 3: 에러 처리 전략 비교
# ============================================================

class TestABErrorHandling:
    """에러 처리 전략 A/B 비교"""

    @pytest.fixture
    def executor(self):
        """모킹된 ActionExecutor"""
        with patch('src.core.action_executor.ImageRecognizer'), \
             patch('src.core.action_executor.DataConnector'), \
             patch('src.core.action_executor.DataManager'), \
             patch('src.core.action_executor.get_logger', return_value=MagicMock()):
            from src.core.action_executor import ActionExecutor
            yield ActionExecutor()

    @pytest.mark.parametrize("variant,on_error,expected_continue", [
        ("A_ignore", "ignore", True),
        ("B_stop", "stop", False),
    ])
    def test_error_strategy_determines_continuation(self, executor, variant, on_error, expected_continue):
        """A/B: 에러 전략에 따라 실행 계속/중단 결정"""
        action = {
            'action_type': 'mouse_click',
            'description': f'{variant} 테스트',
            'id': 1,
            'parameters': {},
            'error_handling': {
                'retry_count': 0,
                'retry_delay': 0,
                'timeout': None,
                'on_error': on_error,
            }
        }
        with patch.object(executor, '_execute_action', return_value=False):
            success, should_continue = executor._execute_action_with_error_handling(action)
            assert success is False
            assert should_continue is expected_continue

    @pytest.mark.parametrize("variant,retry_count,fail_times,expected_success", [
        ("A_no_retry", 0, 1, False),
        ("B_retry_2_fail_1", 2, 1, True),
        ("C_retry_2_fail_3", 2, 3, False),
    ])
    def test_retry_count_behavior(self, executor, variant, retry_count, fail_times, expected_success):
        """A/B/C: 재시도 횟수와 실패 횟수에 따른 결과"""
        action = {
            'action_type': 'mouse_click',
            'description': f'{variant} 테스트',
            'id': 1,
            'parameters': {},
            'error_handling': {
                'retry_count': retry_count,
                'retry_delay': 0,
                'timeout': None,
                'on_error': 'stop',
            }
        }
        # fail_times번 실패 후 성공 (총 시도 횟수 내에서)
        side_effects = [False] * fail_times + [True] * 10
        with patch.object(executor, '_execute_action', side_effect=side_effects):
            success, _ = executor._execute_action_with_error_handling(action)
            assert success is expected_success


# ============================================================
# A/B 테스트 4: 테마 색상 일관성
# ============================================================

class TestABThemeColors:
    """테마 색상 A/B 비교"""

    REQUIRED_COLOR_KEYS = {"primary", "success", "warning", "error", "background", "surface", "text", "text_secondary"}

    @pytest.mark.parametrize("variant,theme", [
        ("A_light", "light"),
        ("B_dark", "dark"),
    ])
    def test_all_color_keys_present(self, variant, theme):
        """A/B: 모든 테마에 필수 색상 키가 존재"""
        colors = Settings(theme=theme).get_theme_colors()
        assert self.REQUIRED_COLOR_KEYS == set(colors.keys())

    @pytest.mark.parametrize("variant,theme", [
        ("A_light", "light"),
        ("B_dark", "dark"),
    ])
    def test_colors_are_valid_hex(self, variant, theme):
        """A/B: 모든 색상이 유효한 HEX 코드"""
        colors = Settings(theme=theme).get_theme_colors()
        for key, value in colors.items():
            assert value.startswith('#'), f"{key}={value}는 HEX 코드가 아닙니다"
            assert len(value) == 7, f"{key}={value}는 #RRGGBB 형식이 아닙니다"

    def test_light_dark_different_backgrounds(self):
        """라이트/다크 배경색이 서로 다름"""
        light = Settings(theme="light").get_theme_colors()
        dark = Settings(theme="dark").get_theme_colors()
        assert light['background'] != dark['background']
        assert light['text'] != dark['text']


# ============================================================
# A/B 테스트 5: from_dict 견고성 (모든 모델)
# ============================================================

class TestABFromDictRobustness:
    """모든 모델의 from_dict 견고성 A/B 비교"""

    @pytest.mark.parametrize("variant,extra_keys", [
        ("A_clean", {}),
        ("B_one_extra", {"garbage": 123}),
        ("C_many_extra", {"a": 1, "b": "x", "c": [1, 2], "d": {"nested": True}}),
    ])
    def test_settings_from_dict_robustness(self, variant, extra_keys):
        """A/B/C: Settings.from_dict가 extra 키에 안전"""
        data = Settings().to_dict()
        data.update(extra_keys)
        result = Settings.from_dict(data)
        assert isinstance(result, Settings)

    @pytest.mark.parametrize("variant,extra_keys", [
        ("A_clean", {}),
        ("B_extra", {"garbage": 123, "old_field": "deprecated"}),
    ])
    def test_action_from_dict_robustness(self, variant, extra_keys):
        """A/B: Action.from_dict가 extra 키에 안전"""
        data = {
            'id': 1, 'order_index': 1, 'action_type': 'delay',
            'description': 'test', 'parameters': {'seconds': 1}
        }
        data.update(extra_keys)
        result = Action.from_dict(data)
        assert isinstance(result, Action)
        assert result.action_type == 'delay'

    @pytest.mark.parametrize("variant,extra_keys", [
        ("A_clean", {}),
        ("B_extra", {"garbage": 123, "old_field": "deprecated"}),
    ])
    def test_project_from_dict_robustness(self, variant, extra_keys):
        """A/B: Project.from_dict가 extra 키에 안전"""
        data = {'id': 1, 'name': 'test', 'description': '', 'category': ''}
        data.update(extra_keys)
        result = Project.from_dict(data)
        assert isinstance(result, Project)
        assert result.name == 'test'


# ============================================================
# A/B 테스트 6: ActionFactory vs 수동 생성 비교
# ============================================================

class TestABActionCreation:
    """ActionFactory vs 수동 생성 A/B 비교"""

    def test_factory_vs_manual_mouse_click(self):
        """A: Factory 생성 vs B: 수동 생성 - 동일한 결과"""
        factory_action = ActionFactory.create_mouse_click(1, 1, 100, 200, 'left')
        manual_action = Action(
            id=1, order_index=1,
            action_type='mouse_click',
            description='마우스 left 클릭 (100, 200)',
            parameters={'x': 100, 'y': 200, 'button': 'left'}
        )
        assert factory_action.action_type == manual_action.action_type
        assert factory_action.parameters == manual_action.parameters
        assert factory_action.id == manual_action.id

    def test_factory_vs_manual_delay(self):
        """A: Factory 생성 vs B: 수동 생성 - delay 액션"""
        factory_action = ActionFactory.create_delay(1, 1, 2.5)
        manual_action = Action(
            id=1, order_index=1,
            action_type='delay',
            description='2.5초 대기',
            parameters={'seconds': 2.5}
        )
        assert factory_action.action_type == manual_action.action_type
        assert factory_action.parameters == manual_action.parameters


# ============================================================
# A/B 테스트 7: 설정 다이얼로그 호환성
# ============================================================

class TestABSettingsDialogCompatibility:
    """settings_dialog.py에서 사용하는 모든 필드가 Settings에 존재하는지 확인"""

    DIALOG_FIELDS = [
        'language', 'auto_save', 'auto_save_interval', 'logging', 'log_level',
        'execution_speed', 'default_delay', 'safety_failsafe',
        'execution_confirm', 'execution_notify',
        'theme', 'primary_color', 'font_size', 'window_size',
        'auto_backup', 'backup_interval', 'backup_retention',
        'developer_mode', 'experimental_features',
    ]

    @pytest.mark.parametrize("field", DIALOG_FIELDS)
    def test_field_exists_in_settings(self, field):
        """settings_dialog.py에서 참조하는 필드가 Settings에 존재"""
        s = Settings()
        assert hasattr(s, field), f"Settings에 '{field}' 필드가 없습니다"

    def test_settings_can_be_created_with_all_dialog_fields(self):
        """settings_dialog._save_settings()와 동일한 방식으로 Settings 생성 가능"""
        # settings_dialog.py:416-435와 동일한 키워드 인자
        s = Settings(
            language='ko',
            auto_save=True,
            auto_save_interval=300,
            logging=True,
            log_level='INFO',
            execution_speed='normal',
            default_delay=0.5,
            safety_failsafe=True,
            execution_confirm=True,
            execution_notify=True,
            theme='light',
            primary_color='#2563eb',
            font_size='normal',
            window_size='1200x800',
            auto_backup=True,
            backup_interval=7,
            backup_retention=30,
            developer_mode=False,
            experimental_features=False,
        )
        assert isinstance(s, Settings)
        assert s.developer_mode is False
        assert s.auto_save_interval == 300
