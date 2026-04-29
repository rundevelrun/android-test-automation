from selenium.webdriver.common.by import By
from .base_page import BasePage


class OrderCompletePage(BasePage):
    COMPLETE_TITLE = (By.ID, "complete_title")
    ORDER_NUMBER = (By.ID, "order_number")
    ORDER_DATE = (By.ID, "order_date")
    ORDER_ITEMS = (By.ID, "order_items")
    ORDER_TOTAL = (By.ID, "order_total")
    HOME_BTN = (By.ID, "home_btn")
    ORDER_LIST_BTN = (By.ID, "order_list_btn")

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
