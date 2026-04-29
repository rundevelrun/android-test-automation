from selenium.webdriver.common.by import By
from .base_page import BasePage


class OrderCompletePage(BasePage):
    COMPLETE_TITLE = (By.CSS_SELECTOR, "#complete_title")
    ORDER_NUMBER = (By.CSS_SELECTOR, "#order_number")
    ORDER_DATE = (By.CSS_SELECTOR, "#order_date")
    ORDER_ITEMS = (By.CSS_SELECTOR, "#order_items")
    ORDER_TOTAL = (By.CSS_SELECTOR, "#order_total")
    HOME_BTN = (By.CSS_SELECTOR, "#home_btn")
    ORDER_LIST_BTN = (By.CSS_SELECTOR, "#order_list_btn")

    def wait_for_load(self):
        self.find(*self.COMPLETE_TITLE)
        return self

    def get_title(self) -> str:
        return self.get_text(*self.COMPLETE_TITLE)

    def get_order_number(self) -> str:
        return self.get_text(*self.ORDER_NUMBER)

    def get_order_total(self) -> str:
        return self.get_text(*self.ORDER_TOTAL)

    def get_item_rows(self) -> list:
        container = self.find(*self.ORDER_ITEMS)
        return container.find_elements(By.CSS_SELECTOR, ".item-row")

    def click_home(self):
        self.find_clickable(*self.HOME_BTN).click()
        return self
