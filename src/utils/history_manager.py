"""
실행 히스토리 관리
프로젝트 실행 기록을 저장하고 관리하는 시스템
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

from .config import config


@dataclass
class ExecutionRecord:
    """실행 기록 데이터 클래스"""
    id: int
    project_id: int
    project_name: str
    execution_time: str  # ISO format
    duration: float  # 실행 시간 (초)
    status: str  # "success", "failed", "cancelled"
    total_actions: int
    executed_actions: int
    error_message: Optional[str] = None
    execution_speed: str = "normal"
    notes: Optional[str] = None


class HistoryManager:
    """실행 히스토리 관리 클래스"""
    
    def __init__(self):
        """초기화"""
        self.history_file = self._get_history_file_path()
        self._ensure_history_file()
    
    def _get_history_file_path(self) -> str:
        """히스토리 파일 경로 반환"""
        data_dir = config.get_data_directory()
        return os.path.join(data_dir, "execution_history.json")
    
    def _ensure_history_file(self):
        """히스토리 파일 생성"""
        if not os.path.exists(self.history_file):
            default_history = {
                "records": [],
                "next_id": 1,
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            self._save_history_data(default_history)
    
    def _load_history_data(self) -> Dict:
        """히스토리 데이터 로드"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"히스토리 데이터 로드 중 오류: {e}")
            return {"records": [], "next_id": 1}
    
    def _save_history_data(self, data: Dict):
        """히스토리 데이터 저장"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"히스토리 데이터 저장 중 오류: {e}")
    
    def add_execution_record(self, project_id: int, project_name: str, 
                           duration: float, status: str, total_actions: int,
                           executed_actions: int, error_message: Optional[str] = None,
                           execution_speed: str = "normal", notes: Optional[str] = None) -> int:
        """
        실행 기록 추가
        
        Args:
            project_id: 프로젝트 ID
            project_name: 프로젝트 이름
            duration: 실행 시간 (초)
            status: 실행 상태
            total_actions: 총 액션 수
            executed_actions: 실행된 액션 수
            error_message: 오류 메시지
            execution_speed: 실행 속도
            notes: 메모
        
        Returns:
            생성된 기록 ID
        """
        try:
            data = self._load_history_data()
            
            # 새 기록 ID 생성
            record_id = data.get("next_id", 1)
            
            # 실행 기록 생성
            record = ExecutionRecord(
                id=record_id,
                project_id=project_id,
                project_name=project_name,
                execution_time=datetime.now().isoformat(),
                duration=duration,
                status=status,
                total_actions=total_actions,
                executed_actions=executed_actions,
                error_message=error_message,
                execution_speed=execution_speed,
                notes=notes
            )
            
            # 기록 추가
            data["records"].append(asdict(record))
            data["next_id"] = record_id + 1
            
            # 데이터 저장
            self._save_history_data(data)
            
            print(f"실행 기록이 추가되었습니다: ID {record_id}")
            return record_id
            
        except Exception as e:
            print(f"실행 기록 추가 중 오류: {e}")
            return -1
    
    def get_execution_records(self, project_id: Optional[int] = None, 
                            limit: Optional[int] = None) -> List[ExecutionRecord]:
        """
        실행 기록 조회
        
        Args:
            project_id: 특정 프로젝트 ID (None이면 모든 기록)
            limit: 조회할 기록 수 제한
        
        Returns:
            실행 기록 목록
        """
        try:
            data = self._load_history_data()
            records = data.get("records", [])
            
            # 프로젝트 ID로 필터링
            if project_id is not None:
                records = [r for r in records if r.get("project_id") == project_id]
            
            # 최신순으로 정렬
            records.sort(key=lambda x: x.get("execution_time", ""), reverse=True)
            
            # 제한 적용
            if limit is not None:
                records = records[:limit]
            
            # ExecutionRecord 객체로 변환
            return [ExecutionRecord(**record) for record in records]
            
        except Exception as e:
            print(f"실행 기록 조회 중 오류: {e}")
            return []
    
    def get_execution_record_by_id(self, record_id: int) -> Optional[ExecutionRecord]:
        """
        ID로 실행 기록 조회
        
        Args:
            record_id: 기록 ID
        
        Returns:
            실행 기록 또는 None
        """
        try:
            data = self._load_history_data()
            records = data.get("records", [])
            
            for record in records:
                if record.get("id") == record_id:
                    return ExecutionRecord(**record)
            
            return None
            
        except Exception as e:
            print(f"실행 기록 조회 중 오류: {e}")
            return None
    
    def delete_execution_record(self, record_id: int) -> bool:
        """
        실행 기록 삭제
        
        Args:
            record_id: 삭제할 기록 ID
        
        Returns:
            성공 여부
        """
        try:
            data = self._load_history_data()
            records = data.get("records", [])
            
            # 해당 기록 찾기 및 삭제
            for i, record in enumerate(records):
                if record.get("id") == record_id:
                    del records[i]
                    self._save_history_data(data)
                    print(f"실행 기록이 삭제되었습니다: ID {record_id}")
                    return True
            
            print(f"실행 기록을 찾을 수 없습니다: ID {record_id}")
            return False
            
        except Exception as e:
            print(f"실행 기록 삭제 중 오류: {e}")
            return False
    
    def clear_execution_history(self, project_id: Optional[int] = None) -> int:
        """
        실행 히스토리 정리
        
        Args:
            project_id: 특정 프로젝트 ID (None이면 모든 기록)
        
        Returns:
            삭제된 기록 수
        """
        try:
            data = self._load_history_data()
            records = data.get("records", [])
            
            if project_id is not None:
                # 특정 프로젝트 기록만 삭제
                original_count = len(records)
                records = [r for r in records if r.get("project_id") != project_id]
                deleted_count = original_count - len(records)
            else:
                # 모든 기록 삭제
                deleted_count = len(records)
                records = []
            
            data["records"] = records
            self._save_history_data(data)
            
            print(f"{deleted_count}개의 실행 기록이 삭제되었습니다.")
            return deleted_count
            
        except Exception as e:
            print(f"실행 히스토리 정리 중 오류: {e}")
            return 0
    
    def get_execution_statistics(self, project_id: Optional[int] = None) -> Dict:
        """
        실행 통계 반환
        
        Args:
            project_id: 특정 프로젝트 ID (None이면 전체 통계)
        
        Returns:
            실행 통계 정보
        """
        try:
            records = self.get_execution_records(project_id)
            
            if not records:
                return {
                    "total_executions": 0,
                    "success_count": 0,
                    "failed_count": 0,
                    "cancelled_count": 0,
                    "total_duration": 0.0,
                    "average_duration": 0.0,
                    "success_rate": 0.0
                }
            
            total_executions = len(records)
            success_count = len([r for r in records if r.status == "success"])
            failed_count = len([r for r in records if r.status == "failed"])
            cancelled_count = len([r for r in records if r.status == "cancelled"])
            
            total_duration = sum(r.duration for r in records)
            average_duration = total_duration / total_executions
            success_rate = (success_count / total_executions) * 100
            
            return {
                "total_executions": total_executions,
                "success_count": success_count,
                "failed_count": failed_count,
                "cancelled_count": cancelled_count,
                "total_duration": total_duration,
                "average_duration": average_duration,
                "success_rate": success_rate,
                "latest_execution": records[0].execution_time if records else None
            }
            
        except Exception as e:
            print(f"실행 통계 계산 중 오류: {e}")
            return {}
    
    def export_execution_history(self, export_path: str, 
                               project_id: Optional[int] = None) -> bool:
        """
        실행 히스토리 내보내기
        
        Args:
            export_path: 내보내기 파일 경로
            project_id: 특정 프로젝트 ID (None이면 모든 기록)
        
        Returns:
            성공 여부
        """
        try:
            records = self.get_execution_records(project_id)
            
            export_data = {
                "export_info": {
                    "exported_at": datetime.now().isoformat(),
                    "total_records": len(records),
                    "project_id": project_id
                },
                "records": [asdict(record) for record in records]
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"실행 히스토리가 내보내기되었습니다: {export_path}")
            return True
            
        except Exception as e:
            print(f"실행 히스토리 내보내기 중 오류: {e}")
            return False
    
    def cleanup_old_records(self, retention_days: int = 30) -> int:
        """
        오래된 실행 기록 정리
        
        Args:
            retention_days: 보관 기간 (일)
        
        Returns:
            삭제된 기록 수
        """
        try:
            data = self._load_history_data()
            records = data.get("records", [])
            
            cutoff_date = datetime.now().timestamp() - (retention_days * 24 * 3600)
            original_count = len(records)
            
            # 오래된 기록 필터링
            records = [
                record for record in records
                if datetime.fromisoformat(record.get("execution_time", "")).timestamp() > cutoff_date
            ]
            
            deleted_count = original_count - len(records)
            data["records"] = records
            self._save_history_data(data)
            
            if deleted_count > 0:
                print(f"{deleted_count}개의 오래된 실행 기록이 정리되었습니다.")
            
            return deleted_count
            
        except Exception as e:
            print(f"오래된 실행 기록 정리 중 오류: {e}")
            return 0 