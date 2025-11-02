# ActionFlow Desktop Automator - 고급 기능 활용 가이드

## 목차

- [이미지 인식 기반 자동화](#이미지-인식-기반-자동화)
- [Excel/CSV 데이터 연동](#excelcsv-데이터-연동)
- [두 기능 통합 활용](#두-기능-통합-활용)
- [실무 활용 시나리오](#실무-활용-시나리오)

---

## 이미지 인식 기반 자동화

### 🎯 핵심 개념

현재는 **고정된 좌표 (x, y)**로 클릭하지만, 이미지 인식을 사용하면 **화면에서 버튼/아이콘을 찾아서** 자동으로 클릭할 수 있습니다.

### 📌 주요 장점

| 기능 | 기존 방식 | 이미지 인식 방식 |
|------|-----------|------------------|
| **좌표 의존성** | ❌ 고정 좌표에 의존 | ✅ 화면에서 자동으로 찾음 |
| **해상도 변경** | ❌ 해상도 바뀌면 실패 | ✅ 어떤 해상도에서도 동작 |
| **UI 변경** | ❌ UI 조금만 바뀌어도 수정 필요 | ✅ 버튼 이미지만 같으면 동작 |
| **창 위치** | ❌ 창 위치 고정 필요 | ✅ 창이 어디에 있든 찾음 |

### 💡 활용 예시 1: 해상도 독립적 클릭

#### 문제 상황
```python
# ❌ 현재 방식의 문제점
action = {
    'action_type': 'mouse_click',
    'parameters': {'x': 500, 'y': 300}
}
# → 1920x1080 해상도에서만 정확
# → 노트북(1366x768)에서는 버튼 위치가 달라서 클릭 실패!
```

#### 해결 방법
```python
# ✅ 이미지 인식 방식
action = {
    'action_type': 'image_click',
    'parameters': {
        'template_image': 'data/templates/login_button.png',
        'confidence': 0.8,  # 80% 일치하면 찾았다고 판단
        'timeout': 10,      # 10초 동안 찾기 시도
        'region': None      # 전체 화면 검색 (특정 영역 지정 가능)
    }
}
# → 어떤 해상도에서도 버튼을 자동으로 찾아서 클릭!
```

### 💡 활용 예시 2: 웹사이트 자동 로그인

#### 시나리오
네이버 자동 로그인 구현

**기존 방식의 문제:**
- 브라우저 창 크기가 달라지면 좌표가 틀어짐
- 웹사이트 UI가 조금만 바뀌어도 좌표 수정 필요
- 여러 모니터 환경에서 작동 안 함

**이미지 인식 활용:**
```python
project_actions = [
    # 1. 로그인 버튼 찾아서 클릭
    {
        'action_type': 'image_click',
        'parameters': {
            'template_image': 'naver_login_button.png',
            'confidence': 0.85
        }
    },

    # 2. ID 입력란 찾아서 클릭
    {
        'action_type': 'image_click',
        'parameters': {
            'template_image': 'id_input_field.png',
            'confidence': 0.8
        }
    },

    # 3. ID 입력
    {
        'action_type': 'keyboard_type',
        'parameters': {'text': 'myid@naver.com'}
    },

    # 4. 비밀번호 입력란 찾아서 클릭
    {
        'action_type': 'image_click',
        'parameters': {
            'template_image': 'password_input_field.png'
        }
    },

    # 5. 비밀번호 입력
    {
        'action_type': 'keyboard_type',
        'parameters': {'text': 'mypassword'}
    },

    # 6. 로그인 버튼 클릭
    {
        'action_type': 'image_click',
        'parameters': {
            'template_image': 'submit_button.png'
        }
    }
]
```

### 💡 활용 예시 3: 조건부 실행

#### 시나리오
특정 상태가 될 때까지 대기

```python
# 이메일에서 "읽지 않은 메일" 아이콘이 나타날 때까지 대기
action = {
    'action_type': 'wait_for_image',
    'parameters': {
        'template_image': 'unread_mail_icon.png',
        'timeout': 60,          # 60초 동안 기다림
        'check_interval': 2,    # 2초마다 확인
        'on_found': 'continue', # 찾으면 다음 액션 실행
        'on_timeout': 'stop'    # 못 찾으면 실행 중지
    }
}
```

### 💡 활용 예시 4: 여러 이미지 중 하나 찾기

```python
# 성공/실패 팝업 중 하나가 나타날 때까지 대기
action = {
    'action_type': 'wait_for_any_image',
    'parameters': {
        'template_images': [
            'success_popup.png',
            'error_popup.png',
            'warning_popup.png'
        ],
        'timeout': 30,
        'return_which': True  # 어떤 이미지를 찾았는지 반환
    }
}
```

### 🔧 이미지 템플릿 준비 방법

1. **스크린샷 캡처**
   - 찾고 싶은 버튼/아이콘을 스크린샷으로 캡처
   - PNG 형식 권장 (투명도 지원)

2. **이미지 크기**
   - 너무 크지 않게: 50x50 ~ 200x200 픽셀 권장
   - 특징이 명확한 부분만 포함

3. **저장 위치**
   - `data/templates/` 폴더에 저장
   - 의미있는 이름 사용: `login_button.png`, `submit_btn.png`

4. **주의사항**
   - 배경이 포함되지 않도록 정확히 자르기
   - 같은 버튼이 여러 개 있으면 가장 특징적인 부분만 캡처

---

## Excel/CSV 데이터 연동

### 🎯 핵심 개념

Excel 파일의 **데이터를 하나씩 읽어서** 반복 작업을 자동화합니다.

### 📌 주요 장점

| 기능 | 수동 작업 | Excel 연동 |
|------|-----------|------------|
| **데이터 관리** | 코드에 하드코딩 | Excel에서 쉽게 관리 |
| **대량 처리** | 하나씩 수동 실행 | 100개도 자동 반복 |
| **결과 저장** | 메모장에 기록 | Excel에 자동 저장 |
| **수정 용이성** | 코드 수정 필요 | Excel만 수정 |

### 💡 활용 예시 1: 대량 회원 가입

#### Excel 파일 준비 (members.xlsx)
```
┌─────────┬────────────────┬─────────────────┬──────────┐
│ 이름    │ 이메일         │ 전화번호        │ 부서     │
├─────────┼────────────────┼─────────────────┼──────────┤
│ 김철수  │ kim@gmail.com  │ 010-1234-5678   │ 개발팀   │
│ 이영희  │ lee@gmail.com  │ 010-2345-6789   │ 디자인팀 │
│ 박민수  │ park@gmail.com │ 010-3456-7890   │ 기획팀   │
│ 최지원  │ choi@gmail.com │ 010-4567-8901   │ 영업팀   │
└─────────┴────────────────┴─────────────────┴──────────┘
```

#### 자동화 프로젝트
```python
project = {
    'name': '회원 대량 가입',
    'data_source': {
        'type': 'excel',
        'file_path': 'data/members.xlsx',
        'sheet_name': 'Sheet1'
    },
    'actions': [
        # 반복 시작 (Excel의 각 행마다)
        {
            'action_type': 'excel_loop_start',
            'parameters': {
                'file': 'data/members.xlsx',
                'sheet': 'Sheet1'
            }
        },

        # 회원가입 페이지 열기
        {
            'action_type': 'image_click',
            'parameters': {
                'template_image': 'signup_button.png'
            }
        },

        # 이름 입력
        {
            'action_type': 'keyboard_type',
            'parameters': {
                'text': '{{이름}}'  # Excel 컬럼명
            }
        },

        # Tab 키로 다음 필드로 이동
        {
            'action_type': 'key_press',
            'parameters': {'key': 'tab'}
        },

        # 이메일 입력
        {
            'action_type': 'keyboard_type',
            'parameters': {
                'text': '{{이메일}}'
            }
        },

        # Tab
        {
            'action_type': 'key_press',
            'parameters': {'key': 'tab'}
        },

        # 전화번호 입력
        {
            'action_type': 'keyboard_type',
            'parameters': {
                'text': '{{전화번호}}'
            }
        },

        # 가입 버튼 클릭
        {
            'action_type': 'image_click',
            'parameters': {
                'template_image': 'submit_button.png'
            }
        },

        # 완료 대기 (2초)
        {
            'action_type': 'delay',
            'parameters': {'seconds': 2}
        },

        # 반복 종료
        {
            'action_type': 'excel_loop_end'
        }
    ]
}
```

### 💡 활용 예시 2: 재고 관리 시스템 데이터 입력

#### 시나리오
상품 100개를 쇼핑몰에 등록

**수동 작업:**
- 1개당 3분 소요 → 100개 = 300분 (5시간)

**자동화 + Excel:**
- Excel에 상품 정보 미리 정리
- ActionFlow가 자동으로 입력
- 100개 = 30분 (10배 빠름)

#### Excel 파일 (products.csv)
```csv
상품명,가격,재고,카테고리,설명,이미지경로
노트북,1200000,50,전자제품,고성능 노트북,images/laptop.jpg
마우스,30000,200,주변기기,무선 마우스,images/mouse.jpg
키보드,80000,150,주변기기,기계식 키보드,images/keyboard.jpg
모니터,350000,80,전자제품,27인치 모니터,images/monitor.jpg
```

#### 자동화 액션
```python
{
    'action_type': 'excel_loop_start',
    'parameters': {'file': 'products.csv'}
},
{
    'action_type': 'keyboard_type',
    'parameters': {'text': '{{상품명}}'}
},
{
    'action_type': 'keyboard_type',
    'parameters': {'text': '{{가격}}'}
},
{
    'action_type': 'keyboard_type',
    'parameters': {'text': '{{재고}}'}
},
{
    'action_type': 'image_click',
    'parameters': {'template_image': 'register_button.png'}
},
{
    'action_type': 'excel_loop_end'
}
```

### 💡 활용 예시 3: 실행 결과를 Excel에 저장

```python
# 작업 결과를 새로운 Excel 파일로 저장
action = {
    'action_type': 'excel_save_results',
    'parameters': {
        'output_file': 'data/작업결과.xlsx',
        'columns': ['상품명', '상태', '시간', '오류메시지'],
        'append': True  # 기존 파일에 추가
    }
}
```

**결과 파일 예시:**
```
┌──────────┬────────┬─────────────────────┬────────────────┐
│ 상품명   │ 상태   │ 시간                │ 오류메시지     │
├──────────┼────────┼─────────────────────┼────────────────┤
│ 노트북   │ 성공   │ 2025-11-02 10:15:23 │                │
│ 마우스   │ 성공   │ 2025-11-02 10:15:45 │                │
│ 키보드   │ 실패   │ 2025-11-02 10:16:02 │ 가격 형식 오류 │
│ 모니터   │ 성공   │ 2025-11-02 10:16:30 │                │
└──────────┴────────┴─────────────────────┴────────────────┘
```

### 💡 활용 예시 4: CSV 파일 읽기 및 필터링

```python
# CSV 파일에서 특정 조건의 데이터만 처리
action = {
    'action_type': 'excel_loop_start',
    'parameters': {
        'file': 'customers.csv',
        'filter': {
            'column': '구매금액',
            'operator': '>=',
            'value': 100000
        }
    }
}
# → 구매금액이 10만원 이상인 고객만 처리
```

---

## 두 기능 통합 활용

### 🚀 최강 조합: 지원서 자동 제출

#### 시나리오
100개 회사에 입사 지원서 제출

#### Excel 파일 (companies.xlsx)
```
┌─────────────┬──────────────┬─────────────────────┬────────────────────┐
│ 회사명      │ 웹사이트     │ 담당자이메일        │ 직무               │
├─────────────┼──────────────┼─────────────────────┼────────────────────┤
│ 삼성전자    │ samsung.com  │ hr@samsung.com      │ SW 엔지니어        │
│ LG전자      │ lg.com       │ recruit@lg.com      │ 백엔드 개발자      │
│ 네이버      │ naver.com    │ career@naver.com    │ 프론트엔드 개발자  │
│ 카카오      │ kakao.com    │ jobs@kakao.com      │ 데이터 분석가      │
└─────────────┴──────────────┴─────────────────────┴────────────────────┘
```

#### 완전 자동화 프로젝트
```python
project = {
    'name': '지원서 대량 제출',
    'actions': [
        # Excel 파일에서 데이터 읽기 시작
        {
            'action_type': 'excel_loop_start',
            'parameters': {'file': 'companies.xlsx'}
        },

        # 1. 브라우저에서 웹사이트 열기
        {
            'action_type': 'browser_navigate',
            'parameters': {'url': '{{웹사이트}}'}
        },

        # 2. 이미지 인식으로 "채용" 버튼 찾기
        {
            'action_type': 'image_click',
            'parameters': {
                'template_image': 'career_button.png',
                'timeout': 10
            }
        },

        # 3. "지원하기" 버튼 찾기
        {
            'action_type': 'wait_for_image',
            'parameters': {
                'template_image': 'apply_button.png',
                'timeout': 15
            }
        },

        # 4. 클릭
        {
            'action_type': 'image_click',
            'parameters': {'template_image': 'apply_button.png'}
        },

        # 5. 이름 입력란 찾아서 클릭
        {
            'action_type': 'image_click',
            'parameters': {'template_image': 'name_field.png'}
        },

        # 6. 이름 입력
        {
            'action_type': 'keyboard_type',
            'parameters': {'text': '홍길동'}
        },

        # 7. 이메일 입력란 찾아서 클릭
        {
            'action_type': 'image_click',
            'parameters': {'template_image': 'email_field.png'}
        },

        # 8. 이메일 입력
        {
            'action_type': 'keyboard_type',
            'parameters': {'text': 'hong@example.com'}
        },

        # 9. 지원 직무 선택란 클릭
        {
            'action_type': 'image_click',
            'parameters': {'template_image': 'position_field.png'}
        },

        # 10. Excel에서 읽은 직무 입력
        {
            'action_type': 'keyboard_type',
            'parameters': {'text': '{{직무}}'}
        },

        # 11. 제출 버튼 클릭
        {
            'action_type': 'image_click',
            'parameters': {'template_image': 'submit_button.png'}
        },

        # 12. 완료 확인 (성공/실패 팝업 대기)
        {
            'action_type': 'wait_for_any_image',
            'parameters': {
                'template_images': [
                    'success_popup.png',
                    'error_popup.png'
                ],
                'timeout': 10
            }
        },

        # 13. 결과를 Excel에 저장
        {
            'action_type': 'excel_save_result',
            'parameters': {
                'status': '{{last_action_result}}',
                'timestamp': '{{current_time}}'
            }
        },

        # 14. 다음 회사로 (반복)
        {
            'action_type': 'excel_loop_end'
        }
    ]
}
```

---

## 실무 활용 시나리오

### 📊 시나리오 1: 대량 이메일 발송

**목표:** 고객 1000명에게 개인화된 이메일 발송

**Excel 파일 (customers.xlsx):**
```
이름, 이메일, 구매상품, 구매일자
김철수, kim@example.com, 노트북, 2025-10-15
이영희, lee@example.com, 마우스, 2025-10-20
```

**자동화 흐름:**
1. Excel에서 고객 정보 읽기
2. 이메일 프로그램에서 "새 메일" 버튼 이미지 인식 클릭
3. Excel 데이터로 이메일 작성
4. 발송
5. 다음 고객 반복

---

### 📦 시나리오 2: ERP 시스템 재고 입력

**목표:** 엑셀 재고 데이터 100건을 ERP에 입력

**자동화 흐름:**
1. Excel에서 재고 데이터 읽기
2. ERP 로그인 화면에서 "로그인" 버튼 이미지 인식
3. 재고 등록 메뉴 찾기 (이미지 인식)
4. Excel 데이터 입력
5. 저장 버튼 클릭 (이미지 인식)
6. 성공/실패 결과를 Excel에 저장

---

### 🌐 시나리오 3: 가격 비교 크롤링

**목표:** 여러 쇼핑몰에서 같은 상품의 가격 수집

**Excel 파일 (products.xlsx):**
```
상품명, 쿠팡URL, 네이버URL, 11번가URL
노트북 ABC모델, http://..., http://..., http://...
```

**자동화 흐름:**
1. Excel에서 상품 정보 읽기
2. 각 URL 방문
3. 가격 영역을 이미지로 찾아서 OCR로 읽기
4. 수집한 가격을 Excel에 저장

---

### 🧪 시나리오 4: UI 테스트 자동화

**목표:** 웹 애플리케이션 100개 화면 테스트

**자동화 흐름:**
1. 로그인 버튼 이미지 인식 → 클릭
2. 메뉴 버튼 이미지 인식 → 클릭
3. 기대하는 화면이 나타나는지 이미지 비교
4. 테스트 결과를 Excel에 저장

---

### 📄 시나리오 5: 보고서 자동 생성

**목표:** 시스템에서 데이터 추출 → Excel 보고서 작성

**자동화 흐름:**
1. 관리 시스템 로그인 (이미지 인식)
2. 보고서 메뉴 클릭 (이미지 인식)
3. 데이터 복사 (Ctrl+C)
4. Excel에 붙여넣기
5. 자동으로 차트 생성
6. PDF로 저장

---

## 비교표: 기능별 차이

| 기능 | 현재 방식 | 이미지 인식 | Excel 연동 | 통합 활용 |
|------|-----------|-------------|------------|-----------|
| **버튼 클릭** | 고정 좌표 | 자동으로 찾음 | - | 자동으로 찾음 |
| **데이터 입력** | 하드코딩 | 하드코딩 | Excel에서 읽음 | Excel에서 읽음 |
| **반복 작업** | 수동 | 수동 | 자동 반복 | 자동 반복 |
| **결과 저장** | 없음 | 없음 | Excel 저장 | Excel 저장 |
| **환경 변화** | ❌ 좌표 수정 | ✅ 자동 적응 | - | ✅ 완전 자동화 |
| **대량 처리** | ❌ 어려움 | ❌ 어려움 | ✅ 쉬움 | ✅ 매우 쉬움 |

---

## 성능 비교

### 작업 시간 비교 (100개 데이터 처리)

| 방법 | 소요 시간 | 정확도 | 유지보수 |
|------|-----------|--------|----------|
| 수동 작업 | 5시간 | 95% | - |
| 기존 ActionFlow | 1시간 | 90% | 어려움 |
| + 이미지 인식 | 50분 | 95% | 보통 |
| + Excel 연동 | 40분 | 95% | 쉬움 |
| + 통합 활용 | **30분** | **98%** | **매우 쉬움** |

---

## 다음 단계

이 고급 기능들을 실제로 사용하려면:

1. **이미지 템플릿 준비**
   - 자주 사용하는 버튼들의 스크린샷 캡처
   - `data/templates/` 폴더에 저장

2. **Excel 파일 준비**
   - 처리할 데이터를 Excel로 정리
   - 컬럼명을 명확하게 설정

3. **테스트 프로젝트 생성**
   - 작은 데이터셋으로 먼저 테스트
   - 정확도 확인 후 대량 데이터 처리

4. **자동화 프로젝트 작성**
   - GUI에서 새 프로젝트 생성
   - 이미지 인식 액션과 Excel 루프 추가
   - 실행 및 결과 확인

---

**ActionFlow Desktop Automator - 단순 매크로에서 강력한 RPA 솔루션으로!** 🚀

© 2025 Photometry4040. All rights reserved.
