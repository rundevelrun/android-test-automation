# AI를 활용한 Android WebView 테스트 자동화

Claude(AI)와 협업하여 처음부터 끝까지 설계·구현한 Android WebView 테스트 자동화 프로젝트입니다.  
테스트 시나리오 설계 → 샘플 APK 제작 → Appium 테스트 코드 작성 → GitHub Actions CI 구성까지 전 과정을 AI와 함께 진행했습니다.

---

## 프로젝트 구조

```
android-test-automation/
├── sample-apk/                    # 테스트 대상 Android 앱 (Kotlin + WebView)
│   └── app/src/main/
│       ├── assets/                # 로컬 HTML 페이지
│       │   ├── login.html
│       │   ├── products.html
│       │   ├── product_detail.html
│       │   ├── cart.html
│       │   └── order_complete.html
│       └── java/.../MainActivity.kt   # WebView + JS↔Native 브릿지
├── tests/                         # Appium + Python 테스트 코드
│   ├── conftest.py                # Driver fixture, 실패 시 스크린샷 자동 캡처
│   ├── capabilities.py            # Appium 연결 설정
│   ├── pages/                     # Page Object Model
│   │   ├── base_page.py
│   │   ├── login_page.py
│   │   ├── products_page.py
│   │   ├── product_detail_page.py
│   │   ├── cart_page.py
│   │   └── native_page.py
│   └── test_cases/                # 테스트 케이스
│       ├── test_tc01_login.py
│       ├── test_tc02_search_filter.py
│       ├── test_tc03_cart.py
│       ├── test_tc04_e2e_order.py
│       ├── test_tc05_native_webview.py
│       ├── test_tc06_network.py
│       └── test_tc07_error_cases.py
├── scripts/
│   ├── ci_setup_capabilities.py   # CI용 capabilities 동적 생성
│   ├── run_emulator_tests.sh      # 에뮬레이터 내 테스트 실행 스크립트
│   ├── start_appium.sh            # 로컬 Appium 서버 시작
│   └── check_env.sh               # 환경 점검
└── .github/workflows/
    ├── android-test.yml           # 메인 CI 파이프라인
    └── network-test.yml           # TC-06 네트워크 예외 테스트 (별도 스케줄)
```

---

## 샘플 앱 (테스트 대상)

실제 서비스와 유사한 쇼핑몰 앱을 WebView 기반으로 직접 제작했습니다.

### 주요 기능
- **로그인** — 이메일/비밀번호 유효성 검사, 5회 실패 시 30초 계정 잠금
- **상품 목록** — 품절/재고 부족 뱃지, 세션 만료 배너
- **상품 상세** — 품절 오버레이, 수량 제한(최대 10개), 재입고 알림
- **장바구니** — 쿠폰 적용(`SAVE10`, `WELCOME`, `FAIL_TEST`), 결제 오류 처리
- **JS↔Native 브릿지** — `AndroidBridge` JavascriptInterface로 네이티브 다이얼로그 호출, 카트 뱃지 업데이트, 페이지 이동

### 기술 스택
- Kotlin + Android WebView
- `WebView.setWebContentsDebuggingEnabled(true)` — Appium/ChromeDriver WebView 접근 허용
- 로컬 HTML/CSS/JS (assets 폴더) — 외부 서버 없이 동작

---

## 테스트 시나리오 (TC-01 ~ TC-07)

총 **59개 테스트 케이스** 자동화

### TC-01 로그인 플로우 (7개)

| # | 테스트 항목 |
|---|------------|
| 01 | 로그인 페이지의 핵심 요소가 노출된다 |
| 02 | 정상 계정으로 로그인하면 상품 목록 페이지로 이동한다 |
| 03 | 잘못된 비밀번호 입력 시 에러 메시지가 노출된다 |
| 04 | 존재하지 않는 이메일 입력 시 에러 메시지가 노출된다 |
| 05 | 이메일 미입력 시 에러 메시지가 노출된다 |
| 06 | 비밀번호 미입력 시 에러 메시지가 노출된다 |
| 07 | 에러 노출 후 올바른 계정 입력 시 에러가 사라지고 이동한다 |

### TC-02 상품 검색 및 필터 (8개)

| # | 테스트 항목 |
|---|------------|
| 01 | 기본 상태에서 전체 상품이 노출된다 |
| 02 | 키워드 검색 시 이름에 해당 키워드가 포함된 상품만 노출된다 |
| 03 | 결과 없는 검색어 입력 시 no-result 메시지가 노출된다 |
| 04 | 전자기기 필터 선택 시 전자기기 상품만 노출된다 |
| 05 | 패션 필터 선택 시 패션 상품만 노출된다 |
| 06 | 식품 필터 선택 시 식품 상품만 노출된다 |
| 07 | 다른 필터 적용 후 전체 필터 선택 시 전체 목록으로 복귀한다 |
| 08 | 필터 적용 상태에서 검색하면 필터 + 검색 교집합 결과가 노출된다 |

