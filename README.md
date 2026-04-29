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

| TC | 시나리오 | 주요 검증 항목 |
|----|---------|--------------|
| TC-01 | 로그인 플로우 | 정상 로그인, 오류 메시지, 빈 필드 유효성 |
| TC-02 | 상품 검색/필터 | 검색 결과, 카테고리 필터, 빈 결과 처리 |
| TC-03 | 장바구니 | 상품 추가/삭제, 수량 변경, 합계 계산 |
| TC-04 | E2E 주문 | 로그인 → 상품 선택 → 장바구니 → 결제 전체 플로우 |
| TC-05 | Native↔WebView 전환 | Context 전환, 네이티브 다이얼로그, 카트 뱃지 업데이트 |
| TC-06 | 네트워크 예외 | 오프라인 상태 처리, 재시도 동작 |
| TC-07 | 에러 케이스 | 계정 잠금, 품절 처리, 수량 초과, 결제 실패 |

총 **59개 테스트 케이스** 자동화

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
