#!/usr/bin/env python3
"""
ActionFlow Desktop Automator - 테스트 실행 스크립트
pytest를 사용하여 모든 테스트를 실행합니다.
"""
import sys
import os


def main():
    """메인 테스트 실행 함수"""
    try:
        import pytest
    except ImportError:
        print("pytest가 설치되지 않았습니다. 설치 중...")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pytest'])
        import pytest

    print("ActionFlow Desktop Automator - 테스트 스위트")
    print("=" * 60)

    # pytest 실행 (자동 테스트 발견)
    exit_code = pytest.main([
        "tests/",
        "-v",
        "--tb=short",
    ])

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
