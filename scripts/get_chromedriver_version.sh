#!/usr/bin/env bash
# 연결된 에뮬레이터/디바이스의 WebView 버전을 읽어
# 맞는 ChromeDriver 다운로드 URL을 출력한다

set -e

DEVICE=${1:-""}  # adb -s 옵션용, 생략하면 기본 디바이스

ADB_CMD="adb"
if [ -n "$DEVICE" ]; then
  ADB_CMD="adb -s $DEVICE"
fi

echo "=== WebView / Chrome 버전 감지 ==="

# 1. 앱 패키지의 WebView 엔진 버전 확인
WEBVIEW_VERSION=$($ADB_CMD shell dumpsys package com.google.android.webview 2>/dev/null \
  | grep versionName | head -1 | awk -F'=' '{print $2}' | tr -d ' ')

CHROME_VERSION=$($ADB_CMD shell dumpsys package com.android.chrome 2>/dev/null \
  | grep versionName | head -1 | awk -F'=' '{print $2}' | tr -d ' ')

if [ -n "$WEBVIEW_VERSION" ]; then
  echo "WebView 버전: $WEBVIEW_VERSION"
  MAJOR=$(echo "$WEBVIEW_VERSION" | cut -d. -f1)
elif [ -n "$CHROME_VERSION" ]; then
  echo "Chrome 버전 (WebView 대체): $CHROME_VERSION"
  MAJOR=$(echo "$CHROME_VERSION" | cut -d. -f1)
else
  echo "[ERROR] WebView/Chrome 버전을 감지할 수 없습니다."
  echo "에뮬레이터가 실행 중인지, adb devices로 연결 확인 바랍니다."
  exit 1
fi

echo "Major 버전: $MAJOR"
echo ""

# 2. ChromeDriver 다운로드 URL 안내
# ChromeDriver 115+ 부터는 CfT(Chrome for Testing) 사용
if [ "$MAJOR" -ge 115 ]; then
  echo "=== ChromeDriver $MAJOR 다운로드 (Chrome for Testing) ==="
  VERSIONS_URL="https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
  echo "최신 $MAJOR.x 버전 확인:"
  echo "  curl -s '$VERSIONS_URL' | python3 -c \\"
  echo "    \"import sys,json; data=json.load(sys.stdin); \\"
  echo "     vers=[v for v in data['versions'] if v['version'].startswith('$MAJOR.')]; \\"
  echo "     last=vers[-1]; print(last['version']); \\"
  echo "     dl=[d for d in last['downloads'].get('chromedriver',[]) if d['platform']=='linux64']; \\"
  echo "     print(dl[0]['url'] if dl else 'linux64 없음')\""
else
  # 114 이하는 구 방식
  echo "=== ChromeDriver $MAJOR 다운로드 (구 방식) ==="
  LATEST_URL="https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$MAJOR"
  echo "버전 확인: curl -s '$LATEST_URL'"
  echo "다운로드: https://chromedriver.storage.googleapis.com/<버전>/chromedriver_linux64.zip"
fi

echo ""
echo "=== capabilities.py 설정 예시 ==="
echo "\"appium:chromedriverExecutable\": \"/path/to/chromedriver\","
echo ""
echo "또는 Appium이 자동 관리하게 하려면:"
echo "\"appium:chromedriverAutodownload\": True,"
echo "(appium-uiautomator2-driver 2.x 이상 필요)"
