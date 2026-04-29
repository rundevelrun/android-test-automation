from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy


class NativePage:
    """네이티브 컨텍스트 전용 페이지 — UIAutomator2로 요소 탐색"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    # 상단 툴바 (네이티브 뷰)
    TOOLBAR_TITLE = (By.XPATH, '//*[@content-desc="toolbar_title"]')
    CART_BADGE = (By.XPATH, '//*[@content-desc="cart_badge"]')

    # 시스템 AlertDialog 버튼
    DIALOG_POSITIVE = (AppiumBy.ID, "android:id/button1")   # 확인
    DIALOG_NEGATIVE = (AppiumBy.ID, "android:id/button2")   # 취소
    DIALOG_TITLE = (AppiumBy.ID, "android:id/alertTitle")
    DIALOG_MESSAGE = (AppiumBy.ID, "android:id/message")

    def get_toolbar_title(self) -> str:
        return self.wait.until(
            EC.presence_of_element_located(self.TOOLBAR_TITLE)
        ).text

    def get_cart_badge_count(self) -> int:
        text = self.wait.until(
            EC.presence_of_element_located(self.CART_BADGE)
        ).text
        return int(text) if text.isdigit() else 0

    def wait_for_dialog(self, timeout: int = 8):
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.DIALOG_TITLE)
        )
        return self

    def get_dialog_title(self) -> str:
        return self.driver.find_element(*self.DIALOG_TITLE).text

    def get_dialog_message(self) -> str:
        return self.driver.find_element(*self.DIALOG_MESSAGE).text

    def confirm_dialog(self):
        self.driver.find_element(*self.DIALOG_POSITIVE).click()

    def cancel_dialog(self):
        self.driver.find_element(*self.DIALOG_NEGATIVE).click()

    def is_dialog_present(self, timeout: int = 5) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.DIALOG_TITLE)
            )
            return True
        except Exception:
            return False
