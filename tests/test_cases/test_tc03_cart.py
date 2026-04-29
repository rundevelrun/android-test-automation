"""TC-03: 상품 상세 및 장바구니"""
import pytest
from pages.login_page import LoginPage
from pages.products_page import ProductsPage
from pages.product_detail_page import ProductDetailPage
from pages.cart_page import CartPage
from pages.native_page import NativePage
from conftest import switch_to_native, switch_to_webview


@pytest.fixture(autouse=True)
def login_and_go_to_products(webview_driver):
    LoginPage(webview_driver).wait_for_load()
    LoginPage(webview_driver).login("test@example.com", "password123")
    ProductsPage(webview_driver).wait_for_load()


class TestCart:

    def test_product_detail_shows_correct_info(self, webview_driver):
        """상품 클릭 시 상세 페이지에서 이름과 가격이 노출된다"""
        ProductsPage(webview_driver).click_product(index=0)
        detail = ProductDetailPage(webview_driver).wait_for_load()
        assert detail.get_product_name() != ""
        assert "₩" in detail.get_total_price_text()

    def test_qty_increase(self, webview_driver):
        """+ 버튼 클릭 시 수량이 1 증가한다"""
        ProductsPage(webview_driver).click_product(index=0)
        detail = ProductDetailPage(webview_driver).wait_for_load()
        initial_qty = detail.get_quantity()
        detail.increase_qty(1)
        assert detail.get_quantity() == initial_qty + 1

    def test_qty_decrease_not_below_one(self, webview_driver):
        """수량 1에서 - 버튼 클릭해도 0 이하로 내려가지 않는다"""
        ProductsPage(webview_driver).click_product(index=0)
        detail = ProductDetailPage(webview_driver).wait_for_load()
        assert detail.get_quantity() == 1
        detail.decrease_qty(1)
        assert detail.get_quantity() == 1

    def test_total_price_updates_with_qty(self, webview_driver):
        """수량 변경 시 합계 금액이 정확히 업데이트된다"""
        ProductsPage(webview_driver).click_product_by_id(1)  # ₩89,000
        detail = ProductDetailPage(webview_driver).wait_for_load()
        detail.increase_qty(1)  # qty = 2
        assert "178,000" in detail.get_total_price_text()

    def test_add_to_cart_shows_toast(self, webview_driver):
        """장바구니 담기 클릭 시 토스트 메시지가 노출된다"""
        ProductsPage(webview_driver).click_product(index=0)
        detail = ProductDetailPage(webview_driver).wait_for_load()
        detail.add_to_cart()
        assert detail.is_toast_visible()
        assert "장바구니" in detail.get_toast_text()

    def test_cart_badge_increments_after_add(self, webview_driver, driver):
        """장바구니 담기 후 네이티브 툴바 배지 숫자가 증가한다"""
        ProductsPage(webview_driver).click_product(index=0)
        ProductDetailPage(webview_driver).wait_for_load().add_to_cart()

        switch_to_native(driver)
        badge_count = NativePage(driver).get_cart_badge_count()
        assert badge_count >= 1
        switch_to_webview(driver)

    def test_remove_item_from_cart(self, webview_driver):
        """장바구니에서 상품 삭제 시 빈 장바구니 상태가 된다"""
        ProductsPage(webview_driver).click_product_by_id(1)
        ProductDetailPage(webview_driver).wait_for_load().add_to_cart()

        webview_driver.execute_script("AndroidBridge.navigate('cart.html')")
        cart = CartPage(webview_driver).wait_for_load()
        cart.remove_item(1)
        cart.wait_for_empty()
        assert cart.is_empty()
