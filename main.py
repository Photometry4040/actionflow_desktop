#!/usr/bin/env python3
"""
ActionFlow Desktop Automator
메인 애플리케이션 진입점

JSON 기반 데이터 저장을 사용하는 로컬 PC용 반복 업무 자동화 도구
단일 .exe 파일로 배포 가능한 간단한 구조
"""

import sys
import os
import traceback
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.gui.main_window import MainWindow
    from src.utils.config import config
    from src.utils.data_manager import DataManager
    
    def main():
        """메인 함수"""
        print("ActionFlow Desktop Automator 시작 중...")
        print(f"버전: {config.get_app_version()}")
        print(f"플랫폼: {config.get_platform()}")
        print(f"개발 모드: {config.is_development()}")
        
        # 설정 검증 및 수정
        if not config.validate_settings():
            print("설정 검증 실패. 기본값으로 수정합니다.")
            config.fix_settings()
        
        # 데이터 관리자 초기화
        try:
            data_manager = DataManager()
            print("데이터 관리자 초기화 완료")
        except Exception as e:
            print(f"데이터 관리자 초기화 오류: {e}")
            return 1
        
        # 메인 윈도우 생성 및 실행
        try:
            app = MainWindow()
            print("메인 윈도우 생성 완료")
            print("애플리케이션 실행 중...")
            app.run()
        except Exception as e:
            print(f"애플리케이션 실행 오류: {e}")
            traceback.print_exc()
            return 1
        
        print("애플리케이션 종료")
        return 0
    
    if __name__ == "__main__":
        # 애플리케이션 실행
        exit_code = main()
        sys.exit(exit_code)

except ImportError as e:
    print(f"모듈 import 오류: {e}")
    print("의존성 설치가 필요합니다: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"초기화 오류: {e}")
    traceback.print_exc()
    sys.exit(1) 