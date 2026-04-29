package com.example.webviewsample

import android.app.AlertDialog
import android.os.Bundle
import android.webkit.JavascriptInterface
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private lateinit var cartBadge: TextView
    private var cartCount = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.webview)
        cartBadge = findViewById(R.id.cart_badge)

        setupWebView()
        webView.loadUrl("file:///android_asset/login.html")
    }

    private fun setupWebView() {
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            // Appium + ChromeDriver가 WebView 내부에 접근하기 위해 필수
            WebView.setWebContentsDebuggingEnabled(true)
        }

        // JavaScript → Android 네이티브 브릿지
        webView.addJavascriptInterface(AndroidBridge(), "AndroidBridge")

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                val url = request.url.toString()
                // 내부 asset 페이지는 WebView에서 처리
                if (url.startsWith("file:///android_asset/")) {
                    return false
                }
                return false
            }

            override fun onPageFinished(view: WebView, url: String) {
                super.onPageFinished(view, url)
                // 페이지 전환 시 툴바 타이틀 업데이트
                val title = when {
                    url.contains("login") -> "로그인"
                    url.contains("products") -> "상품 목록"
                    url.contains("product_detail") -> "상품 상세"
                    url.contains("cart") -> "장바구니"
                    url.contains("order_complete") -> "주문 완료"
                    else -> "ShopDemo"
                }
                findViewById<TextView>(R.id.toolbar_title).text = title
            }
        }
    }

    // JavaScript에서 호출하는 네이티브 브릿지 메서드들
    inner class AndroidBridge {

        // TC-05: WebView → 네이티브 다이얼로그 호출
        @JavascriptInterface
        fun showNativeDialog(title: String, message: String) {
            runOnUiThread {
                AlertDialog.Builder(this@MainActivity)
                    .setTitle(title)
                    .setMessage(message)
                    .setPositiveButton("확인") { dialog, _ ->
                        dialog.dismiss()
                        // 확인 후 WebView에 콜백
                        webView.evaluateJavascript("onNativeDialogConfirmed()", null)
                    }
                    .setNegativeButton("취소") { dialog, _ ->
                        dialog.dismiss()
                        webView.evaluateJavascript("onNativeDialogCancelled()", null)
                    }
                    .show()
            }
        }

        // TC-03: 장바구니 카운트 업데이트 (네이티브 배지)
        @JavascriptInterface
        fun updateCartBadge(count: Int) {
            cartCount = count
            runOnUiThread {
                cartBadge.text = count.toString()
            }
        }

        // TC-06: 네트워크 상태 확인 요청
        @JavascriptInterface
        fun checkNetworkStatus(): Boolean {
            val cm = getSystemService(android.content.Context.CONNECTIVITY_SERVICE)
                as android.net.ConnectivityManager
            val network = cm.activeNetwork ?: return false
            val caps = cm.getNetworkCapabilities(network) ?: return false
            return caps.hasCapability(android.net.NetworkCapabilities.NET_CAPABILITY_INTERNET)
        }

        // 페이지 이동 헬퍼 (JavaScript에서 asset 페이지 이동 시 사용)
        @JavascriptInterface
        fun navigate(page: String) {
            runOnUiThread {
                webView.loadUrl("file:///android_asset/$page")
            }
        }
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}
