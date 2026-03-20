"""
모델 단위 테스트
Settings, Action, Project 모델의 생성, 직렬화, 유효성 검사 테스트
"""
import pytest
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.settings import Settings, DefaultSettings
from src.models.action import Action, ActionTypes, ActionFactory
from src.models.project import Project


# ============================================================
# Settings 테스트
# ============================================================

class TestSettings:
    """Settings 모델 테스트"""

    def test_default_creation(self):
        """기본값으로 Settings 생성"""
        s = Settings()
        assert s.execution_speed == "normal"
        assert s.default_delay == 0.5
        assert s.safety_failsafe is True
        assert s.theme == "light"
        assert s.language == "ko"
        assert s.auto_save is True
        assert s.enable_logging is True
        assert s.developer_mode is False
        assert s.experimental_features is False
        assert s.execution_confirm is True
        assert s.execution_notify is True
        assert s.primary_color == "#2563eb"
        assert s.font_size == "normal"
        assert s.window_size == "1200x800"
        assert s.auto_save_interval == 300
        assert s.backup_retention == 30
        assert s.recent_projects == []

    def test_to_dict_roundtrip(self):
        """to_dict -> from_dict 왕복 테스트"""
        original = Settings()
        d = original.to_dict()
        restored = Settings.from_dict(d)
        assert original.to_dict() == restored.to_dict()

    def test_from_dict_extra_keys_ignored(self):
        """from_dict에 extra 키가 있어도 무시됨"""
        data = Settings().to_dict()
        data['unknown_field'] = 'should_be_ignored'
        data['another_extra'] = 42
        s = Settings.from_dict(data)
        assert not hasattr(s, 'unknown_field') or s.__dict__.get('unknown_field') is None
        assert s.execution_speed == "normal"

    def test_from_dict_missing_keys_use_defaults(self):
        """from_dict에 키가 누락되면 기본값 사용"""
        s = Settings.from_dict({})
        assert s.execution_speed == "normal"
        assert s.theme == "light"
        assert s.developer_mode is False

    def test_from_json_roundtrip(self):
        """JSON 직렬화 왕복 테스트"""
        original = Settings(theme="dark", language="en")
        json_str = original.to_json()
        restored = Settings.from_json(json_str)
        assert restored.theme == "dark"
        assert restored.language == "en"

    @pytest.mark.parametrize("speed,expected_delay", [
        ("fast", 0.1),
        ("normal", 0.5),
        ("slow", 1.0),
        ("unknown", 0.5),  # default_delay 반환
    ])
    def test_get_execution_delay(self, speed, expected_delay):
        """실행 속도별 지연 시간 확인"""
        s = Settings(execution_speed=speed)
        assert s.get_execution_delay() == expected_delay

    def test_theme_colors_light(self):
        """라이트 테마 색상에 필수 키가 모두 존재"""
        s = Settings(theme="light")
        colors = s.get_theme_colors()
        required_keys = {"primary", "success", "warning", "error", "background", "surface", "text", "text_secondary"}
        assert required_keys.issubset(colors.keys())

    def test_theme_colors_dark(self):
        """다크 테마 색상에 필수 키가 모두 존재"""
        s = Settings(theme="dark")
        colors = s.get_theme_colors()
        required_keys = {"primary", "success", "warning", "error", "background", "surface", "text", "text_secondary"}
        assert required_keys.issubset(colors.keys())

    def test_update_partial(self):
        """부분 업데이트"""
        s = Settings()
        s.update(theme="dark", language="en")
        assert s.theme == "dark"
        assert s.language == "en"
        assert s.execution_speed == "normal"  # 변경하지 않은 값은 유지

    def test_recent_projects_management(self):
        """최근 프로젝트 추가/중복제거/최대 10개"""
        s = Settings()
        # 추가
        s.add_recent_project(1)
        s.add_recent_project(2)
        assert s.recent_projects == [2, 1]

        # 중복 추가 시 맨 앞으로 이동
        s.add_recent_project(1)
        assert s.recent_projects == [1, 2]

        # 최대 10개 제한
        for i in range(20):
            s.add_recent_project(100 + i)
        assert len(s.recent_projects) == 10

    def test_clear_recent_projects(self):
        """최근 프로젝트 목록 초기화"""
        s = Settings()
        s.add_recent_project(1)
        s.clear_recent_projects()
        assert s.recent_projects == []

    def test_logging_sync(self):
        """logging과 enable_logging 동기화"""
        s = Settings(logging=False)
        assert s.enable_logging is False

        s2 = Settings(logging=True)
        assert s2.enable_logging is True

    def test_is_dark_theme(self):
        """다크 테마 확인 메서드"""
        assert Settings(theme="dark").is_dark_theme() is True
        assert Settings(theme="light").is_dark_theme() is False

    def test_is_korean(self):
        """한국어 확인 메서드"""
        assert Settings(language="ko").is_korean() is True
        assert Settings(language="en").is_korean() is False


