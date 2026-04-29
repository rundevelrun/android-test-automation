from selenium.webdriver.common.by import By
from .base_page import BasePage


class LoginPage(BasePage):
    EMAIL = (By.CSS_SELECTOR, "#email")
    PASSWORD = (By.CSS_SELECTOR, "#password")
    LOGIN_BTN = (By.CSS_SELECTOR, "#login_btn")
    ERROR_MSG = (By.CSS_SELECTOR, "#error_msg")

    def wait_for_load(self):
        self.find(*self.LOGIN_BTN)
        return self

    def enter_email(self, email: str):
        field = self.find(*self.EMAIL)
        field.clear()
        field.send_keys(email)
        return self

    def enter_password(self, password: str):
        field = self.find(*self.PASSWORD)
        field.clear()
        field.send_keys(password)
        return self

    def click_login(self):
        self.find_clickable(*self.LOGIN_BTN).click()
        return self

    def login(self, email: str, password: str):
        self.enter_email(email).enter_password(password).click_login()

    def get_error_message(self) -> str:
        el = self.find(*self.ERROR_MSG)
        return el.text

    def is_error_visible(self) -> bool:
        return self.is_visible(*self.ERROR_MSG)
