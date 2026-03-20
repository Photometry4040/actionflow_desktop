"""
DataManager 테스트
JSON 데이터 저장/로드, CRUD 연산 테스트
"""
import pytest
import json
import os
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.settings import Settings
from src.models.project import Project


class TestDataManagerInit:
    """DataManager 초기화 테스트"""

    def test_creates_default_files(self, data_manager, tmp_data_dir):
        """초기화 시 기본 JSON 파일들이 생성됨"""
        data_dir = Path(tmp_data_dir)
        assert (data_dir / "projects.json").exists()
        assert (data_dir / "settings.json").exists()
        assert (data_dir / "templates.json").exists()
        assert (data_dir / "backups").is_dir()

    def test_default_projects_structure(self, data_manager, tmp_data_dir):
        """기본 projects.json 구조 확인"""
        with open(os.path.join(tmp_data_dir, "projects.json"), 'r') as f:
            data = json.load(f)
        assert "projects" in data
        assert data["projects"] == []
        assert "next_project_id" in data

    def test_default_settings_values(self, data_manager):
        """기본 설정값 확인"""
        settings = data_manager.get_settings()
        assert isinstance(settings, Settings)
        assert settings.execution_speed == "normal"


class TestDataManagerProjectCRUD:
    """프로젝트 CRUD 테스트"""

    def test_save_and_get_project(self, data_manager):
        """프로젝트 저장 및 조회"""
        project = Project(id=1, name='테스트', description='설명', category='기타')
        data_manager.save_project(project)

        retrieved = data_manager.get_project_by_id(1)
        assert retrieved is not None
        assert retrieved.name == '테스트'

    def test_get_all_projects(self, data_manager):
        """전체 프로젝트 목록 조회"""
        for i in range(3):
            p = Project(id=i + 1, name=f'프로젝트{i}', description='', category='')
            data_manager.save_project(p)

        projects = data_manager.get_all_projects()
        assert len(projects) == 3

    def test_update_project(self, data_manager):
        """프로젝트 업데이트"""
        project = Project(id=1, name='원본', description='', category='')
        data_manager.save_project(project)

        project.name = '수정됨'
        data_manager.save_project(project)

        retrieved = data_manager.get_project_by_id(1)
        assert retrieved.name == '수정됨'

    def test_delete_project(self, data_manager):
        """프로젝트 삭제"""
        project = Project(id=1, name='삭제대상', description='', category='')
        data_manager.save_project(project)

        result = data_manager.delete_project(1)
        assert result is True
        assert data_manager.get_project_by_id(1) is None

    def test_delete_nonexistent_project(self, data_manager):
        """존재하지 않는 프로젝트 삭제"""
        result = data_manager.delete_project(999)
        assert result is False

    def test_get_next_project_id(self, data_manager):
        """다음 프로젝트 ID 반환"""
        next_id = data_manager.get_next_project_id()
        assert isinstance(next_id, int)
        assert next_id >= 1


class TestDataManagerSettings:
    """설정 CRUD 테스트"""

    def test_save_and_get_settings(self, data_manager):
        """설정 저장 및 로드"""
        settings = Settings(theme="dark", language="en")
        data_manager.save_settings(settings)

        loaded = data_manager.get_settings()
        assert loaded.theme == "dark"
        assert loaded.language == "en"

    def test_settings_roundtrip_with_new_fields(self, data_manager):
        """새 필드 포함 설정 왕복"""
        settings = Settings(
            developer_mode=True,
            experimental_features=True,
            primary_color="#ff0000",
            auto_save_interval=600,
        )
        data_manager.save_settings(settings)
        loaded = data_manager.get_settings()
        assert loaded.developer_mode is True
        assert loaded.experimental_features is True
        assert loaded.primary_color == "#ff0000"
        assert loaded.auto_save_interval == 600

    def test_reset_settings(self, data_manager):
        """설정 초기화"""
        # 설정 변경 후 초기화
        data_manager.save_settings(Settings(theme="dark"))
        data_manager.reset_settings()

        loaded = data_manager.get_settings()
        assert loaded.theme == "light"

    def test_settings_extra_keys_in_json(self, data_manager, tmp_data_dir):
        """JSON에 예상치 못한 키가 있어도 안전하게 로드"""
        settings_path = os.path.join(tmp_data_dir, "settings.json")
        with open(settings_path, 'r') as f:
            data = json.load(f)
        data['totally_unknown_key'] = 'should_not_crash'
        with open(settings_path, 'w') as f:
            json.dump(data, f)

        loaded = data_manager.get_settings()
        assert isinstance(loaded, Settings)


