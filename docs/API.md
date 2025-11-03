# ActionFlow Desktop Automator - API 문서

## 목차

- [핵심 클래스](#핵심-클래스)
- [데이터 모델](#데이터-모델)
- [유틸리티](#유틸리티)
- [예제](#예제)

## 핵심 클래스

### ActionExecutor

액션 실행을 담당하는 핵심 엔진 클래스입니다.

**위치**: `src/core/action_executor.py`

#### 주요 메서드

```python
def execute_project(
    self,
    project: Project,
    on_progress: Optional[Callable] = None,
    on_complete: Optional[Callable] = None,
    on_error: Optional[Callable] = None
) -> bool:
    """
    프로젝트 실행

    Args:
        project: 실행할 프로젝트
        on_progress: 진행 상황 콜백 (action_index, total_actions, description)
        on_complete: 완료 콜백 (success, message)
        on_error: 오류 콜백 (error_message)

    Returns:
        성공 여부
    """
```

```python
def stop_execution(self) -> None:
    """실행 중지"""

def pause_execution(self) -> None:
    """실행 일시정지"""

def resume_execution(self) -> None:
    """실행 재개"""

def get_execution_status(self) -> Dict:
    """
    실행 상태 반환

    Returns:
        실행 상태 정보 딕셔너리:
        {
            'is_running': bool,  # 실행 중 여부
            'is_paused': bool,  # 일시정지 여부
            'current_action_index': int,  # 현재 액션 인덱스
            'total_actions': int,  # 총 액션 수
            'should_stop': bool,  # 중지 요청 여부
            'progress_percent': float,  # 진행률 (0-100)
            'elapsed_time': float,  # 경과 시간 (초)
            'estimated_remaining_time': float,  # 예상 남은 시간 (초)
            'average_action_time': float  # 액션당 평균 실행 시간 (초)
        }
    """
```

#### 사용 예제

```python
from src.core.action_executor import ActionExecutor
from src.models.project import Project

# 실행 엔진 초기화
executor = ActionExecutor()

# 콜백 함수 정의
def on_progress(current, total, description):
    print(f"진행: {current}/{total} - {description}")

def on_complete(success, message):
    print(f"완료: {message}")

def on_error(error_msg):
    print(f"오류: {error_msg}")

# 프로젝트 실행
executor.execute_project(
    project=my_project,
    on_progress=on_progress,
    on_complete=on_complete,
    on_error=on_error
)
```

---

### MacroRecorder

마우스/키보드 이벤트를 실시간으로 녹화하는 클래스입니다.

**위치**: `src/core/macro_recorder.py`

#### 주요 메서드

```python
def start_recording(
    self,
    on_action_recorded: Optional[Callable] = None,
    on_recording_stopped: Optional[Callable] = None
) -> bool:
    """
    녹화 시작

    Args:
        on_action_recorded: 액션 녹화 시 콜백
        on_recording_stopped: 녹화 중지 시 콜백 (recorded_actions)

    Returns:
        성공 여부
    """

def stop_recording(self) -> List[Dict]:
    """
    녹화 중지

    Returns:
        녹화된 액션 목록
    """

def save_recording_as_project(
    self,
    project_name: str,
    description: str = ""
) -> Optional[int]:
    """
    녹화된 액션을 프로젝트로 저장

    Returns:
        생성된 프로젝트 ID
    """
```

#### 사용 예제

```python
from src.core.macro_recorder import MacroRecorder

recorder = MacroRecorder()

# 녹화 시작
recorder.start_recording(
    on_action_recorded=lambda action: print(f"녹화: {action['description']}")
)

# ... 사용자 작업 ...

# 녹화 중지 및 저장
actions = recorder.stop_recording()
project_id = recorder.save_recording_as_project("내 매크로", "자동으로 녹화됨")
```

---

### ProjectManager

프로젝트 CRUD 및 검색 기능을 제공하는 클래스입니다.

**위치**: `src/core/project_manager.py`

#### 주요 메서드

```python
def create_project(
    self,
    name: str,
    description: str = "",
    category: str = "기타",
    favorite: bool = False
) -> Project:
    """새 프로젝트 생성"""

def get_all_projects(self) -> List[Project]:
    """모든 프로젝트 반환"""

def get_project_by_id(self, project_id: int) -> Optional[Project]:
    """ID로 프로젝트 조회"""

def update_project(self, project: Project) -> bool:
    """프로젝트 업데이트"""

def delete_project(self, project_id: int) -> bool:
    """프로젝트 삭제"""

def search_projects(self, keyword: str) -> List[Project]:
    """프로젝트 검색"""

def duplicate_project(
    self,
    project_id: int,
    new_name: str = None
) -> Optional[Project]:
    """프로젝트 복사"""
```

---

### DataManager

JSON 파일 기반 데이터 저장/로드를 담당하는 클래스입니다.

**위치**: `src/utils/data_manager.py`

#### 주요 메서드

```python
def save_project(self, project: Project) -> bool:
    """프로젝트 저장"""

def get_project_by_id(self, project_id: int) -> Optional[Project]:
    """프로젝트 조회"""

def get_all_projects(self) -> List[Project]:
    """모든 프로젝트 반환"""

def delete_project(self, project_id: int) -> bool:
    """프로젝트 삭제"""

def export_project(self, project_id: int, export_path: str) -> bool:
    """프로젝트 내보내기"""

def import_project(self, import_path: str) -> Optional[Project]:
    """프로젝트 가져오기"""
```

---

### CodeGenerator

프로젝트를 Python 스크립트로 변환하는 클래스입니다.

**위치**: `src/core/code_generator.py`

#### 주요 메서드

```python
def generate_executable_script(
    self,
    project: Project,
    output_path: str
) -> bool:
    """
    실행 가능한 Python 스크립트 생성

    Args:
        project: 프로젝트
        output_path: 출력 파일 경로

    Returns:
        성공 여부
    """

def get_code_statistics(self, project: Project) -> Dict[str, Any]:
    """
    코드 통계 반환

    Returns:
        {
            'total_actions': int,
            'estimated_lines': int,
            'complexity': str,
            'action_types': Dict[str, int]
        }
    """
```

---

## 데이터 모델

### Project

**위치**: `src/models/project.py`

```python
@dataclass
class Project:
    id: int
    name: str
    description: str
    category: str
    favorite: bool
    actions: List[Dict]
    created_at: str
    updated_at: str

    def add_action(self, action: Dict) -> None:
        """액션 추가"""

    def remove_action(self, action_id: int) -> bool:
        """액션 삭제"""

    def get_action_by_id(self, action_id: int) -> Optional[Dict]:
        """액션 조회"""

    def move_action_up(self, action_id: int) -> bool:
        """액션 위로 이동"""

    def move_action_down(self, action_id: int) -> bool:
        """액션 아래로 이동"""
```

### Action

**위치**: `src/models/action.py`

```python
@dataclass
class Action:
    id: int
    order_index: int
    action_type: str
    description: str
    parameters: Dict[str, Any]

class ActionTypes:
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

    # 클립보드 액션
    CLIPBOARD_COPY = "clipboard_copy"
    CLIPBOARD_PASTE = "clipboard_paste"

    # 기타 액션
    DELAY = "delay"
    SCREENSHOT = "screenshot"
    CONDITIONAL = "conditional"
```

### Settings

**위치**: `src/models/settings.py`

```python
@dataclass
class Settings:
    theme: str              # "light" | "dark"
    language: str           # "ko" | "en"
    window_width: int
    window_height: int
    execution_speed: str    # "fast" | "normal" | "slow"
    default_delay: float
    safety_failsafe: bool
    auto_save: bool
    backup_interval: int
    max_history: int
    enable_logging: bool
    log_level: str          # "DEBUG" | "INFO" | "WARNING" | "ERROR"
```

---

## 유틸리티

### Logger

**위치**: `src/utils/logger.py`

```python
from src.utils.logger import get_logger

# 로거 가져오기
logger = get_logger(__name__)

# 로그 레벨별 사용
logger.debug("디버그 메시지")
logger.info("정보 메시지")
logger.warning("경고 메시지")
logger.error("에러 메시지")
logger.critical("치명적 에러")

# 예외 정보 포함
try:
    # 코드
except Exception as e:
    logger.error(f"오류 발생: {str(e)}", exc_info=True)
```

### JSONValidator

**위치**: `src/utils/json_validator.py`

```python
from src.utils.json_validator import JSONValidator

# 프로젝트 파일 검증
is_valid, errors = JSONValidator.validate_projects_file(data)
if not is_valid:
    print(f"검증 실패: {errors}")

# 개별 프로젝트 검증
is_valid, errors = JSONValidator.validate_project(project_data)

# 손상된 파일 복구
repaired_data = JSONValidator.repair_projects_file(damaged_data)
```

### Config

**위치**: `src/utils/config.py`

```python
from src.utils.config import config

# 애플리케이션 정보
app_name = config.get_app_name()
app_version = config.get_app_version()

# 경로 정보
data_dir = config.get_data_directory()
log_dir = config.get_log_directory()

# 설정 정보
theme_colors = config.get_theme_colors()
execution_delay = config.get_execution_delay()

# 플랫폼 확인
if config.is_windows():
    # Windows 전용 코드
elif config.is_macos():
    # macOS 전용 코드
elif config.is_linux():
    # Linux 전용 코드
```

---

## 예제

### 예제 1: 프로그램 방식으로 프로젝트 생성 및 실행

```python
from src.core.project_manager import ProjectManager
from src.core.action_executor import ActionExecutor
from src.models.action import ActionFactory

# 프로젝트 매니저 초기화
pm = ProjectManager()

# 새 프로젝트 생성
project = pm.create_project(
    name="자동 로그인",
    description="웹사이트 자동 로그인 매크로",
    category="웹 자동화"
)

# 액션 추가
action_id = 1

# 1. 마우스 이동
project.add_action({
    'id': action_id,
    'order_index': 1,
    'action_type': 'mouse_move',
    'description': '로그인 버튼으로 이동',
    'parameters': {'x': 500, 'y': 300, 'duration': 0.5}
})
action_id += 1

# 2. 마우스 클릭
project.add_action({
    'id': action_id,
    'order_index': 2,
    'action_type': 'mouse_click',
    'description': '로그인 버튼 클릭',
    'parameters': {'x': 500, 'y': 300, 'button': 'left', 'clicks': 1}
})
action_id += 1

# 3. 키보드 입력
project.add_action({
    'id': action_id,
    'order_index': 3,
    'action_type': 'keyboard_type',
    'description': '사용자 이름 입력',
    'parameters': {'text': 'myusername', 'interval': 0.1}
})

# 프로젝트 저장
pm.update_project(project)

# 프로젝트 실행
executor = ActionExecutor()
executor.execute_project(
    project=project,
    on_complete=lambda success, msg: print(f"실행 완료: {msg}")
)
```

### 예제 2: 매크로 녹화 및 저장

```python
from src.core.macro_recorder import MacroRecorder
import time

recorder = MacroRecorder()

print("3초 후 녹화 시작...")
time.sleep(3)

# 녹화 시작
recorder.start_recording(
    on_action_recorded=lambda action: print(f"✓ {action['description']}")
)

print("녹화 중... (10초 후 자동 종료)")
time.sleep(10)

# 녹화 중지 및 프로젝트로 저장
actions = recorder.stop_recording()
project_id = recorder.save_recording_as_project(
    project_name="녹화된 매크로",
    description="10초간 녹화한 작업"
)

print(f"프로젝트 저장 완료: ID={project_id}, 액션 수={len(actions)}")
```

### 예제 3: Python 스크립트 생성

```python
from src.core.project_manager import ProjectManager
from src.core.code_generator import CodeGenerator

pm = ProjectManager()
generator = CodeGenerator()

# 프로젝트 로드
project = pm.get_project_by_id(1)

# Python 스크립트 생성
output_file = "generated_automation.py"
success = generator.generate_executable_script(project, output_file)

if success:
    print(f"스크립트 생성 완료: {output_file}")

    # 코드 통계 확인
    stats = generator.get_code_statistics(project)
    print(f"총 액션: {stats['total_actions']}개")
    print(f"예상 라인 수: {stats['estimated_lines']}줄")
    print(f"복잡도: {stats['complexity']}")
```

### 예제 4: 실행 상태 모니터링

```python
from src.core.project_manager import ProjectManager
from src.core.action_executor import ActionExecutor
import time
import threading

pm = ProjectManager()
executor = ActionExecutor()

# 프로젝트 로드
project = pm.get_project_by_id(1)

# 실행 상태 모니터링 함수
def monitor_execution():
    while True:
        status = executor.get_execution_status()

        if status['is_running']:
            print(f"\r진행률: {status['progress_percent']:.1f}% | "
                  f"액션: {status['current_action_index'] + 1}/{status['total_actions']} | "
                  f"경과 시간: {status['elapsed_time']:.1f}초 | "
                  f"예상 남은 시간: {status['estimated_remaining_time']:.1f}초",
                  end='', flush=True)
        else:
            break

        time.sleep(0.5)

    print("\n실행 완료!")

# 프로젝트 실행
def on_complete(success, message):
    print(f"\n완료: {message}")

executor.execute_project(
    project=project,
    on_complete=on_complete
)

# 모니터링 시작
monitor_thread = threading.Thread(target=monitor_execution)
monitor_thread.start()
monitor_thread.join()
```

### 예제 5: 실행 상태 기반 제어

```python
from src.core.action_executor import ActionExecutor
import time

executor = ActionExecutor()

# 프로젝트 실행 시작
executor.execute_project(project=my_project)

# 특정 조건에서 일시정지
while True:
    status = executor.get_execution_status()

    if not status['is_running']:
        break

    # 50% 완료 시 일시정지
    if status['progress_percent'] >= 50 and not status['is_paused']:
        print("50% 완료, 잠시 일시정지합니다...")
        executor.pause_execution()
        time.sleep(5)  # 5초 대기
        print("재개합니다...")
        executor.resume_execution()

    # 예상 시간이 너무 길면 중지
    if status['estimated_remaining_time'] > 300:  # 5분 이상
        print("예상 시간이 너무 깁니다. 실행을 중지합니다.")
        executor.stop_execution()
        break

    time.sleep(1)

print("실행 종료")
```

---

## 추가 리소스

- [사용자 가이드](USER_GUIDE.md)
- [README](../README.md)
- [GitHub Issues](https://github.com/Photometry4040/actionflow_desktop/issues)

---

**© 2025 Photometry4040. All rights reserved.**
