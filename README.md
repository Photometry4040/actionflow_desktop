# ActionFlow Desktop Automator

## 📋 프로젝트 개요

**제작자**: Photometry4040  
**저작권**: © 2025 Photometry4040. All rights reserved.

> **중요**: 이 소프트웨어를 배포하거나 수정할 때는 반드시 저작권 표시를 명기해주세요.

**ActionFlow Desktop Automator**는 로컬 PC용 반복 업무 자동화 도구입니다. 개인 사용자가 마우스/키보드 작업을 순차적으로 저장하고 실행할 수 있는 간단한 데스크톱 애플리케이션입니다.

### 🎯 핵심 특징
- **단일 .exe 파일로 배포 가능**한 간단한 구조
- **JSON 기반 데이터 저장** (SQLite 제거)
- 직관적이고 빠른 GUI 인터페이스
- 개인 사용자에 최적화된 기능

## 🚀 빠른 시작

### 설치 요구사항
- Python 3.8 이상
- Windows 10/11, macOS 10.15+, Ubuntu 18.04+

#### 선택적 의존성 (고급 기능)
- **OpenCV** (`opencv-python`): 이미지 인식 기능 사용 시
- **Pandas** (`pandas`): Excel/CSV 데이터 연동 사용 시
- **openpyxl**: Excel 파일(.xlsx) 처리 시

> **참고**: 선택적 의존성이 설치되지 않은 경우 해당 기능이 비활성화되며, 나머지 기능은 정상 동작합니다.

### 개발 환경 설정
```bash
# 1. 프로젝트 클론
git clone <repository-url>
cd actionflow_desktop

# 2. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 애플리케이션 실행
python main.py
```

### 테스트 실행
```bash
# 모든 테스트 실행
python run_tests.py

# 개별 테스트 실행
python tests/test_permissions.py      # 권한 테스트
python tests/test_mouse_action.py     # 마우스 액션 테스트
python tests/test_dialog.py           # 다이얼로그 테스트
python tests/test_action_dialog.py    # 액션 다이얼로그 테스트
```

### 배포
```bash
# 자동 빌드 스크립트 사용 (권장)
python build.py

# 수동 빌드
pyinstaller --onefile --windowed main.py
```

## 📁 프로젝트 구조

```
actionflow_desktop/
├── main.py                 # 메인 애플리케이션 진입점
├── requirements.txt        # Python 의존성
├── README.md              # 프로젝트 문서
├── src/
│   ├── gui/               # GUI 관련 모듈
│   ├── core/              # 핵심 로직
│   ├── models/            # 데이터 모델
│   ├── utils/             # 유틸리티
│   └── resources/         # 리소스 파일
├── data/                  # JSON 데이터 저장소
├── tests/                 # 테스트 코드
└── docs/                  # 문서
```

## 🎯 주요 기능

### 1. 프로젝트 관리
- 프로젝트 생성/수정/삭제
- 프로젝트별 액션 시퀀스 저장
- 프로젝트 목록 및 검색
- 프로젝트 카테고리 분류

### 2. 액션 관리
- 마우스 이동/클릭
- 키보드 입력
- 복사/붙여넣기
- 지연 시간
- 키 조합 (Ctrl+C, Ctrl+V 등)

### 3. 실행 기능
- 프로젝트 전체 실행
- 개별 액션 실행
- 실행 중 중단 (ESC 키)
- 실행 속도 조절

### 4. 코드 생성
- Python 스크립트 생성
- 실행 가능한 .py 파일 저장

### 5. 고급 기능 (Phase 3)
- 매크로 녹화 기능
- 설정 관리 시스템
- 백업/복원 기능
- 템플릿 관리

### 6. 최적화 기능 (Phase 4)
- 실행 히스토리 관리
- 고급 매크로 기능 (조건부 실행, 반복 설정)
- 성능 최적화 (메모리 관리, 캐싱)
- 현대적 테마 시스템
- **로깅 시스템** (일별 로그 파일, 로그 레벨 설정)
- **에러 처리 개선** (상세한 예외 추적 및 복구)
- **JSON 스키마 검증** (데이터 무결성 보장)
- **손상된 파일 자동 복구**

### 7. 고급 자동화 기능 (Phase 5) 🆕
#### 이미지 인식 기반 자동화
- **OpenCV 기반 이미지 매칭**: UI 요소를 이미지로 인식하여 클릭
- **동적 UI 대응**: 좌표 기반이 아닌 이미지 기반 클릭으로 해상도/레이아웃 변경에도 동작
- **신뢰도 조절**: 매칭 신뢰도를 조절하여 유연한 인식
- **템플릿 캐싱**: 성능 향상을 위한 이미지 캐싱
- **주요 기능**:
  - `이미지 클릭`: 화면에서 이미지를 찾아 클릭
  - `이미지 대기`: 특정 이미지가 나타날 때까지 대기
  - `이미지 찾기`: 화면에서 이미지 검색
  - `여러 이미지 대기`: 여러 이미지 중 하나가 나타날 때까지 대기

