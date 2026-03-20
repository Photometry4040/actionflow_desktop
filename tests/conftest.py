"""
ActionFlow Desktop - 공유 테스트 픽스처
모든 테스트에서 사용하는 공통 설정 및 모킹
"""
import sys
import os
import json
import tempfile
import shutil
import pytest
from unittest.mock import MagicMock, patch

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture
def tmp_data_dir(tmp_path):
    """임시 데이터 디렉토리 생성"""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return str(data_dir)


@pytest.fixture
def sample_settings():
    """기본 Settings 인스턴스"""
    from src.models.settings import Settings
    return Settings()


@pytest.fixture
def sample_action_dict():
    """샘플 액션 딕셔너리"""
    return {
        'id': 1,
        'order_index': 1,
        'action_type': 'mouse_click',
        'description': '테스트 클릭',
        'parameters': {'x': 100, 'y': 200, 'button': 'left'},
        'tags': ['테스트'],
    }


@pytest.fixture
def sample_action():
    """샘플 Action 인스턴스"""
    from src.models.action import Action
    return Action(
        id=1,
        order_index=1,
        action_type='mouse_click',
        description='테스트 클릭',
        parameters={'x': 100, 'y': 200, 'button': 'left'},
        tags=['테스트']
    )


@pytest.fixture
def sample_project():
    """3개 액션을 가진 샘플 프로젝트"""
    from src.models.project import Project
    project = Project(
        id=1,
        name='테스트 프로젝트',
        description='테스트용 프로젝트',
        category='테스트'
    )
    for i in range(3):
        project.add_action({
            'id': i + 1,
            'order_index': i + 1,
            'action_type': 'mouse_click',
            'description': f'클릭 {i + 1}',
            'parameters': {'x': 100 * (i + 1), 'y': 200},
        })
    return project


@pytest.fixture
def data_manager(tmp_data_dir):
    """임시 디렉토리 기반 DataManager"""
    with patch('src.utils.data_manager.get_logger', return_value=MagicMock()):
        from src.utils.data_manager import DataManager
        return DataManager(data_dir=tmp_data_dir)


@pytest.fixture
def mock_pyautogui():
    """pyautogui 모킹"""
    mock = MagicMock()
    mock.position.return_value = (500, 500)
    mock.size.return_value = (1920, 1080)
    mock.FAILSAFE = True
    mock.PAUSE = 0.1
    with patch.dict('sys.modules', {'pyautogui': mock}):
        yield mock


@pytest.fixture
def mock_pyperclip():
    """pyperclip 모킹"""
    mock = MagicMock()
    mock.paste.return_value = ''
    with patch.dict('sys.modules', {'pyperclip': mock}):
        yield mock
