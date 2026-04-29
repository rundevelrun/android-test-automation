#!/usr/bin/env bash
# 환경 사전 점검 스크립트 — 실행 전 필수 도구 설치 여부 확인

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok()   { echo -e "${GREEN}[OK]${NC}    $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC}  $1"; }
fail() { echo -e "${RED}[FAIL]${NC}  $1"; }

echo "===== Android Test Automation — 환경 점검 ====="
echo ""

# 1. Java
if java -version 2>&1 | grep -q "version"; then
  JAVA_VER=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}')
  ok "Java: $JAVA_VER"
else
  fail "Java 미설치 — https://adoptium.net 에서 JDK 11+ 설치"
fi

# 2. Android SDK / adb
if command -v adb &>/dev/null; then
  ADB_VER=$(adb version | head -1)
  ok "adb: $ADB_VER"
else
  fail "adb 미설치 — Android Studio 설치 또는 ANDROID_HOME 환경변수 확인"
fi

# 3. Node.js
if command -v node &>/dev/null; then
  NODE_VER=$(node -v)
  ok "Node.js: $NODE_VER"
else
  fail "Node.js 미설치 — https://nodejs.org (v18 이상 권장)"
fi

# 4. Appium
if command -v appium &>/dev/null; then
  APPIUM_VER=$(appium -v 2>/dev/null)
  ok "Appium: $APPIUM_VER"
else
  fail "Appium 미설치 — 'npm install -g appium' 실행"
fi

# 5. Appium UiAutomator2 드라이버
if appium driver list --installed 2>/dev/null | grep -q "uiautomator2"; then
  ok "Appium UiAutomator2 드라이버 설치됨"
else
  fail "UiAutomator2 미설치 — 'appium driver install uiautomator2' 실행"
fi

# 6. Python
if command -v python3 &>/dev/null; then
  PY_VER=$(python3 --version)
  ok "Python: $PY_VER"
else
  fail "Python3 미설치"
fi

# 7. 연결된 디바이스 / 에뮬레이터
echo ""
echo "--- 연결된 Android 디바이스 ---"
DEVICES=$(adb devices | grep -v "List of" | grep -v "^$")
if [ -z "$DEVICES" ]; then
  warn "연결된 디바이스 없음 — 에뮬레이터를 실행하거나 USB 디버깅 디바이스 연결"
else
  echo "$DEVICES"
  ok "디바이스 감지됨"
fi

# 8. ANDROID_HOME
if [ -n "$ANDROID_HOME" ]; then
  ok "ANDROID_HOME=$ANDROID_HOME"
else
  warn "ANDROID_HOME 환경변수 미설정"
fi

echo ""
echo "===== 점검 완료 ====="
