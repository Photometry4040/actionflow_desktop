"""
JSON 스키마 검증
데이터 파일의 구조 검증 및 손상된 파일 복구
"""
import json
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from pathlib import Path

from .logger import get_logger

logger = get_logger(__name__)


class JSONValidator:
    """JSON 데이터 검증 클래스"""

    # 프로젝트 파일 스키마
    PROJECTS_SCHEMA = {
        "type": "object",
        "required": ["projects", "next_project_id", "next_action_id", "created_at", "version"],
        "properties": {
            "projects": {"type": "array"},
            "next_project_id": {"type": "integer", "minimum": 1},
            "next_action_id": {"type": "integer", "minimum": 1},
            "created_at": {"type": "string"},
            "version": {"type": "string"}
        }
    }

    # 프로젝트 스키마
    PROJECT_SCHEMA = {
        "type": "object",
        "required": ["id", "name", "description", "category", "favorite", "actions", "created_at", "updated_at"],
        "properties": {
            "id": {"type": "integer", "minimum": 1},
            "name": {"type": "string", "minLength": 1, "maxLength": 100},
            "description": {"type": "string", "maxLength": 1000},
            "category": {"type": "string"},
            "favorite": {"type": "boolean"},
            "actions": {"type": "array"},
            "created_at": {"type": "string"},
            "updated_at": {"type": "string"}
        }
    }

    # 액션 스키마
    ACTION_SCHEMA = {
        "type": "object",
        "required": ["id", "order_index", "action_type", "description", "parameters"],
        "properties": {
            "id": {"type": "integer", "minimum": 1},
            "order_index": {"type": "integer", "minimum": 1},
            "action_type": {"type": "string"},
            "description": {"type": "string"},
            "parameters": {"type": "object"}
        }
    }

    # 설정 파일 스키마
    SETTINGS_SCHEMA = {
        "type": "object",
        "required": [
            "theme", "language", "window_width", "window_height",
            "execution_speed", "default_delay", "safety_failsafe",
            "auto_save", "backup_interval", "max_history",
            "enable_logging", "log_level"
        ],
        "properties": {
            "theme": {"type": "string", "enum": ["light", "dark"]},
            "language": {"type": "string", "enum": ["ko", "en"]},
            "window_width": {"type": "integer", "minimum": 800},
            "window_height": {"type": "integer", "minimum": 600},
            "execution_speed": {"type": "string", "enum": ["fast", "normal", "slow"]},
            "default_delay": {"type": "number", "minimum": 0},
            "safety_failsafe": {"type": "boolean"},
            "auto_save": {"type": "boolean"},
            "backup_interval": {"type": "integer", "minimum": 1},
            "max_history": {"type": "integer", "minimum": 10},
            "enable_logging": {"type": "boolean"},
            "log_level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]}
        }
    }

    @classmethod
    def validate_projects_file(cls, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        프로젝트 파일 검증

        Args:
            data: 검증할 데이터

        Returns:
            (유효성 여부, 에러 메시지 리스트)
        """
        errors = []

        try:
            # 필수 필드 검증
            for field in cls.PROJECTS_SCHEMA["required"]:
                if field not in data:
                    errors.append(f"필수 필드 누락: {field}")

            # 타입 검증
            if "projects" in data and not isinstance(data["projects"], list):
                errors.append("projects는 배열이어야 합니다")

            if "next_project_id" in data and not isinstance(data["next_project_id"], int):
                errors.append("next_project_id는 정수여야 합니다")

            if "next_action_id" in data and not isinstance(data["next_action_id"], int):
                errors.append("next_action_id는 정수여야 합니다")

            # 각 프로젝트 검증
            if "projects" in data and isinstance(data["projects"], list):
                for i, project in enumerate(data["projects"]):
                    project_valid, project_errors = cls.validate_project(project)
                    if not project_valid:
                        errors.extend([f"프로젝트 #{i}: {err}" for err in project_errors])

        except Exception as e:
            logger.error(f"프로젝트 파일 검증 오류: {str(e)}", exc_info=True)
            errors.append(f"검증 중 오류 발생: {str(e)}")

        return len(errors) == 0, errors

    @classmethod
    def validate_project(cls, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        개별 프로젝트 검증

        Args:
            data: 검증할 프로젝트 데이터

        Returns:
            (유효성 여부, 에러 메시지 리스트)
        """
        errors = []

        try:
            # 필수 필드 검증
            for field in cls.PROJECT_SCHEMA["required"]:
                if field not in data:
                    errors.append(f"필수 필드 누락: {field}")

            # 타입 및 제약 조건 검증
            if "id" in data and (not isinstance(data["id"], int) or data["id"] < 1):
                errors.append("id는 1 이상의 정수여야 합니다")

            if "name" in data:
                if not isinstance(data["name"], str):
                    errors.append("name은 문자열이어야 합니다")
                elif len(data["name"]) == 0 or len(data["name"]) > 100:
                    errors.append("name은 1-100자여야 합니다")

            if "description" in data:
                if not isinstance(data["description"], str):
                    errors.append("description은 문자열이어야 합니다")
                elif len(data["description"]) > 1000:
                    errors.append("description은 1000자 이하여야 합니다")

            if "favorite" in data and not isinstance(data["favorite"], bool):
                errors.append("favorite는 불리언이어야 합니다")

            if "actions" in data:
                if not isinstance(data["actions"], list):
                    errors.append("actions는 배열이어야 합니다")
                else:
                    # 각 액션 검증
                    for i, action in enumerate(data["actions"]):
                        action_valid, action_errors = cls.validate_action(action)
                        if not action_valid:
                            errors.extend([f"액션 #{i}: {err}" for err in action_errors])

        except Exception as e:
            logger.error(f"프로젝트 검증 오류: {str(e)}", exc_info=True)
            errors.append(f"검증 중 오류 발생: {str(e)}")

        return len(errors) == 0, errors

    @classmethod
    def validate_action(cls, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        개별 액션 검증

        Args:
            data: 검증할 액션 데이터

        Returns:
            (유효성 여부, 에러 메시지 리스트)
        """
        errors = []

        try:
            # 필수 필드 검증
            for field in cls.ACTION_SCHEMA["required"]:
                if field not in data:
                    errors.append(f"필수 필드 누락: {field}")

            # 타입 검증
            if "id" in data and (not isinstance(data["id"], int) or data["id"] < 1):
                errors.append("id는 1 이상의 정수여야 합니다")

            if "order_index" in data and (not isinstance(data["order_index"], int) or data["order_index"] < 1):
                errors.append("order_index는 1 이상의 정수여야 합니다")

            if "action_type" in data and not isinstance(data["action_type"], str):
                errors.append("action_type은 문자열이어야 합니다")

            if "description" in data and not isinstance(data["description"], str):
                errors.append("description은 문자열이어야 합니다")

            if "parameters" in data and not isinstance(data["parameters"], dict):
                errors.append("parameters는 객체여야 합니다")

        except Exception as e:
            logger.error(f"액션 검증 오류: {str(e)}", exc_info=True)
            errors.append(f"검증 중 오류 발생: {str(e)}")

        return len(errors) == 0, errors

    @classmethod
    def validate_settings(cls, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        설정 파일 검증

        Args:
            data: 검증할 설정 데이터

        Returns:
            (유효성 여부, 에러 메시지 리스트)
        """
        errors = []

        try:
            # 필수 필드 검증
            for field in cls.SETTINGS_SCHEMA["required"]:
                if field not in data:
                    errors.append(f"필수 필드 누락: {field}")

            # 테마 검증
            if "theme" in data and data["theme"] not in ["light", "dark"]:
                errors.append("theme은 'light' 또는 'dark'여야 합니다")

            # 언어 검증
            if "language" in data and data["language"] not in ["ko", "en"]:
                errors.append("language는 'ko' 또는 'en'이어야 합니다")

            # 윈도우 크기 검증
            if "window_width" in data and (not isinstance(data["window_width"], int) or data["window_width"] < 800):
                errors.append("window_width는 800 이상의 정수여야 합니다")

            if "window_height" in data and (not isinstance(data["window_height"], int) or data["window_height"] < 600):
                errors.append("window_height는 600 이상의 정수여야 합니다")

            # 실행 속도 검증
            if "execution_speed" in data and data["execution_speed"] not in ["fast", "normal", "slow"]:
                errors.append("execution_speed는 'fast', 'normal', 'slow' 중 하나여야 합니다")

            # 기본 지연 시간 검증
            if "default_delay" in data and (not isinstance(data["default_delay"], (int, float)) or data["default_delay"] < 0):
                errors.append("default_delay는 0 이상의 숫자여야 합니다")

            # 로그 레벨 검증
            if "log_level" in data and data["log_level"] not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
                errors.append("log_level은 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL' 중 하나여야 합니다")

        except Exception as e:
            logger.error(f"설정 검증 오류: {str(e)}", exc_info=True)
            errors.append(f"검증 중 오류 발생: {str(e)}")

        return len(errors) == 0, errors

    @classmethod
    def create_default_projects_data(cls) -> Dict[str, Any]:
        """기본 프로젝트 데이터 생성"""
        return {
            "projects": [],
            "next_project_id": 1,
            "next_action_id": 1,
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0"
        }

    @classmethod
    def repair_projects_file(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        손상된 프로젝트 파일 복구

        Args:
            data: 복구할 데이터

        Returns:
            복구된 데이터
        """
        logger.warning("프로젝트 파일 복구 시도")

        repaired = cls.create_default_projects_data()

        try:
            # 기존 프로젝트 복구 시도
            if "projects" in data and isinstance(data["projects"], list):
                valid_projects = []
                for project in data["projects"]:
                    is_valid, _ = cls.validate_project(project)
                    if is_valid:
                        valid_projects.append(project)
                    else:
                        logger.warning(f"손상된 프로젝트 제외: {project.get('name', 'Unknown')}")

                repaired["projects"] = valid_projects

            # ID 카운터 복구
            if "next_project_id" in data and isinstance(data["next_project_id"], int):
                repaired["next_project_id"] = data["next_project_id"]

            if "next_action_id" in data and isinstance(data["next_action_id"], int):
                repaired["next_action_id"] = data["next_action_id"]

            logger.info(f"프로젝트 파일 복구 완료: {len(repaired['projects'])}개의 유효한 프로젝트 복구됨")

        except Exception as e:
            logger.error(f"프로젝트 파일 복구 오류: {str(e)}", exc_info=True)

        return repaired
