"""TC-01: 로그인 플로우"""
import pytest
from pages.login_page import LoginPage
from pages.products_page import ProductsPage


VALID_EMAIL = "test@example.com"
VALID_PASSWORD = "password123"


@pytest.fixture(autouse=True)
def go_to_login(webview_driver):
    """각 테스트 전 로그인 페이지가 로드됐는지 확인"""
    LoginPage(webview_driver).wait_for_load()


class TestLogin:

    def test_login_page_loads(self, webview_driver):
        """로그인 페이지의 핵심 요소가 노출된다"""
        page = LoginPage(webview_driver)
        assert page.find(*LoginPage.EMAIL).is_displayed()
        assert page.find(*LoginPage.PASSWORD).is_displayed()
        assert page.find(*LoginPage.LOGIN_BTN).is_displayed()

    def test_valid_login_navigates_to_products(self, webview_driver):
        """정상 계정으로 로그인하면 상품 목록 페이지로 이동한다"""
        LoginPage(webview_driver).login(VALID_EMAIL, VALID_PASSWORD)
        ProductsPage(webview_driver).wait_for_load()
        assert "products" in webview_driver.current_url

    def test_wrong_password_shows_error(self, webview_driver):
        """잘못된 비밀번호 입력 시 에러 메시지가 노출된다"""
        page = LoginPage(webview_driver)
        page.login(VALID_EMAIL, "wrongpassword")
        assert page.is_error_visible()
        assert "올바르지 않습니다" in page.get_error_message()

    def test_wrong_email_shows_error(self, webview_driver):
        """존재하지 않는 이메일 입력 시 에러 메시지가 노출된다"""
        page = LoginPage(webview_driver)
        page.login("nobody@example.com", VALID_PASSWORD)
        assert page.is_error_visible()

    def test_empty_email_shows_validation_error(self, webview_driver):
        """이메일 미입력 시 에러 메시지가 노출된다"""
        page = LoginPage(webview_driver)
        page.enter_password(VALID_PASSWORD).click_login()
        assert page.is_error_visible()
        assert "모두 입력" in page.get_error_message()

    def test_empty_password_shows_validation_error(self, webview_driver):
        """비밀번호 미입력 시 에러 메시지가 노출된다"""
        page = LoginPage(webview_driver)
        page.enter_email(VALID_EMAIL).click_login()
        assert page.is_error_visible()

    def test_error_clears_on_valid_login(self, webview_driver):
        """에러 노출 후 올바른 계정 입력 시 에러가 사라지고 이동한다"""
        page = LoginPage(webview_driver)
        page.login(VALID_EMAIL, "wrong")
        assert page.is_error_visible()

        page.login(VALID_EMAIL, VALID_PASSWORD)
        ProductsPage(webview_driver).wait_for_load()
        assert "products" in webview_driver.current_url
