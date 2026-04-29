# JavascriptInterface 메서드는 난독화 제외 (WebView 브릿지 보호)
-keepclassmembers class com.example.webviewsample.MainActivity$AndroidBridge {
    @android.webkit.JavascriptInterface <methods>;
}