class TestDataManagerActions:
    """액션 관리 테스트"""

    def test_save_action_to_project(self, data_manager):
        """프로젝트에 액션 저장"""
        project = Project(id=1, name='test', description='', category='')
        data_manager.save_project(project)

        action = {
            'id': 1, 'order_index': 1,
            'action_type': 'delay', 'description': '1초 대기',
            'parameters': {'seconds': 1}
        }
        data_manager.save_action(1, action)

        retrieved = data_manager.get_project_by_id(1)
        assert retrieved.get_action_count() == 1

    def test_save_action_invalid_project(self, data_manager):
        """존재하지 않는 프로젝트에 액션 저장 시 에러"""
        with pytest.raises(ValueError):
            data_manager.save_action(999, {'id': 1})

    def test_get_next_action_order(self, data_manager):
        """다음 액션 순서 반환"""
        project = Project(id=1, name='test', description='', category='')
        project.add_action({'id': 1, 'order_index': 5, 'action_type': 'delay', 'description': '', 'parameters': {}})
        data_manager.save_project(project)

        next_order = data_manager.get_next_action_order(1)
        assert next_order == 6


class TestDataManagerBackup:
    """백업/복원 테스트"""

    def test_create_and_list_backup(self, data_manager):
        """백업 생성 및 목록 조회"""
        backup_path = data_manager.create_backup()
        assert os.path.isdir(backup_path)

        backups = data_manager.get_backup_list()
        assert len(backups) >= 1

    def test_restore_backup(self, data_manager):
        """백업 복원"""
        # 원본 설정 저장
        data_manager.save_settings(Settings(theme="dark"))
        backup_path = data_manager.create_backup()

        # 설정 변경
        data_manager.save_settings(Settings(theme="light"))

        # 백업 복원
        result = data_manager.restore_backup(backup_path)
        assert result is True
        loaded = data_manager.get_settings()
        assert loaded.theme == "dark"

    def test_restore_nonexistent_backup(self, data_manager):
        """존재하지 않는 백업 복원 실패"""
        result = data_manager.restore_backup("/nonexistent/path")
        assert result is False


class TestDataManagerExportImport:
    """내보내기/가져오기 테스트"""

    def test_export_and_import(self, data_manager, tmp_path):
        """프로젝트 내보내기 후 가져오기"""
        project = Project(id=1, name='내보내기 테스트', description='설명', category='기타')
        project.add_action({'id': 1, 'order_index': 1, 'action_type': 'delay', 'description': '', 'parameters': {'seconds': 1}})
        data_manager.save_project(project)

        export_path = str(tmp_path / "export.json")
        result = data_manager.export_project(1, export_path)
        assert result is True
        assert os.path.exists(export_path)

        # 가져오기
        imported = data_manager.import_project(export_path)
        assert imported is not None
        assert imported.name == '내보내기 테스트'
        assert imported.get_action_count() == 1

    def test_export_nonexistent_project(self, data_manager, tmp_path):
        """존재하지 않는 프로젝트 내보내기 실패"""
        result = data_manager.export_project(999, str(tmp_path / "x.json"))
        assert result is False


class TestDataManagerEdgeCases:
    """엣지 케이스 테스트"""

    def test_load_empty_json(self, data_manager, tmp_data_dir):
        """빈 파일 로드 시 빈 딕셔너리 반환"""
        # projects.json을 빈 파일로 덮어쓰기
        with open(os.path.join(tmp_data_dir, "projects.json"), 'w') as f:
            f.write('')

        projects = data_manager.get_all_projects()
        assert projects == []

    def test_load_invalid_json(self, data_manager, tmp_data_dir):
        """잘못된 JSON 로드 시 빈 딕셔너리 반환"""
        with open(os.path.join(tmp_data_dir, "projects.json"), 'w') as f:
            f.write('{invalid json}')

        projects = data_manager.get_all_projects()
        assert projects == []

    def test_get_data_info(self, data_manager):
        """데이터 정보 반환"""
        info = data_manager.get_data_info()
        assert "total_projects" in info
        assert "total_actions" in info
        assert "templates_count" in info