class TestDefaultSettings:
    """DefaultSettings 팩토리 테스트"""

    def test_get_default_settings(self):
        """기본 설정 반환"""
        s = DefaultSettings.get_default_settings()
        assert isinstance(s, Settings)
        assert s.execution_speed == "normal"

    def test_get_minimal_settings(self):
        """최소 설정 반환"""
        s = DefaultSettings.get_minimal_settings()
        assert s.enable_logging is False

    def test_get_performance_settings(self):
        """성능 최적화 설정 반환"""
        s = DefaultSettings.get_performance_settings()
        assert s.execution_speed == "fast"
        assert s.default_delay == 0.1
        assert s.safety_failsafe is False


# ============================================================
# Action 테스트
# ============================================================

class TestAction:
    """Action 모델 테스트"""

    def test_creation(self, sample_action):
        """기본 생성"""
        assert sample_action.id == 1
        assert sample_action.action_type == 'mouse_click'
        assert sample_action.parameters['x'] == 100

    def test_from_dict_extra_keys(self, sample_action_dict):
        """from_dict에 extra 키가 있어도 안전"""
        sample_action_dict['extra_field'] = 'test'
        a = Action.from_dict(sample_action_dict)
        assert a.id == 1
        assert a.action_type == 'mouse_click'

    def test_to_dict_roundtrip(self, sample_action):
        """to_dict -> from_dict 왕복"""
        d = sample_action.to_dict()
        restored = Action.from_dict(d)
        assert restored.id == sample_action.id
        assert restored.action_type == sample_action.action_type

    def test_validate_valid(self, sample_action):
        """유효한 액션 검증"""
        assert sample_action.validate() is True

    def test_validate_missing_type(self):
        """action_type이 None이면 유효하지 않음"""
        a = Action(id=1, order_index=1, action_type=None, description='test', parameters={})
        assert a.validate() is False

    def test_tags_crud(self, sample_action):
        """태그 추가/제거/확인"""
        sample_action.add_tag('새태그')
        assert sample_action.has_tag('새태그')

        sample_action.remove_tag('새태그')
        assert not sample_action.has_tag('새태그')

        # 빈 태그 추가 무시
        sample_action.add_tag('')
        assert '' not in sample_action.get_tags()

        # 중복 태그 추가 무시
        sample_action.add_tag('테스트')
        sample_action.add_tag('테스트')
        assert sample_action.get_tags().count('테스트') == 1

    def test_default_error_handling(self):
        """기본 에러 처리 설정"""
        a = Action(id=1, order_index=1, action_type='delay', description='test', parameters={})
        eh = a.error_handling
        assert eh['retry_count'] == 0
        assert eh['on_error'] == 'stop'
        assert eh['timeout'] is None

    def test_get_set_parameter(self, sample_action):
        """파라미터 조회/설정"""
        assert sample_action.get_parameter('x') == 100
        assert sample_action.get_parameter('missing', 'default') == 'default'
        sample_action.set_parameter('x', 999)
        assert sample_action.get_parameter('x') == 999


class TestActionTypes:
    """ActionTypes 상수 테스트"""

    def test_get_all_types(self):
        """모든 타입이 반환됨"""
        types = ActionTypes.get_all_types()
        assert len(types) > 10
        assert 'mouse_click' in types
        assert 'delay' in types

    def test_display_names(self):
        """표시 이름이 모든 타입에 대해 존재"""
        for t in ActionTypes.get_all_types():
            name = ActionTypes.get_display_name(t)
            assert name is not None and name != ''


