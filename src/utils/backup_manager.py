"""
백업/복원 관리
데이터 백업 및 복원 기능
"""
import os
import shutil
import json
import zipfile
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from .data_manager import DataManager
from .config import config


class BackupManager:
    """백업 관리 클래스"""
    
    def __init__(self):
        """초기화"""
        self.data_manager = DataManager()
        self.backup_dir = self._get_backup_directory()
        self._ensure_backup_directory()
    
    def _get_backup_directory(self) -> str:
        """백업 디렉토리 경로 반환"""
        app_data_dir = config.get_data_directory()
        return os.path.join(app_data_dir, "backups")
    
    def _ensure_backup_directory(self):
        """백업 디렉토리 생성"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_backup(self, backup_name: Optional[str] = None, include_settings: bool = True) -> Optional[str]:
        """
        백업 생성
        
        Args:
            backup_name: 백업 이름 (None이면 자동 생성)
            include_settings: 설정 포함 여부
        
        Returns:
            생성된 백업 파일 경로
        """
        try:
            # 백업 이름 생성
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"backup_{timestamp}"
            
            # 백업 파일 경로
            backup_file = os.path.join(self.backup_dir, f"{backup_name}.zip")
            
            # ZIP 파일 생성
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 프로젝트 데이터 백업
                self._backup_projects(zipf)
                
                # 설정 데이터 백업
                if include_settings:
                    self._backup_settings(zipf)
                
                # 백업 메타데이터 추가
                self._add_backup_metadata(zipf, backup_name, include_settings)
            
            print(f"백업이 생성되었습니다: {backup_file}")
            return backup_file
            
        except Exception as e:
            print(f"백업 생성 중 오류가 발생했습니다: {e}")
            return None
    
    def _backup_projects(self, zipf: zipfile.ZipFile):
        """프로젝트 데이터 백업"""
        projects_file = self.data_manager.projects_file
        
        if os.path.exists(projects_file):
            # 프로젝트 데이터 읽기
            with open(projects_file, 'r', encoding='utf-8') as f:
                projects_data = json.load(f)
            
            # ZIP에 추가
            zipf.writestr('projects.json', json.dumps(projects_data, ensure_ascii=False, indent=2))
    
    def _backup_settings(self, zipf: zipfile.ZipFile):
        """설정 데이터 백업"""
        settings_file = self.data_manager.settings_file
        
        if os.path.exists(settings_file):
            # 설정 데이터 읽기
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings_data = json.load(f)
            
            # ZIP에 추가
            zipf.writestr('settings.json', json.dumps(settings_data, ensure_ascii=False, indent=2))
    
    def _add_backup_metadata(self, zipf: zipfile.ZipFile, backup_name: str, include_settings: bool):
        """백업 메타데이터 추가"""
        metadata = {
            "backup_name": backup_name,
            "created_at": datetime.now().isoformat(),
            "version": config.get_app_version(),
            "include_settings": include_settings,
            "description": f"ActionFlow Desktop Automator 백업 - {backup_name}"
        }
        
        zipf.writestr('backup_metadata.json', json.dumps(metadata, ensure_ascii=False, indent=2))
    
    def restore_backup(self, backup_file: str, restore_settings: bool = True) -> bool:
        """
        백업 복원
        
        Args:
            backup_file: 복원할 백업 파일 경로
            restore_settings: 설정 복원 여부
        
        Returns:
            성공 여부
        """
        try:
            if not os.path.exists(backup_file):
                print(f"백업 파일을 찾을 수 없습니다: {backup_file}")
                return False
            
            # 백업 파일 검증
            if not self._validate_backup_file(backup_file):
                print("백업 파일이 손상되었거나 유효하지 않습니다.")
                return False
            
            # 기존 데이터 백업 (안전을 위해)
            safety_backup = self.create_backup("safety_backup_before_restore", True)
            
            # ZIP 파일에서 복원
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                # 프로젝트 데이터 복원
                if 'projects.json' in zipf.namelist():
                    self._restore_projects(zipf)
                
                # 설정 데이터 복원
                if restore_settings and 'settings.json' in zipf.namelist():
                    self._restore_settings(zipf)
            
            print(f"백업이 성공적으로 복원되었습니다: {backup_file}")
            return True
            
        except Exception as e:
            print(f"백업 복원 중 오류가 발생했습니다: {e}")
            return False
    
    def _validate_backup_file(self, backup_file: str) -> bool:
        """백업 파일 검증"""
        try:
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                # 필수 파일 확인
                required_files = ['projects.json', 'backup_metadata.json']
                file_list = zipf.namelist()
                
                for required_file in required_files:
                    if required_file not in file_list:
                        return False
                
                # 메타데이터 확인
                metadata_content = zipf.read('backup_metadata.json')
                metadata = json.loads(metadata_content)
                
                if 'version' not in metadata or 'created_at' not in metadata:
                    return False
                
                return True
                
        except Exception:
            return False
    
    def _restore_projects(self, zipf: zipfile.ZipFile):
        """프로젝트 데이터 복원"""
        projects_content = zipf.read('projects.json')
        projects_data = json.loads(projects_content)
        
        # 프로젝트 파일에 저장
        with open(self.data_manager.projects_file, 'w', encoding='utf-8') as f:
            json.dump(projects_data, f, ensure_ascii=False, indent=2)
    
    def _restore_settings(self, zipf: zipfile.ZipFile):
        """설정 데이터 복원"""
        settings_content = zipf.read('settings.json')
        settings_data = json.loads(settings_content)
        
        # 설정 파일에 저장
        with open(self.data_manager.settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings_data, f, ensure_ascii=False, indent=2)
    
    def get_backup_list(self) -> List[Dict]:
        """백업 목록 반환"""
        backups = []
        
        if not os.path.exists(self.backup_dir):
            return backups
        
        for filename in os.listdir(self.backup_dir):
            if filename.endswith('.zip'):
                backup_file = os.path.join(self.backup_dir, filename)
                backup_info = self._get_backup_info(backup_file)
                if backup_info:
                    backups.append(backup_info)
        
        # 생성일 기준으로 정렬 (최신순)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        return backups
    
    def _get_backup_info(self, backup_file: str) -> Optional[Dict]:
        """백업 파일 정보 반환"""
        try:
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                if 'backup_metadata.json' not in zipf.namelist():
                    return None
                
                metadata_content = zipf.read('backup_metadata.json')
                metadata = json.loads(metadata_content)
                
                # 파일 크기 추가
                file_size = os.path.getsize(backup_file)
                
                return {
                    'filename': os.path.basename(backup_file),
                    'filepath': backup_file,
                    'backup_name': metadata.get('backup_name', 'Unknown'),
                    'created_at': metadata.get('created_at', ''),
                    'version': metadata.get('version', 'Unknown'),
                    'include_settings': metadata.get('include_settings', False),
                    'file_size': file_size,
                    'file_size_mb': round(file_size / (1024 * 1024), 2)
                }
                
        except Exception:
            return None
    
    def delete_backup(self, backup_file: str) -> bool:
        """
        백업 삭제
        
        Args:
            backup_file: 삭제할 백업 파일 경로
        
        Returns:
            성공 여부
        """
        try:
            if os.path.exists(backup_file):
                os.remove(backup_file)
                print(f"백업이 삭제되었습니다: {backup_file}")
                return True
            else:
                print(f"백업 파일을 찾을 수 없습니다: {backup_file}")
                return False
                
        except Exception as e:
            print(f"백업 삭제 중 오류가 발생했습니다: {e}")
            return False
    
    def cleanup_old_backups(self, retention_days: int = 30) -> int:
        """
        오래된 백업 정리
        
        Args:
            retention_days: 보관 기간 (일)
        
        Returns:
            삭제된 백업 수
        """
        try:
            deleted_count = 0
            cutoff_date = datetime.now().timestamp() - (retention_days * 24 * 3600)
            
            for backup_info in self.get_backup_list():
                backup_file = backup_info['filepath']
                file_time = os.path.getmtime(backup_file)
                
                if file_time < cutoff_date:
                    if self.delete_backup(backup_file):
                        deleted_count += 1
            
            if deleted_count > 0:
                print(f"{deleted_count}개의 오래된 백업이 정리되었습니다.")
            
            return deleted_count
            
        except Exception as e:
            print(f"백업 정리 중 오류가 발생했습니다: {e}")
            return 0
    
    def export_backup(self, backup_file: str, export_path: str) -> bool:
        """
        백업 내보내기
        
        Args:
            backup_file: 내보낼 백업 파일 경로
            export_path: 내보내기 경로
        
        Returns:
            성공 여부
        """
        try:
            if not os.path.exists(backup_file):
                print(f"백업 파일을 찾을 수 없습니다: {backup_file}")
                return False
            
            # 파일 복사
            shutil.copy2(backup_file, export_path)
            print(f"백업이 내보내기되었습니다: {export_path}")
            return True
            
        except Exception as e:
            print(f"백업 내보내기 중 오류가 발생했습니다: {e}")
            return False
    
    def import_backup(self, import_path: str) -> Optional[str]:
        """
        백업 가져오기
        
        Args:
            import_path: 가져올 백업 파일 경로
        
        Returns:
            가져온 백업 파일 경로
        """
        try:
            if not os.path.exists(import_path):
                print(f"가져올 백업 파일을 찾을 수 없습니다: {import_path}")
                return None
            
            # 백업 파일 검증
            if not self._validate_backup_file(import_path):
                print("백업 파일이 손상되었거나 유효하지 않습니다.")
                return None
            
            # 백업 디렉토리로 복사
            filename = os.path.basename(import_path)
            dest_path = os.path.join(self.backup_dir, filename)
            
            shutil.copy2(import_path, dest_path)
            print(f"백업이 가져와졌습니다: {dest_path}")
            return dest_path
            
        except Exception as e:
            print(f"백업 가져오기 중 오류가 발생했습니다: {e}")
            return None
    
    def get_backup_statistics(self) -> Dict:
        """백업 통계 반환"""
        backups = self.get_backup_list()
        
        total_backups = len(backups)
        total_size = sum(backup['file_size'] for backup in backups)
        total_size_mb = round(total_size / (1024 * 1024), 2)
        
        # 최근 백업
        latest_backup = backups[0] if backups else None
        
        # 백업 크기별 분포
        size_distribution = {
            'small': len([b for b in backups if b['file_size_mb'] < 1]),
            'medium': len([b for b in backups if 1 <= b['file_size_mb'] < 5]),
            'large': len([b for b in backups if b['file_size_mb'] >= 5])
        }
        
        return {
            'total_backups': total_backups,
            'total_size_mb': total_size_mb,
            'latest_backup': latest_backup,
            'size_distribution': size_distribution,
            'backup_directory': self.backup_dir
        } 