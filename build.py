"""
빌드 스크립트
PyInstaller를 사용하여 실행 파일 생성
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path


class BuildManager:
    """빌드 관리 클래스"""
    
    def __init__(self):
        """초기화"""
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        self.spec_file = self.project_root / "actionflow.spec"
    
    def clean_build_dirs(self):
        """빌드 디렉토리 정리"""
        print("빌드 디렉토리 정리 중...")
        
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
            print(f"✓ {self.dist_dir} 삭제됨")
        
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            print(f"✓ {self.build_dir} 삭제됨")
        
        if self.spec_file.exists():
            self.spec_file.unlink()
            print(f"✓ {self.spec_file} 삭제됨")
    
    def install_dependencies(self):
        """의존성 설치"""
        print("의존성 설치 중...")
        
        try:
            # PyInstaller 설치
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                         check=True, capture_output=True, text=True)
            print("✓ PyInstaller 설치 완료")
            
            # 프로젝트 의존성 설치
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         check=True, capture_output=True, text=True)
            print("✓ 프로젝트 의존성 설치 완료")
            
        except subprocess.CalledProcessError as e:
            print(f"✗ 의존성 설치 실패: {e}")
            return False
        
        return True
    
    def create_spec_file(self):
        """PyInstaller spec 파일 생성"""
        print("PyInstaller spec 파일 생성 중...")
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[r'{self.project_root}'],
    binaries=[],
    datas=[
        ('data', 'data'),
        ('src/resources', 'src/resources'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.simpledialog',
        'pyautogui',
        'pyperclip',
        'pynput',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'json',
        'threading',
        'time',
        'datetime',
        'dataclasses',
        'typing',
        'pathlib',
        'os',
        'sys',
        'zipfile',
        'shutil',
        'gc',
        'collections',
        'functools',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ActionFlow',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/resources/icons/app_icon.ico' if os.path.exists('src/resources/icons/app_icon.ico') else None,
)
'''
        
        with open(self.spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print(f"✓ {self.spec_file} 생성 완료")
    
    def build_executable(self):
        """실행 파일 빌드"""
        print("실행 파일 빌드 중...")
        
        try:
            # PyInstaller 실행
            cmd = [sys.executable, "-m", "PyInstaller", "--clean", str(self.spec_file)]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            print("✓ 빌드 완료")
            print(result.stdout)
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"✗ 빌드 실패: {e}")
            print(e.stderr)
            return False
    
    def create_distribution_package(self):
        """배포 패키지 생성"""
        print("배포 패키지 생성 중...")
        
        try:
            # 배포 디렉토리 생성
            package_dir = self.project_root / "package"
            if package_dir.exists():
                shutil.rmtree(package_dir)
            package_dir.mkdir()
            
            # 실행 파일 복사
            exe_file = self.dist_dir / "ActionFlow.exe"
            if exe_file.exists():
                shutil.copy2(exe_file, package_dir)
                print("✓ 실행 파일 복사 완료")
            else:
                print("✗ 실행 파일을 찾을 수 없습니다")
                return False
            
            # README 파일 생성
            readme_content = """ActionFlow Desktop Automator

사용법:
1. ActionFlow.exe를 실행합니다
2. 프로젝트를 생성하고 액션을 추가합니다
3. 실행 버튼을 클릭하여 자동화를 시작합니다

주요 기능:
- 마우스/키보드 자동화
- 프로젝트 관리
- 코드 생성
- 백업/복원
- 설정 관리

지원 OS: Windows 10/11

개발: ActionFlow Team
"""
            
            with open(package_dir / "README.txt", 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            print("✓ README 파일 생성 완료")
            
            # 라이선스 파일 복사 (있는 경우)
            license_file = self.project_root / "LICENSE"
            if license_file.exists():
                shutil.copy2(license_file, package_dir)
                print("✓ 라이선스 파일 복사 완료")
            
            print(f"✓ 배포 패키지 생성 완료: {package_dir}")
            return True
            
        except Exception as e:
            print(f"✗ 배포 패키지 생성 실패: {e}")
            return False
    
    def run_tests(self):
        """빌드 전 테스트 실행"""
        print("테스트 실행 중...")
        
        try:
            # 기본 import 테스트
            test_imports = [
                "from src.models.project import Project",
                "from src.core.action_executor import ActionExecutor",
                "from src.gui.main_window import MainWindow",
                "from src.utils.data_manager import DataManager"
            ]
            
            for import_stmt in test_imports:
                try:
                    exec(import_stmt)
                    print(f"✓ {import_stmt}")
                except Exception as e:
                    print(f"✗ {import_stmt}: {e}")
                    return False
            
            print("✓ 모든 테스트 통과")
            return True
            
        except Exception as e:
            print(f"✗ 테스트 실행 실패: {e}")
            return False
    
    def build(self, clean: bool = True, test: bool = True):
        """
        전체 빌드 프로세스 실행
        
        Args:
            clean: 빌드 디렉토리 정리 여부
            test: 테스트 실행 여부
        """
        print("=" * 50)
        print("ActionFlow Desktop Automator 빌드 시작")
        print("=" * 50)
        
        # 1. 테스트 실행
        if test:
            if not self.run_tests():
                print("✗ 테스트 실패로 빌드를 중단합니다.")
                return False
        
        # 2. 빌드 디렉토리 정리
        if clean:
            self.clean_build_dirs()
        
        # 3. 의존성 설치
        if not self.install_dependencies():
            print("✗ 의존성 설치 실패로 빌드를 중단합니다.")
            return False
        
        # 4. spec 파일 생성
        self.create_spec_file()
        
        # 5. 실행 파일 빌드
        if not self.build_executable():
            print("✗ 실행 파일 빌드 실패.")
            return False
        
        # 6. 배포 패키지 생성
        if not self.create_distribution_package():
            print("✗ 배포 패키지 생성 실패.")
            return False
        
        print("=" * 50)
        print("🎉 빌드 완료!")
        print("=" * 50)
        print(f"실행 파일: {self.dist_dir}/ActionFlow.exe")
        print(f"배포 패키지: {self.project_root}/package/")
        print("=" * 50)
        
        return True


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ActionFlow 빌드 스크립트")
    parser.add_argument("--no-clean", action="store_true", help="빌드 디렉토리 정리하지 않음")
    parser.add_argument("--no-test", action="store_true", help="테스트 실행하지 않음")
    
    args = parser.parse_args()
    
    build_manager = BuildManager()
    success = build_manager.build(
        clean=not args.no_clean,
        test=not args.no_test
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 