#### Excel/CSV 데이터 연동
- **Pandas 기반 데이터 처리**: Excel/CSV 파일 읽기 및 쓰기
- **데이터 루프**: 행 단위 반복 처리로 대량 작업 자동화
- **필터링 기능**: 조건에 맞는 데이터만 처리
- **중첩 루프 지원**: 복잡한 데이터 처리 시나리오
- **주요 기능**:
  - `Excel/CSV 로드`: 데이터 파일 불러오기
  - `루프 시작`: 각 행을 순회하며 자동화 실행
  - `셀 값 가져오기`: 특정 컬럼의 값을 가져와 사용
  - `결과 저장`: 처리 결과를 새 파일로 저장

**사용 예시**: Excel 파일의 고객 목록을 읽어 각 고객에게 자동으로 이메일 전송, 웹사이트에서 데이터를 추출하여 Excel로 저장 등

📚 **상세 가이드**: [고급 기능 활용 가이드](docs/ADVANCED_FEATURES.md) 참조

## 📊 데이터 구조

### JSON 기반 데이터 저장
- `data/projects.json` - 프로젝트 및 액션 데이터
- `data/settings.json` - 사용자 설정
- `data/templates.json` - 액션 템플릿

사용자가 직접 JSON 파일을 확인하고 편집할 수 있습니다.

### 로그 파일 위치
- **Windows**: `%APPDATA%/ActionFlow/logs/actionflow_YYYYMMDD.log`
- **macOS**: `~/Library/Application Support/ActionFlow/logs/actionflow_YYYYMMDD.log`
- **Linux**: `~/.config/ActionFlow/logs/actionflow_YYYYMMDD.log`

로그 파일은 일별로 자동 생성되며, 최대 5개까지 보관됩니다 (각 10MB 제한).

## 🛠️ 개발 가이드라인

### 개발 완료 상태
- ✅ **Phase 1**: 기본 구조 및 프로젝트 관리
- ✅ **Phase 2**: 액션 관리 및 실행 엔진
- ✅ **Phase 3**: 고급 기능 (코드 생성, 백업/복원, 설정 관리)
- ✅ **Phase 4**: 최적화 및 배포 (히스토리, 성능 최적화, 빌드 시스템)
- ✅ **Phase 5**: 고급 자동화 (이미지 인식, Excel/CSV 연동)

### 코딩 스타일
- PEP 8 준수
- 함수/클래스에 docstring 필수
- 변수명은 snake_case
- 클래스명은 PascalCase

### 테스트
```bash
# 테스트 실행
pytest

# 코드 포맷팅
black .

# 린팅
flake8
```

## 📝 저작권 및 라이선스

**제작자**: Photometry4040  
**저작권**: © 2025 Photometry4040. All rights reserved.

### 📋 라이선스 조건
- 이 소프트웨어는 개인 및 상업적 용도로 사용할 수 있습니다.
- **배포 시 반드시 저작권 표시를 명기해주세요.**
- 소스 코드 수정 시에도 원본 저작권 표시를 유지해야 합니다.
- 무단 배포 및 상업적 이용은 금지됩니다.

### 🔒 보안 정책
- 모든 데이터는 로컬에만 저장됩니다.
- 외부 네트워크 연결이 없습니다.
- 사용자 입력은 철저히 검증됩니다.
- 실행 중 안전 장치(ESC 키)가 구현되어 있습니다.
- 데이터 암호화 및 백업 기능이 포함되어 있습니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해 주세요.

---

## 🎯 성능 목표 달성

- ✅ **앱 시작 시간**: 3초 이내
- ✅ **액션 실행 지연**: 100ms 이내
- ✅ **메모리 사용량**: 100MB 이하 (최적화 기능으로 관리)
- ✅ **프로젝트 저장**: 1초 이내
- ✅ **실행 중 응답성**: ESC 키 즉시 반응
- ✅ **배포**: 단일 실행 파일 (20MB) 생성 완료

## 🚀 배포 완료

- **실행 파일**: `dist/ActionFlow` (macOS/Linux) 또는 `dist/ActionFlow.exe` (Windows)
- **패키지**: `package/` 디렉토리에 배포용 파일들
- **빌드 스크립트**: `python build.py`로 자동 빌드

---

**ActionFlow Desktop Automator** - 간단하고 효율적인 데스크톱 자동화 도구 🚀 