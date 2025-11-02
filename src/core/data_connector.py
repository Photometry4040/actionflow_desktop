"""
Excel/CSV 데이터 연동 모듈
pandas를 사용한 데이터 읽기/쓰기 및 루프 처리
"""
from typing import List, Dict, Any, Optional, Iterator
from pathlib import Path
from datetime import datetime

from ..utils.logger import get_logger

logger = get_logger(__name__)

# pandas 선택적 import (설치되지 않았을 경우 대비)
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
    logger.info("Pandas 사용 가능")
except ImportError:
    PANDAS_AVAILABLE = False
    logger.warning("Pandas가 설치되지 않았습니다. Excel/CSV 연동 기능이 제한됩니다.")
    logger.warning("설치: pip install pandas openpyxl")


class DataConnector:
    """Excel/CSV 데이터 연동 클래스"""

    def __init__(self):
        """초기화"""
        self.current_data = None
        self.current_index = 0
        self.loop_stack = []  # 중첩 루프 지원

        if not PANDAS_AVAILABLE:
            logger.error("Pandas가 설치되지 않아 Excel/CSV 기능을 사용할 수 없습니다")

    def load_data(
        self,
        file_path: str,
        sheet_name: Optional[str] = None,
        encoding: str = 'utf-8'
    ) -> bool:
        """
        Excel 또는 CSV 파일 로드

        Args:
            file_path: 파일 경로
            sheet_name: Excel 시트명 (CSV는 무시)
            encoding: 인코딩 (CSV만 해당)

        Returns:
            성공 여부
        """
        if not PANDAS_AVAILABLE:
            logger.error("Pandas가 설치되지 않아 데이터를 로드할 수 없습니다")
            return False

        try:
            file_path = Path(file_path)

            if not file_path.exists():
                logger.error(f"파일이 존재하지 않습니다: {file_path}")
                return False

            logger.info(f"데이터 로드 시작: {file_path}")

            # 파일 확장자에 따라 처리
            if file_path.suffix.lower() in ['.xlsx', '.xls']:
                # Excel 파일
                if sheet_name:
                    self.current_data = pd.read_excel(file_path, sheet_name=sheet_name)
                else:
                    self.current_data = pd.read_excel(file_path)
                logger.info(f"Excel 파일 로드 완료: {len(self.current_data)}행")

            elif file_path.suffix.lower() == '.csv':
                # CSV 파일
                self.current_data = pd.read_csv(file_path, encoding=encoding)
                logger.info(f"CSV 파일 로드 완료: {len(self.current_data)}행")

            else:
                logger.error(f"지원하지 않는 파일 형식: {file_path.suffix}")
                return False

            # 인덱스 초기화
            self.current_index = 0

            logger.debug(f"컬럼: {list(self.current_data.columns)}")
            logger.debug(f"데이터 샘플:\n{self.current_data.head(2)}")

            return True

        except Exception as e:
            logger.error(f"데이터 로드 오류: {str(e)}", exc_info=True)
            return False

    def start_loop(self, filter_condition: Optional[Dict[str, Any]] = None) -> bool:
        """
        루프 시작 (데이터 순회 시작)

        Args:
            filter_condition: 필터 조건 {'column': '컬럼명', 'operator': '>=', 'value': 값}

        Returns:
            성공 여부
        """
        if self.current_data is None:
            logger.error("로드된 데이터가 없습니다")
            return False

        try:
            # 현재 상태 저장 (중첩 루프 지원)
            self.loop_stack.append({
                'data': self.current_data.copy(),
                'index': 0
            })

            # 필터 적용
            if filter_condition:
                filtered_data = self._apply_filter(self.current_data, filter_condition)
                self.current_data = filtered_data
                logger.info(f"필터 적용 후: {len(self.current_data)}행")

            self.current_index = 0
            logger.info(f"루프 시작: 총 {len(self.current_data)}행 처리 예정")

            return True

        except Exception as e:
            logger.error(f"루프 시작 오류: {str(e)}", exc_info=True)
            return False

    def get_next_row(self) -> Optional[Dict[str, Any]]:
        """
        다음 행 데이터 가져오기

        Returns:
            행 데이터 딕셔너리, 더 이상 없으면 None
        """
        if self.current_data is None:
            logger.error("로드된 데이터가 없습니다")
            return None

        if self.current_index >= len(self.current_data):
            logger.debug("모든 행을 처리했습니다")
            return None

        try:
            # 현재 행 가져오기
            row = self.current_data.iloc[self.current_index]

            # pandas Series를 딕셔너리로 변환
            row_dict = row.to_dict()

            # NaN 값을 None으로 변환
            row_dict = {k: (None if pd.isna(v) else v) for k, v in row_dict.items()}

            logger.debug(f"행 {self.current_index + 1}/{len(self.current_data)}: {row_dict}")

            self.current_index += 1

            return row_dict

        except Exception as e:
            logger.error(f"행 데이터 가져오기 오류: {str(e)}", exc_info=True)
            return None

    def end_loop(self) -> bool:
        """
        루프 종료

        Returns:
            성공 여부
        """
        try:
            if self.loop_stack:
                # 중첩 루프인 경우 이전 상태 복원
                prev_state = self.loop_stack.pop()
                self.current_data = prev_state['data']
                self.current_index = prev_state['index']
                logger.debug("중첩 루프 종료, 이전 상태 복원")
            else:
                logger.info(f"루프 종료: 총 {self.current_index}행 처리 완료")

            return True

        except Exception as e:
            logger.error(f"루프 종료 오류: {str(e)}", exc_info=True)
            return False

    def has_next(self) -> bool:
        """
        다음 행이 있는지 확인

        Returns:
            다음 행 존재 여부
        """
        if self.current_data is None:
            return False

        return self.current_index < len(self.current_data)

    def get_current_row_number(self) -> int:
        """현재 행 번호 반환 (1부터 시작)"""
        return self.current_index

    def get_total_rows(self) -> int:
        """전체 행 수 반환"""
        if self.current_data is None:
            return 0
        return len(self.current_data)

    def get_column_value(self, column_name: str, default: Any = None) -> Any:
        """
        현재 행의 특정 컬럼 값 가져오기

        Args:
            column_name: 컬럼명
            default: 값이 없을 때 기본값

        Returns:
            컬럼 값
        """
        if self.current_data is None or self.current_index == 0:
            return default

        try:
            # 이전 행 데이터 가져오기 (current_index는 이미 증가된 상태)
            row = self.current_data.iloc[self.current_index - 1]

            if column_name not in row:
                logger.warning(f"컬럼 '{column_name}'이 존재하지 않습니다")
                return default

            value = row[column_name]

            # NaN 처리
            if pd.isna(value):
                return default

            return value

        except Exception as e:
            logger.error(f"컬럼 값 가져오기 오류: {str(e)}", exc_info=True)
            return default

    def save_data(
        self,
        data: List[Dict[str, Any]],
        output_path: str,
        append: bool = False
    ) -> bool:
        """
        데이터를 Excel 또는 CSV로 저장

        Args:
            data: 저장할 데이터 (딕셔너리 리스트)
            output_path: 출력 파일 경로
            append: 기존 파일에 추가 여부

        Returns:
            성공 여부
        """
        if not PANDAS_AVAILABLE:
            logger.error("Pandas가 설치되지 않아 데이터를 저장할 수 없습니다")
            return False

        try:
            logger.info(f"데이터 저장 시작: {output_path}, 행 수: {len(data)}")

            output_path = Path(output_path)

            # DataFrame 생성
            df = pd.DataFrame(data)

            # 기존 파일에 추가하는 경우
            if append and output_path.exists():
                logger.debug("기존 파일에 데이터 추가")
                existing_df = pd.read_excel(output_path) if output_path.suffix.lower() in ['.xlsx', '.xls'] else pd.read_csv(output_path)
                df = pd.concat([existing_df, df], ignore_index=True)

            # 파일 저장
            if output_path.suffix.lower() in ['.xlsx', '.xls']:
                df.to_excel(output_path, index=False)
                logger.info(f"Excel 파일 저장 완료: {len(df)}행")
            elif output_path.suffix.lower() == '.csv':
                df.to_csv(output_path, index=False, encoding='utf-8-sig')
                logger.info(f"CSV 파일 저장 완료: {len(df)}행")
            else:
                logger.error(f"지원하지 않는 파일 형식: {output_path.suffix}")
                return False

            return True

        except Exception as e:
            logger.error(f"데이터 저장 오류: {str(e)}", exc_info=True)
            return False

    def get_column_names(self) -> List[str]:
        """
        컬럼명 리스트 반환

        Returns:
            컬럼명 리스트
        """
        if self.current_data is None:
            return []

        return list(self.current_data.columns)

    def _apply_filter(
        self,
        data: pd.DataFrame,
        filter_condition: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        데이터 필터링

        Args:
            data: 원본 데이터
            filter_condition: 필터 조건

        Returns:
            필터링된 데이터
        """
        try:
            column = filter_condition.get('column')
            operator = filter_condition.get('operator', '==')
            value = filter_condition.get('value')

            if column not in data.columns:
                logger.warning(f"필터 컬럼 '{column}'이 존재하지 않습니다")
                return data

            logger.debug(f"필터 적용: {column} {operator} {value}")

            # 연산자에 따라 필터링
            if operator == '==':
                return data[data[column] == value]
            elif operator == '!=':
                return data[data[column] != value]
            elif operator == '>':
                return data[data[column] > value]
            elif operator == '>=':
                return data[data[column] >= value]
            elif operator == '<':
                return data[data[column] < value]
            elif operator == '<=':
                return data[data[column] <= value]
            elif operator == 'contains':
                return data[data[column].astype(str).str.contains(str(value), na=False)]
            else:
                logger.warning(f"지원하지 않는 연산자: {operator}")
                return data

        except Exception as e:
            logger.error(f"필터 적용 오류: {str(e)}", exc_info=True)
            return data

    def reset(self):
        """데이터 커넥터 초기화"""
        self.current_data = None
        self.current_index = 0
        self.loop_stack.clear()
        logger.debug("DataConnector 초기화 완료")

    def is_pandas_available(self) -> bool:
        """Pandas 사용 가능 여부"""
        return PANDAS_AVAILABLE

    def get_data_info(self) -> Dict[str, Any]:
        """
        현재 로드된 데이터 정보 반환

        Returns:
            데이터 정보 딕셔너리
        """
        if self.current_data is None:
            return {
                'loaded': False,
                'rows': 0,
                'columns': []
            }

        return {
            'loaded': True,
            'rows': len(self.current_data),
            'columns': list(self.current_data.columns),
            'current_index': self.current_index,
            'dtypes': {col: str(dtype) for col, dtype in self.current_data.dtypes.items()}
        }
