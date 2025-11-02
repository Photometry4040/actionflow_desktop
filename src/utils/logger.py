"""
로깅 시스템
애플리케이션 전역 로깅 설정 및 관리
"""
import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class LoggerSetup:
    """로거 설정 및 관리 클래스"""

    _initialized = False
    _loggers = {}

    @classmethod
    def setup_logging(cls, log_dir: Optional[Path] = None, log_level: str = "INFO",
                     enable_console: bool = True, enable_file: bool = True) -> None:
        """
        로깅 시스템 초기화

        Args:
            log_dir: 로그 파일 디렉토리
            log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            enable_console: 콘솔 출력 활성화
            enable_file: 파일 출력 활성화
        """
        if cls._initialized:
            return

        # 로그 레벨 설정
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)

        # 루트 로거 설정
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)

        # 기존 핸들러 제거
        root_logger.handlers.clear()

        # 포맷터 설정
        detailed_formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        simple_formatter = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 콘솔 핸들러 추가
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(numeric_level)
            console_handler.setFormatter(simple_formatter)
            root_logger.addHandler(console_handler)

        # 파일 핸들러 추가
        if enable_file and log_dir:
            try:
                # 로그 디렉토리 생성
                log_dir = Path(log_dir)
                log_dir.mkdir(parents=True, exist_ok=True)

                # 날짜별 로그 파일
                timestamp = datetime.now().strftime("%Y%m%d")
                log_file = log_dir / f"actionflow_{timestamp}.log"

                # 파일 핸들러 (일반 로그)
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file,
                    maxBytes=10 * 1024 * 1024,  # 10MB
                    backupCount=5,
                    encoding='utf-8'
                )
                file_handler.setLevel(numeric_level)
                file_handler.setFormatter(detailed_formatter)
                root_logger.addHandler(file_handler)

                # 에러 전용 로그 파일
                error_log_file = log_dir / f"actionflow_error_{timestamp}.log"
                error_handler = logging.handlers.RotatingFileHandler(
                    error_log_file,
                    maxBytes=10 * 1024 * 1024,  # 10MB
                    backupCount=5,
                    encoding='utf-8'
                )
                error_handler.setLevel(logging.ERROR)
                error_handler.setFormatter(detailed_formatter)
                root_logger.addHandler(error_handler)

            except Exception as e:
                print(f"로그 파일 핸들러 설정 오류: {e}")

        cls._initialized = True

        # 초기화 로그
        root_logger.info("=" * 80)
        root_logger.info("ActionFlow Desktop Automator - 로깅 시스템 초기화 완료")
        root_logger.info(f"로그 레벨: {log_level}")
        root_logger.info(f"콘솔 출력: {enable_console}")
        root_logger.info(f"파일 출력: {enable_file}")
        if enable_file and log_dir:
            root_logger.info(f"로그 디렉토리: {log_dir}")
        root_logger.info("=" * 80)

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        모듈별 로거 반환

        Args:
            name: 로거 이름 (보통 __name__ 사용)

        Returns:
            로거 인스턴스
        """
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger

        return cls._loggers[name]

    @classmethod
    def shutdown(cls):
        """로깅 시스템 종료"""
        logging.shutdown()
        cls._initialized = False
        cls._loggers.clear()


def get_logger(name: str) -> logging.Logger:
    """
    편의 함수: 로거 반환

    Args:
        name: 로거 이름

    Returns:
        로거 인스턴스
    """
    return LoggerSetup.get_logger(name)


# 전역 로거 인스턴스 (하위 호환성)
logger = logging.getLogger(__name__)
