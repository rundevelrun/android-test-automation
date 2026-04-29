"""TC-07: 오류 케이스 — 로그인 잠금, 품절, 수량 초과, 결제 실패, 세션 만료"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.login_page import LoginPage
from pages.products_page import ProductsPage
from pages.product_detail_page import ProductDetailPage
from pages.cart_page import CartPage
from pages.native_page import NativePage
from conftest import switch_to_native, switch_to_webview


def wait(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))


def wait_visible(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, value)))


# ────────────────────────────────────────────────
# TC-07-01 ~ 07-04 : 로그인 잠금
# ────────────────────────────────────────────────
class TestLoginLockout:

    @pytest.fixture(autouse=True)
    def go_to_login(self, webview_driver):
        # sessionStorage 초기화 (잠금 상태 리셋)
        webview_driver.execute_script(
            "sessionStorage.removeItem('login_fail_count');"
            "sessionStorage.removeItem('login_lockout_until');"
        )
        webview_driver.execute_script("AndroidBridge.navigate('login.html')")
        LoginPage(webview_driver).wait_for_load()

    def test_warning_appears_after_3_failures(self, webview_driver):
        """3회 실패 시 '계정 잠김 경고' 문구가 노출된다"""
        page = LoginPage(webview_driver)
        for _ in range(3):
            page.login("test@example.com", "wrong")
            webview_driver.execute_script("document.getElementById('error_msg').classList.remove('show')")

        warn = wait_visible(webview_driver, By.ID, "attempt_warn")
        assert "실패" in warn.text
        assert "잠" in warn.text

    def test_account_locked_after_5_failures(self, webview_driver):
        """5회 연속 로그인 실패 시 계정 잠금 배너가 노출된다"""
        page = LoginPage(webview_driver)
        for _ in range(5):
            page.login("test@example.com", "wrong")

        banner = wait_visible(webview_driver, By.ID, "lockout_banner")
        assert banner.is_displayed()
        assert "잠금" in banner.text

    def test_login_button_disabled_during_lockout(self, webview_driver):
        """잠금 상태에서 로그인 버튼이 비활성화된다"""
        for _ in range(5):
            LoginPage(webview_driver).login("test@example.com", "wrong")

        btn = webview_driver.find_element(By.ID, "login_btn")
        assert not btn.is_enabled()

    def test_lockout_timer_visible(self, webview_driver):
        """잠금 배너에 남은 시간 타이머가 노출된다"""
        for _ in range(5):
            LoginPage(webview_driver).login("test@example.com", "wrong")

        timer = wait_visible(webview_driver, By.ID, "lockout_timer")
        assert "초" in timer.text

    def test_invalid_email_format_shows_error(self, webview_driver):
        """잘못된 이메일 형식 입력 시 형식 오류 메시지가 노출된다"""
        page = LoginPage(webview_driver)
        page.enter_email("notanemail").enter_password("password123").click_login()
        error = wait_visible(webview_driver, By.ID, "error_msg")
        assert "이메일 형식" in error.text


# ────────────────────────────────────────────────
# TC-07-05 ~ 07-08 : 품절 상품
# ────────────────────────────────────────────────
class TestOutOfStock:

    @pytest.fixture(autouse=True)
    def login(self, webview_driver):
        LoginPage(webview_driver).wait_for_load()
        LoginPage(webview_driver).login("test@example.com", "password123")
        ProductsPage(webview_driver).wait_for_load()

    def test_soldout_badge_visible_on_list(self, webview_driver):
        """품절 상품(id=9)에 '품절' 배지가 노출된다"""
        badge = wait_visible(webview_driver, By.ID, "badge_soldout_9")
        assert "품절" in badge.text

    def test_low_stock_badge_visible_on_list(self, webview_driver):
        """재고 2개 상품(id=10)에 '재고 N개' 배지가 노출된다"""
        badge = wait_visible(webview_driver, By.ID, "badge_low_10")
        assert "재고" in badge.text

    def test_soldout_product_click_shows_native_dialog(self, driver, webview_driver):
        """품절 상품 클릭 시 재입고 안내 네이티브 다이얼로그가 노출된다"""
        webview_driver.find_element(By.ID, "product_9").click()
        switch_to_native(driver)
        assert NativePage(driver).is_dialog_present()
        NativePage(driver).cancel_dialog()
        switch_to_webview(driver)

    def test_soldout_product_detail_buttons_disabled(self, webview_driver):
        """품절 상품 상세 진입 시 장바구니·구매 버튼이 비활성화된다"""
        webview_driver.execute_script(
            "sessionStorage.setItem('selected_product_id', '9');"
            "AndroidBridge.navigate('product_detail.html');"
        )
        ProductDetailPage(webview_driver).wait_for_load()
        cart_btn = webview_driver.find_element(By.ID, "add_to_cart_btn")
        buy_btn = webview_driver.find_element(By.ID, "buy_now_btn")
        assert not cart_btn.is_enabled()
        assert not buy_btn.is_enabled()

    def test_soldout_overlay_visible_on_detail(self, webview_driver):
        """품절 상품 상세에서 SOLD OUT 오버레이가 노출된다"""
        webview_driver.execute_script(
            "sessionStorage.setItem('selected_product_id', '9');"
            "AndroidBridge.navigate('product_detail.html');"
        )
        ProductDetailPage(webview_driver).wait_for_load()
        overlay = wait_visible(webview_driver, By.ID, "soldout_overlay")
        assert overlay.is_displayed()

    def test_restock_box_visible_on_soldout_detail(self, webview_driver):
        """품절 상품 상세에서 재입고 알림 신청 박스가 노출된다"""
        webview_driver.execute_script(
            "sessionStorage.setItem('selected_product_id', '9');"
            "AndroidBridge.navigate('product_detail.html');"
        )
        ProductDetailPage(webview_driver).wait_for_load()
        box = wait_visible(webview_driver, By.ID, "restock_box")
        assert box.is_displayed()

    def test_low_stock_status_shown_on_detail(self, webview_driver):
        """재고 부족 상품(id=10) 상세에서 재고 수량 경고 텍스트가 노출된다"""
        webview_driver.execute_script(
            "sessionStorage.setItem('selected_product_id', '10');"
            "AndroidBridge.navigate('product_detail.html');"
        )
        ProductDetailPage(webview_driver).wait_for_load()
        status = wait(webview_driver, By.ID, "stock_status")
        assert "재고" in status.text and "남음" in status.text


# ────────────────────────────────────────────────
# TC-07-09 ~ 07-11 : 수량 한도 초과
# ────────────────────────────────────────────────
class TestQuantityLimit:

    @pytest.fixture(autouse=True)
    def go_to_detail(self, webview_driver):
        LoginPage(webview_driver).wait_for_load()
        LoginPage(webview_driver).login("test@example.com", "password123")
        ProductsPage(webview_driver).wait_for_load()
        ProductsPage(webview_driver).click_product_by_id(1)
        ProductDetailPage(webview_driver).wait_for_load()

    def test_qty_cannot_exceed_10(self, webview_driver):
        """+ 버튼을 11번 눌러도 수량은 10을 초과하지 않는다"""
        detail = ProductDetailPage(webview_driver)
        detail.increase_qty(10)
        assert detail.get_quantity() == 10

    def test_qty_limit_warning_shown_at_max(self, webview_driver):
        """수량 10에서 + 버튼 클릭 시 최대 수량 경고 문구가 노출된다"""
        ProductDetailPage(webview_driver).increase_qty(9)  # qty = 10
        webview_driver.find_element(By.ID, "qty_plus").click()  # 11 시도
        warn = wait_visible(webview_driver, By.ID, "qty_limit_warn")
        assert warn.is_displayed()
        assert "10개" in warn.text

    def test_cart_limit_warning_when_cart_already_full(self, webview_driver):
        """장바구니에 이미 10개 담긴 상태에서 추가 시 한도 경고가 노출된다"""
        # 장바구니에 동일 상품 10개 강제 설정
        webview_driver.execute_script(
            "sessionStorage.setItem('cart', JSON.stringify("
            "[{id:1, name:'무선 블루투스 이어폰', price:89000, qty:10}]));"
        )
        ProductDetailPage(webview_driver).add_to_cart()
        warn = wait_visible(webview_driver, By.ID, "cart_limit_warn")
        assert warn.is_displayed()
        assert "최대" in warn.text


# ────────────────────────────────────────────────
# TC-07-12 ~ 07-14 : 결제 실패 & 쿠폰
# ────────────────────────────────────────────────
class TestPaymentAndCoupon:

    @pytest.fixture(autouse=True)
    def go_to_cart_with_item(self, webview_driver):
        LoginPage(webview_driver).wait_for_load()
        LoginPage(webview_driver).login("test@example.com", "password123")
        webview_driver.execute_script(
            "sessionStorage.setItem('cart', JSON.stringify("
            "[{id:1, name:'무선 블루투스 이어폰', price:89000, qty:1}]));"
            "AndroidBridge.navigate('cart.html');"
        )
        CartPage(webview_driver).wait_for_load()

    def test_invalid_coupon_shows_error(self, webview_driver):
        """존재하지 않는 쿠폰 코드 입력 시 오류 메시지가 노출된다"""
        webview_driver.find_element(By.ID, "coupon_input").send_keys("INVALID999")
        webview_driver.find_element(By.ID, "apply_coupon_btn").click()
        msg = wait_visible(webview_driver, By.ID, "coupon_msg")
        assert "유효하지 않은" in msg.text

    def test_valid_coupon_applies_discount(self, webview_driver):
        """유효한 쿠폰(SAVE10) 입력 시 할인이 적용되고 성공 메시지가 노출된다"""
        webview_driver.find_element(By.ID, "coupon_input").send_keys("SAVE10")
        webview_driver.find_element(By.ID, "apply_coupon_btn").click()
        msg = wait_visible(webview_driver, By.ID, "coupon_msg")
        assert "적용" in msg.text

        # 할인 금액이 total_price에 반영됐는지 확인 (재렌더링 후 summary 확인)
        subtotal_el = webview_driver.find_element(By.ID, "subtotal_price")
        assert "89,000" in subtotal_el.text  # 원가
        total_el = webview_driver.find_element(By.ID, "total_price")
        # 10% 할인: 89000 - 8900 = 80100 + 배송비 3000 = 83100
        assert "89,000" not in total_el.text  # 할인 적용으로 달라져야 함

    def test_fail_test_coupon_triggers_payment_error(self, webview_driver):
        """FAIL_TEST 쿠폰 적용 후 주문 시 결제 실패 배너가 노출된다"""
        webview_driver.find_element(By.ID, "coupon_input").send_keys("FAIL_TEST")
        webview_driver.find_element(By.ID, "apply_coupon_btn").click()
        wait_visible(webview_driver, By.ID, "coupon_msg")

        webview_driver.find_element(By.ID, "order_btn").click()
        banner = wait_visible(webview_driver, By.ID, "payment_error_banner")
        assert banner.is_displayed()
        assert "결제" in banner.text

        error_code = webview_driver.find_element(By.ID, "payment_error_code").text
        assert "ERR_PAYMENT_" in error_code

    def test_payment_error_does_not_navigate_away(self, webview_driver):
        """결제 실패 시 장바구니 페이지에 그대로 머문다 (주문완료 페이지로 가지 않는다)"""
        webview_driver.find_element(By.ID, "coupon_input").send_keys("FAIL_TEST")
        webview_driver.find_element(By.ID, "apply_coupon_btn").click()
        webview_driver.find_element(By.ID, "order_btn").click()
        assert "cart" in webview_driver.current_url


# ────────────────────────────────────────────────
# TC-07-15 ~ 07-16 : 세션 만료
# ────────────────────────────────────────────────
class TestSessionExpiry:

    def test_session_banner_shown_when_not_logged_in(self, webview_driver):
        """로그인 없이 products 페이지 진입 시 세션 만료 배너가 노출된다"""
        webview_driver.execute_script(
            "sessionStorage.removeItem('logged_in');"
            "AndroidBridge.navigate('products.html');"
        )
        ProductsPage(webview_driver).wait_for_load()
        banner = wait_visible(webview_driver, By.ID, "session_banner")
        assert banner.is_displayed()
        assert "세션" in banner.text

    def test_no_session_banner_when_logged_in(self, webview_driver):
        """정상 로그인 후 products 진입 시 세션 만료 배너가 노출되지 않는다"""
        LoginPage(webview_driver).wait_for_load()
        LoginPage(webview_driver).login("test@example.com", "password123")
        ProductsPage(webview_driver).wait_for_load()
        banner = webview_driver.find_element(By.ID, "session_banner")
        assert not banner.is_displayed()
