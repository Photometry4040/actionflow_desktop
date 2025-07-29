#!/usr/bin/env python3
"""
ActionFlow Desktop Automator - 테스트 실행 스크립트
모든 테스트를 순차적으로 실행합니다.
"""
import sys
import os
import subprocess
import time

def run_test(test_file):
    """개별 테스트 실행"""
    print(f"\n{'='*60}")
    print(f"🧪 테스트 실행: {test_file}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ 테스트 성공")
            print(result.stdout)
        else:
            print("❌ 테스트 실패")
            print(result.stdout)
            print(result.stderr)
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ 테스트 시간 초과")
        return False
    except Exception as e:
        print(f"💥 테스트 실행 오류: {e}")
        return False

def main():
    """메인 테스트 실행 함수"""
    print("🚀 ActionFlow Desktop Automator - 테스트 스위트")
    print("=" * 60)
    
    # 테스트 파일 목록
    test_files = [
        "tests/test_permissions.py",
        "tests/test_mouse_action.py",
        "tests/test_dialog.py",
        "tests/test_action_dialog.py"
    ]
    
    # 테스트 실행
    results = []
    for test_file in test_files:
        if os.path.exists(test_file):
            success = run_test(test_file)
            results.append((test_file, success))
            time.sleep(1)  # 테스트 간 간격
        else:
            print(f"⚠️ 테스트 파일을 찾을 수 없음: {test_file}")
            results.append((test_file, False))
    
    # 결과 요약
    print(f"\n{'='*60}")
    print("📊 테스트 결과 요약")
    print(f"{'='*60}")
    
    passed = 0
    failed = 0
    
    for test_file, success in results:
        status = "✅ 통과" if success else "❌ 실패"
        print(f"{test_file}: {status}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\n총 테스트: {len(results)}개")
    print(f"통과: {passed}개")
    print(f"실패: {failed}개")
    
    if failed == 0:
        print("\n🎉 모든 테스트가 통과했습니다!")
        return 0
    else:
        print(f"\n⚠️ {failed}개의 테스트가 실패했습니다.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 