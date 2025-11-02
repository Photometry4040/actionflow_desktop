"""
이미지 인식 모듈
OpenCV를 사용한 화면 이미지 검색 및 템플릿 매칭
"""
import time
from typing import Tuple, Optional, List, Dict, Any
from pathlib import Path
import pyautogui
from PIL import Image

from ..utils.logger import get_logger

logger = get_logger(__name__)

# OpenCV 선택적 import (설치되지 않았을 경우 대비)
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
    logger.info("OpenCV 사용 가능")
except ImportError:
    OPENCV_AVAILABLE = False
    logger.warning("OpenCV가 설치되지 않았습니다. 이미지 인식 기능이 제한됩니다.")
    logger.warning("설치: pip install opencv-python")


class ImageRecognizer:
    """이미지 인식 및 템플릿 매칭 클래스"""

    def __init__(self):
        """초기화"""
        self.last_screenshot = None
        self.template_cache = {}  # 템플릿 이미지 캐시

        if not OPENCV_AVAILABLE:
            logger.error("OpenCV가 설치되지 않아 이미지 인식 기능을 사용할 수 없습니다")

    def find_on_screen(
        self,
        template_path: str,
        confidence: float = 0.8,
        region: Optional[Tuple[int, int, int, int]] = None,
        grayscale: bool = True
    ) -> Tuple[bool, Optional[Tuple[int, int]]]:
        """
        화면에서 이미지 찾기

        Args:
            template_path: 찾을 이미지 파일 경로
            confidence: 신뢰도 임계값 (0.0 ~ 1.0)
            region: 검색 영역 (x, y, width, height), None이면 전체 화면
            grayscale: 흑백 모드 사용 여부 (더 빠름)

        Returns:
            (찾음 여부, 위치(x, y)) 튜플
        """
        if not OPENCV_AVAILABLE:
            logger.error("OpenCV가 설치되지 않아 이미지 검색을 수행할 수 없습니다")
            return False, None

        try:
            logger.debug(f"이미지 검색 시작: {template_path}, 신뢰도: {confidence}")

            # 1. 현재 화면 캡처
            screenshot = self._capture_screen(region)
            if screenshot is None:
                return False, None

            # 2. 템플릿 이미지 로드
            template = self._load_template(template_path)
            if template is None:
                return False, None

            # 3. 이미지 전처리 (흑백 변환)
            if grayscale:
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
                if len(template.shape) == 3:
                    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

            # 4. 템플릿 매칭
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            logger.debug(f"매칭 결과: 최대값 = {max_val:.3f}, 위치 = {max_loc}")

            # 5. 신뢰도 체크
            if max_val >= confidence:
                # 템플릿 중심점 계산
                template_h, template_w = template.shape[:2]
                center_x = max_loc[0] + template_w // 2
                center_y = max_loc[1] + template_h // 2

                # region이 지정된 경우 좌표 보정
                if region:
                    center_x += region[0]
                    center_y += region[1]

                logger.info(f"이미지 찾음: {template_path} at ({center_x}, {center_y}), 신뢰도: {max_val:.3f}")
                return True, (center_x, center_y)
            else:
                logger.debug(f"이미지를 찾지 못함: 신뢰도 부족 ({max_val:.3f} < {confidence})")
                return False, None

        except Exception as e:
            logger.error(f"이미지 검색 오류: {str(e)}", exc_info=True)
            return False, None

    def wait_for_image(
        self,
        template_path: str,
        confidence: float = 0.8,
        timeout: float = 10.0,
        check_interval: float = 0.5,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> Tuple[bool, Optional[Tuple[int, int]]]:
        """
        이미지가 나타날 때까지 대기

        Args:
            template_path: 찾을 이미지 파일 경로
            confidence: 신뢰도 임계값
            timeout: 최대 대기 시간 (초)
            check_interval: 확인 간격 (초)
            region: 검색 영역

        Returns:
            (찾음 여부, 위치) 튜플
        """
        logger.info(f"이미지 대기 시작: {template_path}, 타임아웃: {timeout}초")

        start_time = time.time()
        attempts = 0

        while time.time() - start_time < timeout:
            attempts += 1
            found, location = self.find_on_screen(template_path, confidence, region)

            if found:
                logger.info(f"이미지 찾음 (시도 {attempts}회, {time.time() - start_time:.1f}초 경과)")
                return True, location

            time.sleep(check_interval)

        logger.warning(f"이미지를 찾지 못함: 타임아웃 ({attempts}회 시도)")
        return False, None

    def find_any(
        self,
        template_paths: List[str],
        confidence: float = 0.8,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> Tuple[bool, Optional[int], Optional[Tuple[int, int]]]:
        """
        여러 이미지 중 하나 찾기

        Args:
            template_paths: 찾을 이미지 파일 경로 리스트
            confidence: 신뢰도 임계값
            region: 검색 영역

        Returns:
            (찾음 여부, 찾은 이미지 인덱스, 위치) 튜플
        """
        logger.debug(f"여러 이미지 중 하나 찾기: {len(template_paths)}개")

        for index, template_path in enumerate(template_paths):
            found, location = self.find_on_screen(template_path, confidence, region)
            if found:
                logger.info(f"이미지 찾음: {template_path} (인덱스 {index})")
                return True, index, location

        logger.debug("여러 이미지 중 하나도 찾지 못함")
        return False, None, None

    def get_image_location_pyautogui(
        self,
        template_path: str,
        confidence: float = 0.8,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> Optional[Tuple[int, int]]:
        """
        PyAutoGUI를 사용한 이미지 찾기 (OpenCV 대안)

        Args:
            template_path: 찾을 이미지 파일 경로
            confidence: 신뢰도 임계값
            region: 검색 영역

        Returns:
            이미지 중심점 좌표, 못 찾으면 None
        """
        try:
            logger.debug(f"PyAutoGUI로 이미지 검색: {template_path}")

            location = pyautogui.locateCenterOnScreen(
                template_path,
                confidence=confidence,
                region=region
            )

            if location:
                logger.info(f"이미지 찾음 (PyAutoGUI): {template_path} at {location}")
                return location
            else:
                logger.debug(f"이미지를 찾지 못함 (PyAutoGUI): {template_path}")
                return None

        except pyautogui.ImageNotFoundException:
            logger.debug(f"이미지를 찾지 못함 (PyAutoGUI): {template_path}")
            return None
        except Exception as e:
            logger.error(f"PyAutoGUI 이미지 검색 오류: {str(e)}", exc_info=True)
            return None

    def click_image(
        self,
        template_path: str,
        confidence: float = 0.8,
        timeout: float = 0,
        region: Optional[Tuple[int, int, int, int]] = None,
        button: str = 'left',
        clicks: int = 1
    ) -> bool:
        """
        이미지를 찾아서 클릭

        Args:
            template_path: 찾을 이미지 파일 경로
            confidence: 신뢰도 임계값
            timeout: 최대 대기 시간 (0이면 대기 안 함)
            region: 검색 영역
            button: 마우스 버튼 ('left', 'right', 'middle')
            clicks: 클릭 횟수

        Returns:
            성공 여부
        """
        try:
            # 이미지 찾기 (필요시 대기)
            if timeout > 0:
                found, location = self.wait_for_image(template_path, confidence, timeout, region=region)
            else:
                found, location = self.find_on_screen(template_path, confidence, region)

            if found and location:
                # 클릭
                x, y = location
                logger.info(f"이미지 클릭: ({x}, {y}), 버튼: {button}, 횟수: {clicks}")
                pyautogui.click(x, y, clicks=clicks, button=button)
                return True
            else:
                logger.warning(f"이미지를 찾지 못해 클릭 실패: {template_path}")
                return False

        except Exception as e:
            logger.error(f"이미지 클릭 오류: {str(e)}", exc_info=True)
            return False

    def _capture_screen(
        self,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> Optional[np.ndarray]:
        """
        화면 캡처

        Args:
            region: 캡처 영역 (x, y, width, height)

        Returns:
            numpy 배열 형태의 이미지, 실패 시 None
        """
        try:
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()

            # PIL Image를 numpy 배열로 변환
            screenshot_np = np.array(screenshot)

            # RGB → BGR 변환 (OpenCV는 BGR 사용)
            screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

            return screenshot_bgr

        except Exception as e:
            logger.error(f"화면 캡처 오류: {str(e)}", exc_info=True)
            return None

    def _load_template(self, template_path: str) -> Optional[np.ndarray]:
        """
        템플릿 이미지 로드 (캐싱 지원)

        Args:
            template_path: 이미지 파일 경로

        Returns:
            numpy 배열 형태의 이미지, 실패 시 None
        """
        try:
            # 캐시 확인
            if template_path in self.template_cache:
                logger.debug(f"캐시에서 템플릿 로드: {template_path}")
                return self.template_cache[template_path]

            # 파일 존재 확인
            if not Path(template_path).exists():
                logger.error(f"템플릿 파일이 존재하지 않습니다: {template_path}")
                return None

            # 이미지 로드
            template = cv2.imread(template_path)
            if template is None:
                logger.error(f"템플릿 이미지 로드 실패: {template_path}")
                return None

            # 캐시에 저장
            self.template_cache[template_path] = template
            logger.debug(f"템플릿 로드 완료: {template_path}, 크기: {template.shape}")

            return template

        except Exception as e:
            logger.error(f"템플릿 로드 오류: {str(e)}", exc_info=True)
            return None

    def clear_cache(self):
        """템플릿 이미지 캐시 초기화"""
        self.template_cache.clear()
        logger.debug("템플릿 캐시 초기화 완료")

    def get_screen_size(self) -> Tuple[int, int]:
        """화면 크기 반환"""
        return pyautogui.size()

    def is_opencv_available(self) -> bool:
        """OpenCV 사용 가능 여부"""
        return OPENCV_AVAILABLE
