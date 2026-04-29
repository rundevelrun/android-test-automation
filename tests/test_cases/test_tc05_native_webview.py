"""TC-05: 네이티브 ↔ WebView Context 전환"""
import pytest
from pages.login_page import LoginPage
from pages.products_page import ProductsPage
from pages.product_detail_page import ProductDetailPage
from pages.native_page import NativePage
from pages.cart_page import CartPage
from conftest import switch_to_native, switch_to_webview
from capabilities import NATIVE_CONTEXT, WEBVIEW_CONTEXT_PREFIX


@pytest.fixture(autouse=True)
def login_and_go_to_detail(webview_driver):
    LoginPage(webview_driver).wait_for_load()
    LoginPage(webview_driver).login("test@example.com", "password123")
    ProductsPage(webview_driver).wait_for_load()
    ProductsPage(webview_driver).click_product_by_id(1)
    ProductDetailPage(webview_driver).wait_for_load()


class TestNativeWebviewSwitch:

    def test_webview_context_is_available(self, driver, webview_driver):
        """앱 실행 후 WebView context가 감지된다"""
        contexts = driver.contexts
        webview_contexts = [c for c in contexts if c.startswith(WEBVIEW_CONTEXT_PREFIX)]
        assert len(webview_contexts) >= 1

    def test_native_context_switch(self, driver, webview_driver):
        """Native context로 전환 후 툴바 타이틀을 네이티브 요소로 읽을 수 있다"""
        switch_to_native(driver)
        title = NativePage(driver).get_toolbar_title()
        assert title in ["상품 상세", "ShopDemo"]
        switch_to_webview(driver)

    def test_buy_now_triggers_native_dialog(self, driver, webview_driver):
        """바로 구매 버튼 클릭 시 네이티브 AlertDialog가 노출된다"""
        ProductDetailPage(webview_driver).click_buy_now()

        switch_to_native(driver)
        native = NativePage(driver)
        assert native.is_dialog_present()
        assert native.get_dialog_title() == "구매 확인"
        assert "구매하시겠습니까" in native.get_dialog_message()

        native.cancel_dialog()
        switch_to_webview(driver)

    def test_dialog_confirm_navigates_to_cart(self, driver, webview_driver):
        """다이얼로그 확인 클릭 시 WebView가 장바구니 페이지로 이동한다"""
        ProductDetailPage(webview_driver).click_buy_now()

        switch_to_native(driver)
        NativePage(driver).wait_for_dialog().confirm_dialog()

        switch_to_webview(driver)
        CartPage(webview_driver).wait_for_load()
        assert "cart" in webview_driver.current_url

    def test_dialog_cancel_stays_on_detail(self, driver, webview_driver):
        """다이얼로그 취소 클릭 시 상세 페이지에 머무른다"""
        ProductDetailPage(webview_driver).click_buy_now()

        switch_to_native(driver)
        NativePage(driver).wait_for_dialog().cancel_dialog()

        switch_to_webview(driver)
        # 취소 후 상세 페이지에 남아있어야 함
        assert "product_detail" in webview_driver.current_url

    def test_cart_badge_updates_in_native_after_webview_action(self, driver, webview_driver):
        """WebView에서 장바구니 담기 후 네이티브 배지 카운트가 업데이트된다"""
        switch_to_native(driver)
        native = NativePage(driver)
        initial_count = native.get_cart_badge_count()

        switch_to_webview(driver)
        ProductDetailPage(webview_driver).add_to_cart()

        switch_to_native(driver)
        updated_count = NativePage(driver).get_cart_badge_count()
        assert updated_count == initial_count + 1
        switch_to_webview(driver)

    def test_toolbar_title_updates_on_page_navigation(self, driver, webview_driver):
        """WebView 페이지 전환 시 네이티브 툴바 타이틀이 갱신된다"""
        # 현재: 상품 상세
        switch_to_native(driver)
        assert NativePage(driver).get_toolbar_title() == "상품 상세"

        switch_to_webview(driver)
        webview_driver.execute_script("AndroidBridge.navigate('products.html')")
        ProductsPage(webview_driver).wait_for_load()

        switch_to_native(driver)
        assert NativePage(driver).get_toolbar_title() == "상품 목록"
        switch_to_webview(driver)
