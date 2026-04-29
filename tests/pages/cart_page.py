from selenium.webdriver.common.by import By
from .base_page import BasePage


class CartPage(BasePage):
    ORDER_BTN = (By.ID, "order_btn")
    SUBTOTAL_PRICE = (By.ID, "subtotal_price")
    TOTAL_PRICE = (By.ID, "total_price")
    EMPTY_STATE = (By.CSS_SELECTOR, ".empty-state")
    CART_ITEMS = (By.CSS_SELECTOR, ".cart-item")

    def wait_for_load(self):
        self.find(*self.ORDER_BTN)
        return self

    def wait_for_empty(self):
        self.find(*self.EMPTY_STATE)
        return self

    def is_empty(self) -> bool:
        return self.is_visible(*self.EMPTY_STATE, timeout=5)

    def get_item_count(self) -> int:
        return len(self.driver.find_elements(*self.CART_ITEMS))

    def get_item_qty(self, product_id: int) -> int:
        el = self.driver.find_element(By.ID, f"qty_{product_id}")
        return int(el.text)

    def change_item_qty(self, product_id: int, delta: int):
        item = self.find(By.ID, f"cart_item_{product_id}")
        btn_selector = ".qty-btn:first-of-type" if delta < 0 else ".qty-btn:last-of-type"
        btn = item.find_element(By.CSS_SELECTOR, btn_selector)
        for _ in range(abs(delta)):
            btn.click()
        return self

    def remove_item(self, product_id: int):
        item = self.find(By.ID, f"cart_item_{product_id}")
        item.find_element(By.CSS_SELECTOR, ".remove-btn").click()
        return self

    def get_total_price_text(self) -> str:
        return self.get_text(*self.TOTAL_PRICE)

    def click_order(self):
        self.find_clickable(*self.ORDER_BTN).click()
        return self
