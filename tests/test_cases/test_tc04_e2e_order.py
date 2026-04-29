"""TC-04: E2E 주문 완료 플로우"""
import pytest
from pages.login_page import LoginPage
from pages.products_page import ProductsPage
from pages.product_detail_page import ProductDetailPage
from pages.cart_page import CartPage
from pages.order_complete_page import OrderCompletePage


class TestE2EOrder:

    def test_full_order_flow(self, webview_driver):
        """로그인 → 상품 선택 → 장바구니 → 주문까지 전체 플로우가 정상 동작한다"""
        # Step 1: 로그인
        LoginPage(webview_driver).wait_for_load()
        LoginPage(webview_driver).login("test@example.com", "password123")

        # Step 2: 상품 선택
        ProductsPage(webview_driver).wait_for_load()
        ProductsPage(webview_driver).click_product_by_id(1)

        # Step 3: 수량 설정 후 장바구니 추가
        detail = ProductDetailPage(webview_driver).wait_for_load()
        detail.increase_qty(1)  # qty = 2
        detail.add_to_cart()

        # Step 4: 장바구니로 이동
        webview_driver.execute_script("AndroidBridge.navigate('cart.html')")
        cart = CartPage(webview_driver).wait_for_load()
        assert cart.get_item_count() == 1

        # Step 5: 주문
        total_text = cart.get_total_price_text()
        cart.click_order()

        # Step 6: 완료 페이지 검증
        complete = OrderCompletePage(webview_driver).wait_for_load()
        assert "완료" in complete.get_title()
        order_number = complete.get_order_number()
        assert order_number.startswith("ORD-")
        assert complete.get_order_total() != "₩0"

    def test_order_number_is_unique_per_order(self, webview_driver):
        """주문마다 고유한 주문번호가 생성된다"""
        def place_order():
            LoginPage(webview_driver).wait_for_load()
            LoginPage(webview_driver).login("test@example.com", "password123")
            ProductsPage(webview_driver).wait_for_load()
            ProductsPage(webview_driver).click_product_by_id(1)
            ProductDetailPage(webview_driver).wait_for_load().add_to_cart()
            webview_driver.execute_script("AndroidBridge.navigate('cart.html')")
            CartPage(webview_driver).wait_for_load().click_order()
            return OrderCompletePage(webview_driver).wait_for_load().get_order_number()

        order1 = place_order()
        # 홈으로 돌아가서 두 번째 주문
        webview_driver.execute_script("AndroidBridge.navigate('login.html')")
        order2 = place_order()

        assert order1 != order2

    def test_order_complete_shows_correct_items(self, webview_driver):
        """주문 완료 페이지에서 주문한 상품 정보가 정확히 표시된다"""
        LoginPage(webview_driver).wait_for_load()
        LoginPage(webview_driver).login("test@example.com", "password123")
        ProductsPage(webview_driver).wait_for_load()
        ProductsPage(webview_driver).click_product_by_id(5)  # 유기농 그래놀라 ₩15,000

        ProductDetailPage(webview_driver).wait_for_load().add_to_cart()
        webview_driver.execute_script("AndroidBridge.navigate('cart.html')")
        CartPage(webview_driver).wait_for_load().click_order()

        complete = OrderCompletePage(webview_driver).wait_for_load()
        item_rows = complete.get_item_rows()
        assert len(item_rows) == 1
        assert "그래놀라" in item_rows[0].text

    def test_multiple_items_order(self, webview_driver):
        """여러 상품을 장바구니에 담고 한 번에 주문할 수 있다"""
        LoginPage(webview_driver).wait_for_load()
        LoginPage(webview_driver).login("test@example.com", "password123")
        ProductsPage(webview_driver).wait_for_load()

        # 상품 1 추가
        ProductsPage(webview_driver).click_product_by_id(1)
        ProductDetailPage(webview_driver).wait_for_load().add_to_cart()
        webview_driver.execute_script("AndroidBridge.navigate('products.html')")
        ProductsPage(webview_driver).wait_for_load()

        # 상품 2 추가
        ProductsPage(webview_driver).click_product_by_id(5)
        ProductDetailPage(webview_driver).wait_for_load().add_to_cart()

        webview_driver.execute_script("AndroidBridge.navigate('cart.html')")
        cart = CartPage(webview_driver).wait_for_load()
        assert cart.get_item_count() == 2
        cart.click_order()

        complete = OrderCompletePage(webview_driver).wait_for_load()
        assert len(complete.get_item_rows()) == 2
