#!/usr/bin/env sh
set -e

DEVICE=$(adb devices | grep -v "List of" | grep "device$" | awk '{print $1}' | head -1)
echo "Device: $DEVICE"

if [ -n "$DEVICE" ]; then
  adb -s "$DEVICE" uninstall com.example.webviewsample || true
  adb -s "$DEVICE" install apk/app-debug.apk
else
  adb uninstall com.example.webviewsample || true
  adb install apk/app-debug.apk
  DEVICE=$(adb devices | grep -v "List of" | grep "device$" | awk '{print $1}' | head -1)
fi
echo "APK installed (device: $DEVICE)"

python3 scripts/ci_setup_capabilities.py "$DEVICE"

cd tests
mkdir -p reports
pytest test_cases/ \
  -v \
  --html=reports/report.html \
  --self-contained-html \
  --junitxml=reports/junit.xml \
  -p no:cacheprovider \
  || true
