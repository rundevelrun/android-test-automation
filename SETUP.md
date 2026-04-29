# 환경 셋업 가이드

## 전체 흐름

```
[PC]
 ├── Appium Server (Node.js)
 │    └── UiAutomator2 Driver
 │         └── ChromeDriver  ←→  WebView (APK 내부)
 ├── Python 테스트 코드
 │    └── Appium Python Client
 └── Android Emulator / 실기기
      └── WebViewSample.apk
```

---

## Step 1. 필수 도구 설치

### Java JDK 11+
```bash
# Ubuntu/Debian
sudo apt install openjdk-17-jdk

# macOS (Homebrew)
brew install openjdk@17

# 확인
java -version
```

### Node.js 18+
```bash
# Ubuntu — nvm 권장
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
nvm install 20
nvm use 20

# macOS
brew install node

# 확인
node -v   # v20.x.x
```

### Android SDK
Android Studio 설치 후 SDK Manager에서:
- **Android SDK Platform-Tools** (adb 포함)
- **Android SDK Build-Tools**
- **Android Emulator**
- **API 레벨 34** (또는 테스트 대상 버전)

```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
export ANDROID_HOME=$HOME/Android/Sdk          # macOS: $HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/emulator

# 적용
source ~/.bashrc

# 확인
adb version
```

---

## Step 2. Appium 2.x 설치

```bash
# 전역 설치
npm install -g appium

# 확인 (2.x 이상이어야 함)
appium -v

# UiAutomator2 드라이버 설치
appium driver install uiautomator2

# 설치 확인
appium driver list --installed
```

---

## Step 3. ChromeDriver 버전 매칭 (핵심)

WebView 내부는 Chrome 엔진 위에서 동작하므로, **WebView 버전과 ChromeDriver 버전이 일치**해야 합니다.
버전 불일치 시 `Could not get a session` 에러 발생.

### 3-1. 에뮬레이터 WebView 버전 확인

```bash
# 에뮬레이터 실행 후
adb shell dumpsys package com.google.android.webview | grep versionName
# 예: versionName=124.0.6367.82

# Chrome이 WebView로 사용되는 경우
adb shell dumpsys package com.android.chrome | grep versionName
```

### 3-2. ChromeDriver 다운로드

자동화 스크립트 사용:
```bash
./scripts/get_chromedriver_version.sh
```

또는 수동으로:

**WebView 버전 115 이상 (권장)**
```bash
# 버전별 JSON에서 검색
curl -s "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json" \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
major = '124'  # ← 실제 WebView major 버전으로 교체
vers = [v for v in data['versions'] if v['version'].startswith(major + '.')]
last = vers[-1]
print('버전:', last['version'])
dl = [d for d in last['downloads'].get('chromedriver', []) if d['platform'] == 'linux64']
print('URL:', dl[0]['url'] if dl else 'not found')
"

# 다운로드 및 압축 해제
wget <출력된 URL> -O chromedriver.zip
unzip chromedriver.zip
chmod +x chromedriver-linux64/chromedriver
```

**WebView 버전 114 이하 (구버전)**
```bash
MAJOR=114  # 실제 버전으로 교체
LATEST=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$MAJOR")
wget "https://chromedriver.storage.googleapis.com/$LATEST/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
chmod +x chromedriver
```

### 3-3. capabilities.py에 경로 설정

```python
# 방법 A: 경로 직접 지정 (권장)
"appium:chromedriverExecutable": "/home/user/chromedriver/chromedriver",

# 방법 B: Appium 자동 다운로드 (appium-uiautomator2-driver 2.x 이상)
"appium:chromedriverAutodownload": True,
# → Appium이 WebView 버전을 감지해 자동으로 맞는 ChromeDriver 다운로드
```

방법 B를 사용하면 버전 관리를 Appium에 위임할 수 있어 편리합니다.

---

## Step 4. 에뮬레이터 설정

Android Studio → Device Manager → Create Virtual Device

권장 설정:
- **Device**: Pixel 6
- **System Image**: API 34 (Google APIs, x86_64)
- **RAM**: 2048MB 이상

```bash
# CLI로 실행
emulator -avd <AVD_NAME> &

# 연결 확인
adb devices
# 출력 예: emulator-5554   device
```

APK 설치:
```bash
adb install sample-apk/app/build/outputs/apk/debug/app-debug.apk
```

---

## Step 5. Python 환경 설정

```bash
# 가상환경 생성
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 의존성 설치
pip install -r tests/requirements.txt
```

---

## Step 6. capabilities.py 최종 설정

```python
# tests/capabilities.py

APPIUM_SERVER = "http://127.0.0.1:4723"

CAPABILITIES = {
    "platformName": "Android",
    "appium:automationName": "UiAutomator2",
    "appium:deviceName": "emulator-5554",        # adb devices 출력값
    "appium:app": "/absolute/path/to/app-debug.apk",
    "appium:appPackage": "com.example.webviewsample",
    "appium:appActivity": ".MainActivity",
    "appium:chromedriverExecutable": "/path/to/chromedriver",
    "appium:noReset": False,
    "appium:newCommandTimeout": 60,
    "appium:autoGrantPermissions": True,
}
```

---

## Step 7. 실행

터미널 1 — Appium 서버 시작:
```bash
./scripts/start_appium.sh
# 또는: appium --relaxed-security
```

터미널 2 — 환경 점검:
```bash
./scripts/check_env.sh
```

터미널 3 — 테스트 실행:
```bash
cd tests
source ../.venv/bin/activate

pytest                                        # 전체 실행
pytest test_cases/test_tc01_login.py          # TC-01만
pytest test_cases/test_tc05_native_webview.py # TC-05만
pytest -k "login or cart"                     # 키워드 필터
pytest -v --html=reports/report.html          # HTML 리포트 생성
```

---

## 자주 발생하는 에러

| 에러 메시지 | 원인 | 해결 |
|---|---|---|
| `Could not get a session` / `chrome not reachable` | ChromeDriver 버전 불일치 | Step 3 재확인, major 버전 맞추기 |
| `WebView context not found` | WebView가 아직 로드 안 됨 | `conftest.py`의 timeout 늘리기 (기본 15초) |
| `Original error: unknown error` | `setWebContentsDebuggingEnabled` 미설정 | APK의 `MainActivity.kt` 확인 |
| `adb: no devices` | 에뮬레이터 미실행 | `emulator -avd <name>` 실행 |
| `Appium server not running` | 서버 미시작 | `./scripts/start_appium.sh` 실행 |
| `UiAutomator2 driver not found` | 드라이버 미설치 | `appium driver install uiautomator2` |

---

## ChromeDriver 버전 대응표 (참고)

| Android WebView / Chrome | ChromeDriver |
|---|---|
| 124.x | 124.x |
| 120.x | 120.x |
| 114.x | 114.x |
| 112.x | 112.x |

**Major 버전만 일치하면 됩니다.** Minor/patch는 달라도 동작합니다.

---

## 빠른 시작 체크리스트

```
[ ] Java 11+ 설치
[ ] Android Studio + SDK 설치, ANDROID_HOME 설정
[ ] Node.js 18+ 설치
[ ] npm install -g appium
[ ] appium driver install uiautomator2
[ ] 에뮬레이터 생성 및 실행 (adb devices 확인)
[ ] WebView major 버전 확인 후 ChromeDriver 다운로드
[ ] capabilities.py에 APK 경로, 디바이스명, ChromeDriver 경로 설정
[ ] pip install -r tests/requirements.txt
[ ] ./scripts/check_env.sh 로 최종 점검
[ ] Appium 서버 시작 후 pytest 실행
```
