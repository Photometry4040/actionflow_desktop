"""
프로젝트 데이터 모델
JSON 기반 데이터 저장을 위한 프로젝트 클래스
"""
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import json


@dataclass
class Project:
    """프로젝트 데이터 모델"""

    id: int
    name: str
    description: str
    category: str
    favorite: bool = False
    created_at: str = None
    updated_at: str = None
    actions: List[Dict] = None
    tags: List[str] = None  # 태그 목록
    last_executed_at: str = None  # 마지막 실행 시간
    execution_count: int = 0  # 실행 횟수

    def __post_init__(self):
        """초기화 후 처리"""
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()
        if self.actions is None:
            self.actions = []
        if self.tags is None:
            self.tags = []
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return asdict(self)
    
    def to_json(self) -> str:
        """JSON 문자열로 변환"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Project':
        """딕셔너리에서 프로젝트 생성"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Project':
        """JSON 문자열에서 프로젝트 생성"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def update_timestamp(self):
        """업데이트 시간 갱신"""
        self.updated_at = datetime.now().isoformat()
    
    def add_action(self, action: Dict):
        """액션 추가"""
        self.actions.append(action)
        self.update_timestamp()
    
    def remove_action(self, action_id: int):
        """액션 제거"""
        self.actions = [action for action in self.actions if action.get('id') != action_id]
        self.update_timestamp()
    
    def get_action_count(self) -> int:
        """액션 개수 반환"""
        return len(self.actions)
    
    def is_empty(self) -> bool:
        """빈 프로젝트인지 확인"""
        return len(self.actions) == 0
    
    def get_action_by_id(self, action_id: int) -> Optional[Dict]:
        """ID로 액션 찾기"""
        for action in self.actions:
            if action.get('id') == action_id:
                return action
        return None
    
    def move_action_up(self, action_id: int) -> bool:
        """액션을 위로 이동"""
        if len(self.actions) <= 1:
            return False
        
        # 액션 찾기
        action_index = None
        for i, action in enumerate(self.actions):
            if action.get('id') == action_id:
                action_index = i
                break
        
        if action_index is None or action_index == 0:
            return False
        
        # 액션 순서 변경
        self.actions[action_index], self.actions[action_index - 1] = \
            self.actions[action_index - 1], self.actions[action_index]
        
        # order_index 업데이트
        self.actions[action_index]['order_index'] = action_index + 1
        self.actions[action_index - 1]['order_index'] = action_index
        
        self.update_timestamp()
        return True
    
    def move_action_down(self, action_id: int) -> bool:
        """액션을 아래로 이동"""
        if len(self.actions) <= 1:
            return False
        
        # 액션 찾기
        action_index = None
        for i, action in enumerate(self.actions):
            if action.get('id') == action_id:
                action_index = i
                break
        
        if action_index is None or action_index == len(self.actions) - 1:
            return False
        
        # 액션 순서 변경
        self.actions[action_index], self.actions[action_index + 1] = \
            self.actions[action_index + 1], self.actions[action_index]
        
        # order_index 업데이트
        self.actions[action_index]['order_index'] = action_index + 1
        self.actions[action_index + 1]['order_index'] = action_index + 2
        
        self.update_timestamp()
        return True
    
    def reorder_actions(self):
        """액션들의 order_index를 순서대로 재정렬"""
        for i, action in enumerate(self.actions):
            action['order_index'] = i + 1
        self.update_timestamp()
    
    def update_action(self, action_id: int, updated_action: Dict) -> bool:
        """
        액션 업데이트
        
        Args:
            action_id: 업데이트할 액션 ID
            updated_action: 업데이트된 액션 데이터
        
        Returns:
            성공 여부
        """
        for i, action in enumerate(self.actions):
            if action.get('id') == action_id:
                # 기존 ID와 order_index 유지
                updated_action['id'] = action_id
                updated_action['order_index'] = action.get('order_index', i + 1)
                
                # 액션 업데이트
                self.actions[i] = updated_action
                self.update_timestamp()
                return True

        return False

    # 태그 관리 메서드
    def add_tag(self, tag: str) -> bool:
        """
        태그 추가

        Args:
            tag: 추가할 태그

        Returns:
            성공 여부 (중복 시 False)
        """
        tag = tag.strip()
        if not tag or tag in self.tags:
            return False

        self.tags.append(tag)
        self.update_timestamp()
        return True

    def remove_tag(self, tag: str) -> bool:
        """
        태그 제거

        Args:
            tag: 제거할 태그

        Returns:
            성공 여부
        """
        if tag in self.tags:
            self.tags.remove(tag)
            self.update_timestamp()
            return True
        return False

    def has_tag(self, tag: str) -> bool:
        """태그 포함 여부 확인"""
        return tag in self.tags

    def get_tags(self) -> List[str]:
        """태그 목록 반환"""
        return self.tags.copy()

    # 실행 이력 메서드
    def record_execution(self):
        """실행 기록 업데이트"""
        self.last_executed_at = datetime.now().isoformat()
        self.execution_count += 1
        self.update_timestamp()

    def get_last_executed(self) -> Optional[str]:
        """마지막 실행 시간 반환"""
        return self.last_executed_at

    def get_execution_count(self) -> int:
        """실행 횟수 반환"""
        return self.execution_count 