### TC-03 상품 상세 및 장바구니 (7개)

| # | 테스트 항목 |
|---|------------|
| 01 | 상품 클릭 시 상세 페이지에서 이름과 가격이 노출된다 |
| 02 | + 버튼 클릭 시 수량이 1 증가한다 |
| 03 | 수량 1에서 - 버튼 클릭해도 0 이하로 내려가지 않는다 |
| 04 | 수량 변경 시 합계 금액이 정확히 업데이트된다 |
| 05 | 장바구니 담기 클릭 시 토스트 메시지가 노출된다 |
| 06 | 장바구니 담기 후 네이티브 툴바 배지 숫자가 증가한다 |
| 07 | 장바구니에서 상품 삭제 시 빈 장바구니 상태가 된다 |

### TC-04 E2E 주문 완료 플로우 (4개)

| # | 테스트 항목 |
|---|------------|
| 01 | 로그인 → 상품 선택 → 장바구니 → 주문까지 전체 플로우가 정상 동작한다 |
| 02 | 주문마다 고유한 주문번호가 생성된다 |
| 03 | 주문 완료 페이지에서 주문한 상품 정보가 정확히 표시된다 |
| 04 | 여러 상품을 장바구니에 담고 한 번에 주문할 수 있다 |

### TC-05 Native ↔ WebView Context 전환 (7개)

| # | 테스트 항목 |
|---|------------|
| 01 | 앱 실행 후 WebView context가 감지된다 |
| 02 | Native context로 전환 후 툴바 타이틀을 네이티브 요소로 읽을 수 있다 |
| 03 | 바로 구매 버튼 클릭 시 네이티브 AlertDialog가 노출된다 |
| 04 | 다이얼로그 확인 클릭 시 WebView가 장바구니 페이지로 이동한다 |
| 05 | 다이얼로그 취소 클릭 시 상세 페이지에 머무른다 |
| 06 | WebView에서 장바구니 담기 후 네이티브 배지 카운트가 업데이트된다 |
| 07 | WebView 페이지 전환 시 네이티브 툴바 타이틀이 갱신된다 |

### TC-06 네트워크 예외 처리 (5개)

| # | 테스트 항목 | 비고 |
|---|------------|------|
| 01 | 오프라인 상태에서 offline 페이지 진입 시 재시도 버튼이 노출된다 | |
| 02 | 오프라인 상태에서 네트워크 상태 텍스트가 '오프라인'을 포함한다 | CI skip |
| 03 | 오프라인 상태에서 재시도 클릭 시 연결 안됨 메시지가 유지된다 | CI skip |
| 04 | 오프라인 → 온라인 복구 후 재시도 클릭 시 상품 목록으로 이동한다 | CI skip |
| 05 | 네트워크 복구 후 로그인이 정상 동작한다 | |

> CI skip: 에뮬레이터 환경에서 네트워크 차단이 AndroidBridge 감지에 반영되지 않아 실기기 테스트 시에만 실행

### TC-07 에러 케이스 (21개)

| # | 테스트 항목 |
|---|------------|
| **로그인 잠금** | |
| 01 | 3회 실패 시 '계정 잠김 경고' 문구가 노출된다 |
| 02 | 5회 연속 로그인 실패 시 계정 잠금 배너가 노출된다 |
| 03 | 잠금 상태에서 로그인 버튼이 비활성화된다 |
| 04 | 잠금 배너에 남은 시간 타이머가 노출된다 |
| 05 | 잘못된 이메일 형식 입력 시 형식 오류 메시지가 노출된다 |
| **품절 상품** | |
| 06 | 품절 상품(id=9)에 '품절' 배지가 노출된다 |
| 07 | 재고 2개 상품(id=10)에 '재고 N개' 배지가 노출된다 |
| 08 | 품절 상품 클릭 시 재입고 안내 네이티브 다이얼로그가 노출된다 |
| 09 | 품절 상품 상세 진입 시 장바구니·구매 버튼이 비활성화된다 |
| 10 | 품절 상품 상세에서 SOLD OUT 오버레이가 노출된다 |
| 11 | 품절 상품 상세에서 재입고 알림 신청 박스가 노출된다 |
| 12 | 재고 부족 상품(id=10) 상세에서 재고 수량 경고 텍스트가 노출된다 |
| **수량 한도** | |
| 13 | + 버튼을 11번 눌러도 수량은 10을 초과하지 않는다 |
| 14 | 수량 10에서 + 버튼 클릭 시 최대 수량 경고 문구가 노출된다 |
| 15 | 장바구니에 이미 10개 담긴 상태에서 추가 시 한도 경고가 노출된다 |
| **결제 실패 & 쿠폰** | |
| 16 | 존재하지 않는 쿠폰 코드 입력 시 오류 메시지가 노출된다 |
| 17 | 유효한 쿠폰(SAVE10) 입력 시 할인이 적용되고 성공 메시지가 노출된다 |
| 18 | FAIL_TEST 쿠폰 적용 후 주문 시 결제 실패 배너가 노출된다 |
| 19 | 결제 실패 시 장바구니 페이지에 그대로 머문다 |
| **세션 만료** | |
| 20 | 로그인 없이 products 페이지 진입 시 세션 만료 배너가 노출된다 |
| 21 | 정상 로그인 후 products 진입 시 세션 만료 배너가 노출되지 않는다 |

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| 테스트 프레임워크 | Appium 2.x + UiAutomator2 driver |
| 테스트 언어 | Python 3.11 + pytest |
| WebView 자동화 | ChromeDriver (chromedriverAutodownload) |
| 패턴 | Page Object Model (POM) |
| 리포트 | pytest-html + JUnit XML |
| CI/CD | GitHub Actions + android-emulator-runner |
| 에뮬레이터 | Android API 34 (x86_64, google_apis) |

