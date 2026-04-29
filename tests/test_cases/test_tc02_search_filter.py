"""TC-02: 상품 검색 및 필터"""
import pytest
from pages.login_page import LoginPage
from pages.products_page import ProductsPage

TOTAL_PRODUCTS = 10
ELECTRONICS_COUNT = 4
FASHION_COUNT = 4
FOOD_COUNT = 2


@pytest.fixture(autouse=True)
def login_and_go_to_products(webview_driver):
    LoginPage(webview_driver).wait_for_load()
    LoginPage(webview_driver).login("test@example.com", "password123")
    ProductsPage(webview_driver).wait_for_load()


class TestSearchAndFilter:

    def test_all_products_shown_by_default(self, webview_driver):
        """기본 상태에서 전체 상품이 노출된다"""
        page = ProductsPage(webview_driver)
        assert page.get_product_count() == TOTAL_PRODUCTS

    def test_search_by_keyword_returns_matching_products(self, webview_driver):
        """키워드 검색 시 이름에 해당 키워드가 포함된 상품만 노출된다"""
        page = ProductsPage(webview_driver)
        page.search("이어폰")
        names = page.get_product_names()
        assert len(names) >= 1
        assert all("이어폰" in name for name in names)

    def test_search_no_result_shows_empty_state(self, webview_driver):
        """결과 없는 검색어 입력 시 no-result 메시지가 노출된다"""
        page = ProductsPage(webview_driver)
        page.search("존재하지않는상품XYZ")
        assert page.is_no_result_visible()

    def test_filter_electronics(self, webview_driver):
        """전자기기 필터 선택 시 전자기기 상품만 노출된다"""
        page = ProductsPage(webview_driver)
        page.apply_filter("전자기기")
        assert page.get_product_count() == ELECTRONICS_COUNT
        assert page.is_filter_active("전자기기")

    def test_filter_fashion(self, webview_driver):
        """패션 필터 선택 시 패션 상품만 노출된다"""
        page = ProductsPage(webview_driver)
        page.apply_filter("패션")
        assert page.get_product_count() == FASHION_COUNT

    def test_filter_food(self, webview_driver):
        """식품 필터 선택 시 식품 상품만 노출된다"""
        page = ProductsPage(webview_driver)
        page.apply_filter("식품")
        assert page.get_product_count() == FOOD_COUNT

    def test_filter_all_resets_to_full_list(self, webview_driver):
        """다른 필터 적용 후 전체 필터 선택 시 전체 목록으로 복귀한다"""
        page = ProductsPage(webview_driver)
        page.apply_filter("전자기기")
        page.apply_filter("전체")
        assert page.get_product_count() == TOTAL_PRODUCTS

    def test_search_within_filter(self, webview_driver):
        """필터 적용 상태에서 검색하면 필터 + 검색 교집합 결과가 노출된다"""
        page = ProductsPage(webview_driver)
        page.apply_filter("전자기기")
        page.search("헤드폰")
        names = page.get_product_names()
        assert len(names) >= 1
        assert all("헤드폰" in name for name in names)