class TestActionFactory:
    """ActionFactory 팩토리 메서드 테스트"""

    def test_create_mouse_move(self):
        a = ActionFactory.create_mouse_move(1, 1, 100, 200)
        assert a.action_type == ActionTypes.MOUSE_MOVE
        assert a.parameters['x'] == 100

    def test_create_mouse_click(self):
        a = ActionFactory.create_mouse_click(2, 2, 300, 400, 'right')
        assert a.action_type == ActionTypes.MOUSE_CLICK
        assert a.parameters['button'] == 'right'

    def test_create_keyboard_type(self):
        a = ActionFactory.create_keyboard_type(3, 3, 'Hello')
        assert a.action_type == ActionTypes.KEYBOARD_TYPE
        assert a.parameters['text'] == 'Hello'

    def test_create_delay(self):
        a = ActionFactory.create_delay(4, 4, 2.5)
        assert a.action_type == ActionTypes.DELAY
        assert a.parameters['seconds'] == 2.5

    def test_create_hotkey(self):
        a = ActionFactory.create_hotkey(5, 5, ['ctrl', 'c'])
        assert a.action_type == ActionTypes.KEYBOARD_HOTKEY
        assert a.parameters['keys'] == ['ctrl', 'c']


# ============================================================
# Project 테스트
# ============================================================

class TestProject:
    """Project 모델 테스트"""

    def test_creation(self):
        """기본 생성 시 타임스탬프 자동 설정"""
        p = Project(id=1, name='테스트', description='설명', category='기타')
        assert p.created_at is not None
        assert p.updated_at is not None
        assert p.actions == []

    def test_from_dict_extra_keys(self):
        """from_dict에 extra 키가 있어도 안전"""
        data = {
            'id': 1, 'name': 'test', 'description': '', 'category': '',
            'unknown_field': 'ignored'
        }
        p = Project.from_dict(data)
        assert p.id == 1

    def test_to_dict_roundtrip(self, sample_project):
        """to_dict -> from_dict 왕복"""
        d = sample_project.to_dict()
        restored = Project.from_dict(d)
        assert restored.id == sample_project.id
        assert len(restored.actions) == 3

    def test_add_remove_action(self):
        """액션 추가/제거"""
        p = Project(id=1, name='test', description='', category='')
        assert p.is_empty()

        p.add_action({'id': 1, 'order_index': 1, 'action_type': 'delay', 'description': '1초', 'parameters': {'seconds': 1}})
        assert p.get_action_count() == 1
        assert not p.is_empty()

        p.remove_action(1)
        assert p.is_empty()

    def test_get_action_by_id(self, sample_project):
        """ID로 액션 조회"""
        action = sample_project.get_action_by_id(2)
        assert action is not None
        assert action['id'] == 2

        assert sample_project.get_action_by_id(999) is None

    def test_move_action_up(self, sample_project):
        """액션 위로 이동"""
        # id=2를 위로 이동
        result = sample_project.move_action_up(2)
        assert result is True
        assert sample_project.actions[0]['id'] == 2
        assert sample_project.actions[1]['id'] == 1

    def test_move_action_up_first_item(self, sample_project):
        """첫 번째 액션은 위로 이동 불가"""
        result = sample_project.move_action_up(1)
        assert result is False

    def test_move_action_down(self, sample_project):
        """액션 아래로 이동"""
        result = sample_project.move_action_down(1)
        assert result is True
        assert sample_project.actions[0]['id'] == 2
        assert sample_project.actions[1]['id'] == 1

    def test_move_action_down_last_item(self, sample_project):
        """마지막 액션은 아래로 이동 불가"""
        result = sample_project.move_action_down(3)
        assert result is False

    def test_reorder_actions(self, sample_project):
        """액션 순서 재정렬"""
        # 순서를 섞은 후 재정렬
        sample_project.actions.reverse()
        sample_project.reorder_actions()
        for i, action in enumerate(sample_project.actions):
            assert action['order_index'] == i + 1

    def test_update_action(self, sample_project):
        """액션 업데이트"""
        updated = {'action_type': 'delay', 'description': '변경됨', 'parameters': {'seconds': 2}}
        result = sample_project.update_action(1, updated)
        assert result is True
        action = sample_project.get_action_by_id(1)
        assert action['description'] == '변경됨'
        assert action['action_type'] == 'delay'

    def test_update_action_not_found(self, sample_project):
        """존재하지 않는 액션 업데이트 실패"""
        result = sample_project.update_action(999, {'description': 'x'})
        assert result is False
