APPIUM_SERVER = "http://127.0.0.1:4723"

CAPABILITIES = {
    "platformName": "Android",
    "appium:automationName": "UiAutomator2",
    "appium:deviceName": "Android Emulator",  # adb devices 출력값으로 교체
    "appium:app": "/path/to/WebViewSample.apk",  # 빌드된 APK 경로로 교체
    "appium:appPackage": "com.example.webviewsample",
    "appium:appActivity": ".MainActivity",
    "appium:chromedriverExecutable": "/path/to/chromedriver",  # ChromeDriver 경로로 교체
    "appium:noReset": False,
    "appium:newCommandTimeout": 60,
    "appium:autoGrantPermissions": True,
}

# WebView context 전환에 사용하는 context 이름 prefix
WEBVIEW_CONTEXT_PREFIX = "WEBVIEW_com.example.webviewsample"
NATIVE_CONTEXT = "NATIVE_APP"
