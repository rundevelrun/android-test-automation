from selenium.webdriver.common.by import By
from .base_page import BasePage


class ProductDetailPage(BasePage):
    PRODUCT_NAME = (By.CSS_SELECTOR, "#product_name")
    PRODUCT_PRICE = (By.CSS_SELECTOR, "#product_price")
    QTY_MINUS = (By.CSS_SELECTOR, "#qty_minus")
    QTY_PLUS = (By.CSS_SELECTOR, "#qty_plus")
    QTY_VALUE = (By.CSS_SELECTOR, "#qty_value")
    TOTAL_PRICE = (By.CSS_SELECTOR, "#total_price")
    ADD_TO_CART_BTN = (By.CSS_SELECTOR, "#add_to_cart_btn")
    BUY_NOW_BTN = (By.CSS_SELECTOR, "#buy_now_btn")
    TOAST_MSG = (By.CSS_SELECTOR, "#toast_msg")

    def wait_for_load(self):
        self.find(*self.PRODUCT_NAME)
        return self

    def get_product_name(self) -> str:
        return self.get_text(*self.PRODUCT_NAME)

    def get_quantity(self) -> int:
        return int(self.get_text(*self.QTY_VALUE))

    def get_total_price_text(self) -> str:
        return self.get_text(*self.TOTAL_PRICE)

    def increase_qty(self, times: int = 1):
        for _ in range(times):
            self.find_clickable(*self.QTY_PLUS).click()
        return self

    def decrease_qty(self, times: int = 1):
        for _ in range(times):
            self.find_clickable(*self.QTY_MINUS).click()
        return self

    def add_to_cart(self):
        self.find_clickable(*self.ADD_TO_CART_BTN).click()
        return self

    def click_buy_now(self):
        self.find_clickable(*self.BUY_NOW_BTN).click()
        return self

    def is_toast_visible(self) -> bool:
        return self.is_visible(*self.TOAST_MSG, timeout=3)

    def get_toast_text(self) -> str:
        return self.get_text(*self.TOAST_MSG)
