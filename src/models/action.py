"""
액션 데이터 모델
JSON 기반 데이터 저장을 위한 액션 클래스
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import json


@dataclass
class Action:
    """액션 데이터 모델"""

    id: int
    order_index: int
    action_type: str
    description: str
    parameters: Dict[str, Any]
    tags: list = None

    def __post_init__(self):
        """초기화 후 처리"""
        if self.tags is None:
            self.tags = []
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return asdict(self)
    
    def to_json(self) -> str:
        """JSON 문자열로 변환"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Action':
        """딕셔너리에서 액션 생성"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Action':
        """JSON 문자열에서 액션 생성"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def get_parameter(self, key: str, default: Any = None) -> Any:
        """파라미터 값 가져오기"""
        return self.parameters.get(key, default)
    
    def set_parameter(self, key: str, value: Any):
        """파라미터 값 설정"""
        self.parameters[key] = value
    
    def validate(self) -> bool:
        """액션 유효성 검사"""
        required_fields = ['id', 'order_index', 'action_type', 'description']
        for field in required_fields:
            if not hasattr(self, field) or getattr(self, field) is None:
                return False
        return True

    def add_tag(self, tag: str):
        """
        태그 추가

        Args:
            tag: 추가할 태그
        """
        if self.tags is None:
            self.tags = []
        if tag and tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str):
        """
        태그 제거

        Args:
            tag: 제거할 태그
        """
        if self.tags and tag in self.tags:
            self.tags.remove(tag)

    def has_tag(self, tag: str) -> bool:
        """
        태그 존재 여부 확인

        Args:
            tag: 확인할 태그

        Returns:
            태그 존재 여부
        """
        return self.tags is not None and tag in self.tags

    def get_tags(self) -> list:
        """태그 목록 반환"""
        return self.tags if self.tags is not None else []


class ActionTypes:
    """액션 타입 상수"""
    
    # 마우스 액션
    MOUSE_MOVE = "mouse_move"
    MOUSE_CLICK = "mouse_click"
    MOUSE_DOUBLE_CLICK = "mouse_double_click"
    MOUSE_RIGHT_CLICK = "mouse_right_click"
    MOUSE_DRAG = "mouse_drag"
    
    # 키보드 액션
    KEYBOARD_TYPE = "keyboard_type"
    KEYBOARD_PRESS = "keyboard_press"
    KEYBOARD_HOTKEY = "keyboard_hotkey"
    KEY_COMBINATION = "key_combination"

    # 클립보드 액션
    CLIPBOARD_COPY = "clipboard_copy"
    CLIPBOARD_PASTE = "clipboard_paste"

    # 이미지 인식 액션
    IMAGE_CLICK = "image_click"
    WAIT_FOR_IMAGE = "wait_for_image"
    FIND_IMAGE = "find_image"
    WAIT_FOR_ANY_IMAGE = "wait_for_any_image"

    # Excel/CSV 데이터 연동 액션
    EXCEL_LOAD_DATA = "excel_load_data"
    EXCEL_LOOP_START = "excel_loop_start"
    EXCEL_LOOP_END = "excel_loop_end"
    EXCEL_GET_CELL = "excel_get_cell"
    EXCEL_SAVE_RESULTS = "excel_save_results"

    # 기타 액션
    DELAY = "delay"
    SCREENSHOT = "screenshot"
    CONDITIONAL = "conditional"
    
    @classmethod
    def get_all_types(cls) -> list:
        """모든 액션 타입 반환"""
        return [
            cls.MOUSE_MOVE,
            cls.MOUSE_CLICK,
            cls.MOUSE_DOUBLE_CLICK,
            cls.MOUSE_RIGHT_CLICK,
            cls.MOUSE_DRAG,
            cls.KEYBOARD_TYPE,
            cls.KEYBOARD_PRESS,
            cls.KEYBOARD_HOTKEY,
            cls.KEY_COMBINATION,
            cls.CLIPBOARD_COPY,
            cls.CLIPBOARD_PASTE,
            cls.IMAGE_CLICK,
            cls.WAIT_FOR_IMAGE,
            cls.FIND_IMAGE,
            cls.WAIT_FOR_ANY_IMAGE,
            cls.EXCEL_LOAD_DATA,
            cls.EXCEL_LOOP_START,
            cls.EXCEL_LOOP_END,
            cls.EXCEL_GET_CELL,
            cls.EXCEL_SAVE_RESULTS,
            cls.DELAY,
            cls.SCREENSHOT,
            cls.CONDITIONAL
        ]
    
    @classmethod
    def get_display_name(cls, action_type: str) -> str:
        """액션 타입의 표시 이름 반환"""
        display_names = {
            cls.MOUSE_MOVE: "마우스 이동",
            cls.MOUSE_CLICK: "마우스 클릭",
            cls.MOUSE_DOUBLE_CLICK: "마우스 더블클릭",
            cls.MOUSE_RIGHT_CLICK: "마우스 우클릭",
            cls.MOUSE_DRAG: "마우스 드래그",
            cls.KEYBOARD_TYPE: "키보드 입력",
            cls.KEYBOARD_PRESS: "키보드 누르기",
            cls.KEYBOARD_HOTKEY: "키보드 단축키",
            cls.KEY_COMBINATION: "키 조합",
            cls.CLIPBOARD_COPY: "복사",
            cls.CLIPBOARD_PASTE: "붙여넣기",
            cls.IMAGE_CLICK: "이미지 클릭",
            cls.WAIT_FOR_IMAGE: "이미지 대기",
            cls.FIND_IMAGE: "이미지 찾기",
            cls.WAIT_FOR_ANY_IMAGE: "여러 이미지 중 하나 대기",
            cls.EXCEL_LOAD_DATA: "Excel/CSV 로드",
            cls.EXCEL_LOOP_START: "Excel 루프 시작",
            cls.EXCEL_LOOP_END: "Excel 루프 종료",
            cls.EXCEL_GET_CELL: "Excel 셀 값 가져오기",
            cls.EXCEL_SAVE_RESULTS: "Excel/CSV 저장",
            cls.DELAY: "지연",
            cls.SCREENSHOT: "스크린샷",
            cls.CONDITIONAL: "조건부 실행"
        }
        return display_names.get(action_type, action_type)


