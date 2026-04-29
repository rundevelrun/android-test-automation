"""TC-06: 네트워크 예외 처리"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.login_page import LoginPage
from pages.products_page import ProductsPage
from conftest import switch_to_native, switch_to_webview


def set_network(driver, enable: bool):
    """ADB로 에뮬레이터 네트워크 연결/해제"""
    import subprocess
    if enable:
        subprocess.run(["adb", "shell", "svc", "wifi", "enable"], check=True)
        subprocess.run(["adb", "shell", "svc", "data", "enable"], check=True)
    else:
        subprocess.run(["adb", "shell", "svc", "wifi", "disable"], check=True)
        subprocess.run(["adb", "shell", "svc", "data", "disable"], check=True)


@pytest.fixture()
def offline_driver(driver):
    """테스트 전 오프라인 전환, 종료 후 복구"""
    set_network(driver, False)
    switch_to_webview(driver)
    yield driver
    switch_to_native(driver)
    set_network(driver, True)


class TestNetwork:

    def test_offline_page_shows_retry_button(self, offline_driver):
        """오프라인 상태에서 offline 페이지 진입 시 재시도 버튼이 노출된다"""
        offline_driver.execute_script("AndroidBridge.navigate('offline.html')")
        retry_btn = WebDriverWait(offline_driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#retry_btn"))
        )
        assert retry_btn.is_displayed()

    @pytest.mark.skip(reason="CI 에뮬레이터에서 adb svc wifi disable이 AndroidBridge 네트워크 감지에 반영되지 않음")
    def test_offline_status_shows_on_page(self, offline_driver):
        """오프라인 상태에서 네트워크 상태 텍스트가 '오프라인'을 포함한다"""
        offline_driver.execute_script("AndroidBridge.navigate('offline.html')")
        status_el = WebDriverWait(offline_driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#network_status"))
        )
        assert "오프라인" in status_el.text

    @pytest.mark.skip(reason="CI 에뮬레이터에서 adb svc wifi disable이 AndroidBridge 네트워크 감지에 반영되지 않음")
    def test_retry_when_offline_shows_still_disconnected(self, offline_driver):
        """오프라인 상태에서 재시도 클릭 시 연결 안됨 메시지가 유지된다"""
        offline_driver.execute_script("AndroidBridge.navigate('offline.html')")
        retry_btn = WebDriverWait(offline_driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#retry_btn"))
        )
        retry_btn.click()
        status_el = offline_driver.find_element(By.CSS_SELECTOR, "#network_status")
        assert "연결되지 않았습니다" in status_el.text or "오프라인" in status_el.text

    @pytest.mark.skip(reason="CI 에뮬레이터에서 adb svc wifi disable이 AndroidBridge 네트워크 감지에 반영되지 않음")
    def test_retry_after_network_recovery_navigates_to_products(self, driver, webview_driver):
        """오프라인 → 온라인 복구 후 재시도 클릭 시 상품 목록으로 이동한다"""
        switch_to_native(driver)
        set_network(driver, False)
        switch_to_webview(driver)

        webview_driver.execute_script("AndroidBridge.navigate('offline.html')")
        WebDriverWait(webview_driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#retry_btn"))
        )

        switch_to_native(driver)
        set_network(driver, True)
        switch_to_webview(driver)

        retry_btn = WebDriverWait(webview_driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#retry_btn"))
        )
        retry_btn.click()

        ProductsPage(webview_driver).wait_for_load()
        assert "products" in webview_driver.current_url

    def test_login_works_after_network_recovery(self, driver, webview_driver):
        """네트워크 복구 후 로그인이 정상 동작한다"""
        switch_to_native(driver)
        set_network(driver, False)
        set_network(driver, True)
        switch_to_webview(driver)

        webview_driver.execute_script("AndroidBridge.navigate('login.html')")
        LoginPage(webview_driver).wait_for_load()
        LoginPage(webview_driver).login("test@example.com", "password123")
        ProductsPage(webview_driver).wait_for_load()
        assert "products" in webview_driver.current_url
