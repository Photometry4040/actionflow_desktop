"""
코드 생성 기능
프로젝트의 액션들을 Python 스크립트로 변환
"""
import os
from typing import List, Dict, Optional
from datetime import datetime

from ..models.project import Project
from ..utils.config import config


class CodeGenerator:
    """코드 생성 클래스"""
    
    def __init__(self):
        """초기화"""
        self.template_dir = os.path.join(os.path.dirname(__file__), '..', 'resources', 'templates')
        self._ensure_template_directory()
    
    def _ensure_template_directory(self):
        """템플릿 디렉토리 생성"""
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
    
    def generate_python_script(self, project: Project, output_path: Optional[str] = None) -> str:
        """
        Python 스크립트 생성
        
        Args:
            project: 변환할 프로젝트
            output_path: 출력 파일 경로 (None이면 문자열 반환)
        
        Returns:
            생성된 Python 코드
        """
        # 헤더 생성
        header = self._generate_header(project)
        
        # 임포트 섹션
        imports = self._generate_imports()
        
        # 설정 섹션
        settings = self._generate_settings()
        
        # 메인 함수
        main_function = self._generate_main_function(project)
        
        # 실행 섹션
        execution = self._generate_execution_section()
        
        # 전체 코드 조합
        full_code = f"{header}\n\n{imports}\n\n{settings}\n\n{main_function}\n\n{execution}"
        
        # 파일로 저장
        if output_path:
            self._save_to_file(full_code, output_path)
        
        return full_code
    
    def _generate_header(self, project: Project) -> str:
        """헤더 생성"""
        return f'''"""
{project.name}
{project.description}

생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
생성 도구: ActionFlow Desktop Automator
"""

# -*- coding: utf-8 -*-'''
    
    def _generate_imports(self) -> str:
        """임포트 섹션 생성"""
        return '''# 필수 라이브러리 임포트
import time
import pyautogui
import pyperclip

# 안전 장치 설정
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1'''
    
    def _generate_settings(self) -> str:
        """설정 섹션 생성"""
        return '''# 실행 설정
EXECUTION_SPEED = "normal"  # "fast", "normal", "slow"
DEFAULT_DELAY = 0.5
SAFETY_FAILSAFE = True

# 실행 속도에 따른 지연 시간 설정
if EXECUTION_SPEED == "fast":
    DEFAULT_DELAY = 0.1
elif EXECUTION_SPEED == "slow":
    DEFAULT_DELAY = 1.0'''
    
    def _generate_main_function(self, project: Project) -> str:
        """메인 함수 생성"""
        function_code = f'''def run_{project.name.lower().replace(' ', '_').replace('-', '_')}():
    """
    {project.name} 실행 함수
    {project.description}
    """
    print(f"프로젝트 '{project.name}' 실행을 시작합니다...")
    
    try:'''
        
        # 액션들을 코드로 변환
        actions_code = self._generate_actions_code(project.actions)
        
        function_code += f"\n{actions_code}\n"
        function_code += '''        print("프로젝트 실행이 완료되었습니다.")
        
    except Exception as e:
        print(f"실행 중 오류가 발생했습니다: {{e}}")
        return False
    
    return True'''
        
        return function_code
    
    def _generate_actions_code(self, actions: List[Dict]) -> str:
        """액션들을 Python 코드로 변환"""
        if not actions:
            return "        # 실행할 액션이 없습니다."
        
        # 액션 순서대로 정렬
        sorted_actions = sorted(actions, key=lambda x: x.get('order_index', 0))
        
        code_lines = []
        for i, action in enumerate(sorted_actions):
            action_code = self._convert_action_to_code(action, i + 1)
            code_lines.append(action_code)
        
        return "\n".join(code_lines)
    
    def _convert_action_to_code(self, action: Dict, index: int) -> str:
        """개별 액션을 Python 코드로 변환"""
        action_type = action.get('action_type', '')
        description = action.get('description', '')
        parameters = action.get('parameters', {})
        
        # 주석 추가
        comment = f"        # {index}. {description}"
        
        if action_type == 'mouse_move':
            return self._generate_mouse_move_code(comment, parameters)
        elif action_type == 'mouse_click':
            return self._generate_mouse_click_code(comment, parameters)
        elif action_type == 'keyboard_type':
            return self._generate_keyboard_type_code(comment, parameters)
        elif action_type == 'delay':
            return self._generate_delay_code(comment, parameters)
        elif action_type == 'clipboard_copy':
            return self._generate_clipboard_copy_code(comment, parameters)
        elif action_type == 'clipboard_paste':
            return self._generate_clipboard_paste_code(comment, parameters)
        elif action_type == 'key_combination':
            return self._generate_key_combination_code(comment, parameters)
        else:
            return f"{comment}\n        # 알 수 없는 액션 타입: {action_type}"
    
    def _generate_mouse_move_code(self, comment: str, parameters: Dict) -> str:
        """마우스 이동 코드 생성"""
        x = parameters.get('x', 0)
        y = parameters.get('y', 0)
        duration = parameters.get('duration', 0.5)
        
        return f"""{comment}
        pyautogui.moveTo({x}, {y}, duration={duration})"""
    
    def _generate_mouse_click_code(self, comment: str, parameters: Dict) -> str:
        """마우스 클릭 코드 생성"""
        x = parameters.get('x', 0)
        y = parameters.get('y', 0)
        button = parameters.get('button', 'left')
        clicks = parameters.get('clicks', 1)
        
        return f"""{comment}
        pyautogui.click({x}, {y}, clicks={clicks}, button='{button}')"""
    
    def _generate_keyboard_type_code(self, comment: str, parameters: Dict) -> str:
        """키보드 입력 코드 생성"""
        text = parameters.get('text', '')
        interval = parameters.get('interval', 0.1)
        
        # 텍스트 이스케이프 처리
        escaped_text = text.replace('"', '\\"').replace("'", "\\'")
        
        return f"""{comment}
        pyautogui.write("{escaped_text}", interval={interval})"""
    
    def _generate_delay_code(self, comment: str, parameters: Dict) -> str:
        """지연 시간 코드 생성"""
        seconds = parameters.get('seconds', 1.0)
        
        return f"""{comment}
        time.sleep({seconds})"""
    
    def _generate_clipboard_copy_code(self, comment: str, parameters: Dict) -> str:
        """클립보드 복사 코드 생성"""
        text = parameters.get('text', '')
        
        # 텍스트 이스케이프 처리
        escaped_text = text.replace('"', '\\"').replace("'", "\\'")
        
        return f"""{comment}
        pyperclip.copy("{escaped_text}")"""
    
    def _generate_clipboard_paste_code(self, comment: str, parameters: Dict) -> str:
        """클립보드 붙여넣기 코드 생성"""
        method = parameters.get('method', 'Ctrl+V')
        
        if method == 'Ctrl+V':
            return f"""{comment}
        pyautogui.hotkey('ctrl', 'v')"""
        else:
            return f"""{comment}
        # 마우스 우클릭 후 붙여넣기
        pyautogui.rightClick()
        time.sleep(0.1)
        pyautogui.press('v')"""
    
    def _generate_key_combination_code(self, comment: str, parameters: Dict) -> str:
        """키 조합 코드 생성"""
        keys = parameters.get('keys', '')
        
        # 키 조합 파싱
        key_list = keys.split('+')
        key_args = ", ".join([f"'{key}'" for key in key_list])
        
        return f"""{comment}
        pyautogui.hotkey({key_args})"""
    
    def _generate_execution_section(self) -> str:
        """실행 섹션 생성"""
        return '''if __name__ == "__main__":
    # 실행 전 3초 대기
    print("3초 후 실행을 시작합니다...")
    time.sleep(3)
    
    # 메인 함수 실행
    success = run_project()
    
    if success:
        print("모든 작업이 성공적으로 완료되었습니다.")
    else:
        print("실행 중 오류가 발생했습니다.")'''
    
    def _save_to_file(self, code: str, file_path: str):
        """코드를 파일로 저장"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            print(f"코드가 {file_path}에 저장되었습니다.")
        except Exception as e:
            print(f"파일 저장 중 오류가 발생했습니다: {e}")
    
    def generate_executable_script(self, project: Project, output_path: str) -> bool:
        """
        실행 가능한 독립 스크립트 생성
        
        Args:
            project: 변환할 프로젝트
            output_path: 출력 파일 경로
        
        Returns:
            성공 여부
        """
        try:
            # 기본 Python 스크립트 생성
            python_code = self.generate_python_script(project)
            
            # 실행 가능한 스크립트로 변환 (shebang 추가)
            shebang = "#!/usr/bin/env python3\n"
            executable_code = shebang + python_code
            
            # 파일로 저장
            self._save_to_file(executable_code, output_path)
            
            # 실행 권한 부여 (Unix/Linux/macOS)
            if os.name != 'nt':  # Windows가 아닌 경우
                os.chmod(output_path, 0o755)
            
            return True
            
        except Exception as e:
            print(f"실행 가능한 스크립트 생성 중 오류가 발생했습니다: {e}")
            return False
    
    def generate_template_code(self, template_name: str, actions: List[Dict]) -> str:
        """
        템플릿 코드 생성
        
        Args:
            template_name: 템플릿 이름
            actions: 액션 목록
        
        Returns:
            생성된 템플릿 코드
        """
        template_code = f'''"""
{template_name} 템플릿
재사용 가능한 액션 템플릿
"""

def {template_name.lower().replace(' ', '_').replace('-', '_')}_template():
    """
    {template_name} 템플릿 함수
    """
    print(f"템플릿 '{template_name}' 실행을 시작합니다...")
    
    try:'''
        
        # 액션 코드 생성
        actions_code = self._generate_actions_code(actions)
        template_code += f"\n{actions_code}\n"
        
        template_code += '''        print("템플릿 실행이 완료되었습니다.")
        
    except Exception as e:
        print(f"템플릿 실행 중 오류가 발생했습니다: {{e}}")
        return False
    
    return True'''
        
        return template_code
    
    def get_code_statistics(self, project: Project) -> Dict:
        """
        코드 통계 반환
        
        Args:
            project: 프로젝트
        
        Returns:
            코드 통계 정보
        """
        total_actions = len(project.actions)
        action_types = {}
        
        for action in project.actions:
            action_type = action.get('action_type', '')
            action_types[action_type] = action_types.get(action_type, 0) + 1
        
        return {
            'total_actions': total_actions,
            'action_types': action_types,
            'estimated_lines': total_actions * 3 + 50,  # 대략적인 코드 라인 수
            'complexity': self._calculate_complexity(project.actions)
        }
    
    def _calculate_complexity(self, actions: List[Dict]) -> str:
        """코드 복잡도 계산"""
        if not actions:
            return "매우 간단"
        
        total_actions = len(actions)
        
        if total_actions <= 5:
            return "간단"
        elif total_actions <= 15:
            return "보통"
        elif total_actions <= 30:
            return "복잡"
        else:
            return "매우 복잡" 