class ActionFactory:
    """액션 생성 팩토리"""
    
    @staticmethod
    def create_mouse_move(id: int, order_index: int, x: int, y: int, description: str = "") -> Action:
        """마우스 이동 액션 생성"""
        return Action(
            id=id,
            order_index=order_index,
            action_type=ActionTypes.MOUSE_MOVE,
            description=description or f"마우스를 ({x}, {y})로 이동",
            parameters={"x": x, "y": y}
        )
    
    @staticmethod
    def create_mouse_click(id: int, order_index: int, x: int, y: int, button: str = "left", description: str = "") -> Action:
        """마우스 클릭 액션 생성"""
        return Action(
            id=id,
            order_index=order_index,
            action_type=ActionTypes.MOUSE_CLICK,
            description=description or f"마우스 {button} 클릭 ({x}, {y})",
            parameters={"x": x, "y": y, "button": button}
        )
    
    @staticmethod
    def create_keyboard_type(id: int, order_index: int, text: str, description: str = "") -> Action:
        """키보드 입력 액션 생성"""
        return Action(
            id=id,
            order_index=order_index,
            action_type=ActionTypes.KEYBOARD_TYPE,
            description=description or f"키보드 입력: {text}",
            parameters={"text": text}
        )
    
    @staticmethod
    def create_delay(id: int, order_index: int, seconds: float, description: str = "") -> Action:
        """지연 액션 생성"""
        return Action(
            id=id,
            order_index=order_index,
            action_type=ActionTypes.DELAY,
            description=description or f"{seconds}초 대기",
            parameters={"seconds": seconds}
        )
    
    @staticmethod
    def create_hotkey(id: int, order_index: int, keys: list, description: str = "") -> Action:
        """단축키 액션 생성"""
        return Action(
            id=id,
            order_index=order_index,
            action_type=ActionTypes.KEYBOARD_HOTKEY,
            description=description or f"단축키: {'+'.join(keys)}",
            parameters={"keys": keys}
        ) 