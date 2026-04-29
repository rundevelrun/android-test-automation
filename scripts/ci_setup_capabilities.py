"""
CI 전용: 에뮬레이터의 WebView 버전을 adb로 읽어
tests/capabilities.py를 동적으로 덮어쓴다.

사용법:
  python3 scripts/ci_setup_capabilities.py emulator-5554
"""
import subprocess
import sys
import os
import textwrap

def get_webview_major(device: str) -> str:
    for pkg in ["com.google.android.webview", "com.android.chrome"]:
        result = subprocess.run(
            ["adb", "-s", device, "shell", "dumpsys", "package", pkg],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            if "versionName" in line:
                version = line.strip().split("=")[-1].strip()
                major = version.split(".")[0]
                print(f"[ci_setup] WebView 버전: {version} (major={major})")
                return major
    raise RuntimeError("WebView 버전 감지 실패")


def main():
    device = sys.argv[1] if len(sys.argv) > 1 else "emulator-5554"
    apk_path = os.path.abspath("apk/app-debug.apk")
    major = get_webview_major(device)

    capabilities_content = textwrap.dedent(f"""\
        # CI 자동 생성 — 편집하지 마세요
        APPIUM_SERVER = "http://127.0.0.1:4723"

        CAPABILITIES = {{
            "platformName": "Android",
            "appium:automationName": "UiAutomator2",
            "appium:deviceName": "{device}",
            "appium:app": "{apk_path}",
            "appium:appPackage": "com.example.webviewsample",
            "appium:appActivity": ".MainActivity",
            # ChromeDriver를 Appium이 자동으로 WebView 버전({major}.x)에 맞게 선택
            "appium:chromedriverAutodownload": True,
            "appium:noReset": False,
            "appium:newCommandTimeout": 120,
            "appium:autoGrantPermissions": True,
            "appium:androidDeviceReadyTimeout": 60,
        }}

        WEBVIEW_CONTEXT_PREFIX = "WEBVIEW_com.example.webviewsample"
        NATIVE_CONTEXT = "NATIVE_APP"
    """)

    out_path = os.path.join("tests", "capabilities.py")
    with open(out_path, "w") as f:
        f.write(capabilities_content)

    print(f"[ci_setup] capabilities.py 생성 완료: {out_path}")
    print(f"[ci_setup] 디바이스={device}, APK={apk_path}")


if __name__ == "__main__":
    main()