---

## 핵심 구현 포인트

### WebView Context 전환
Appium에서 WebView를 테스트하려면 Native → WebView context로 전환이 필요합니다.

```python
# conftest.py
def switch_to_webview(driver, timeout=15):
    end = time.time() + timeout
    while time.time() < end:
        contexts = driver.contexts
        for ctx in contexts:
            if ctx.startswith("WEBVIEW_com.example.webviewsample"):
                driver.switch_to.context(ctx)
                return
        time.sleep(1)
    raise TimeoutError("WebView context not found")
```

### 실패 시 스크린샷 자동 캡처
테스트 실패 시 자동으로 스크린샷을 찍어 HTML 리포트에 임베드합니다.

```python
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        driver = _driver_store.get(item.nodeid)
        driver.switch_to.context(NATIVE_CONTEXT)
        driver.save_screenshot(filename)
```

### CI 동적 Capabilities 생성
에뮬레이터의 WebView 버전을 자동 감지해 `chromedriverAutodownload: True`로 설정합니다.

```python
# scripts/ci_setup_capabilities.py
version = get_webview_version(device)  # adb dumpsys로 버전 확인
write_capabilities(device, version)    # tests/capabilities.py 자동 생성
```

---

## CI/CD 파이프라인

```
push to main
    │
    ├─ Job 1: Build APK
    │   └─ gradle assembleDebug → artifact 업로드
    │
    └─ Job 2: Appium Test (API 34)
        ├─ APK artifact 다운로드
        ├─ Appium 서버 시작 (백그라운드)
        ├─ Android 에뮬레이터 부팅 (KVM 가속)
        ├─ APK 설치
        ├─ WebView 버전 감지 → capabilities 생성
        ├─ pytest 실행 (59 tests)
        └─ 결과 업로드
            ├─ HTML 리포트
            ├─ JUnit XML (PR 코멘트 자동 표시)
            └─ 실패 스크린샷
```

---

## 로컬 실행

### 사전 준비
- Android Studio / Android SDK
- Node.js 20+
- Python 3.11+
- 실물 기기 또는 에뮬레이터 (API 34 권장)

### 환경 설정

```bash
# Appium 설치
npm install -g appium
appium driver install uiautomator2

# Python 의존성
pip install -r tests/requirements.txt

# 환경 점검
bash scripts/check_env.sh
```

### APK 빌드

```bash
cd sample-apk
gradle assembleDebug
```

### Appium 서버 시작

```bash
bash scripts/start_appium.sh
```

### 테스트 실행

```bash
cd tests
pytest test_cases/ -v --html=reports/report.html --self-contained-html
```

---

## AI 협업 방식

이 프로젝트는 Claude(AI)와 다음 방식으로 협업했습니다.

1. **테스트 시나리오 설계** — 실제 서비스에서 발생할 수 있는 엣지 케이스 도출
2. **샘플 APK 설계 및 구현** — 테스트 가능한 기능(계정 잠금, 품절, 결제 오류 등) 포함
3. **테스트 코드 작성** — Page Object Model 패턴 적용, fixture 설계
4. **CI 파이프라인 구성** — 에뮬레이터 환경 세팅, ChromeDriver 자동 매칭
5. **디버깅** — CI 오류(sh 문법, APK 서명, import 경로 등) 원인 분석 및 수정

AI를 활용하면 테스트 자동화 인프라 구축에 필요한 반복적인 설정 작업과 트러블슈팅 시간을 크게 단축할 수 있습니다.
