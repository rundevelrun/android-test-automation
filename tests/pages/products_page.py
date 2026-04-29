from selenium.webdriver.common.by import By
from .base_page import BasePage


class ProductsPage(BasePage):
    SEARCH_INPUT = (By.ID, "search_input")
    SEARCH_BTN = (By.ID, "search_btn")
    FILTER_ALL = (By.ID, "filter_all")
    FILTER_ELECTRONICS = (By.ID, "filter_electronics")
    FILTER_FASHION = (By.ID, "filter_fashion")
    FILTER_FOOD = (By.ID, "filter_food")
    PRODUCT_GRID = (By.ID, "product_grid")
    PRODUCT_CARDS = (By.CSS_SELECTOR, ".product-card")
    NO_RESULT = (By.ID, "no_result")

    def wait_for_load(self):
        self.find(*self.PRODUCT_GRID)
        return self

    def search(self, keyword: str):
        field = self.find(*self.SEARCH_INPUT)
        field.clear()
        field.send_keys(keyword)
        self.find_clickable(*self.SEARCH_BTN).click()
        return self

    def clear_search(self):
        field = self.find(*self.SEARCH_INPUT)
        field.clear()
        self.find_clickable(*self.SEARCH_BTN).click()
        return self

    def apply_filter(self, category: str):
        filter_map = {
            "전체": self.FILTER_ALL,
            "전자기기": self.FILTER_ELECTRONICS,
            "패션": self.FILTER_FASHION,
            "식품": self.FILTER_FOOD,
        }
        self.find_clickable(*filter_map[category]).click()
        return self

    def get_product_count(self) -> int:
        cards = self.driver.find_elements(*self.PRODUCT_CARDS)
        return len(cards)

    def get_product_names(self) -> list[str]:
        cards = self.find_all(*self.PRODUCT_CARDS)
        return [c.find_element(By.CSS_SELECTOR, ".product-name").text for c in cards]

    def click_product(self, index: int = 0):
        cards = self.find_all(*self.PRODUCT_CARDS)
        cards[index].click()
        return self

    def click_product_by_id(self, product_id: int):
        self.find_clickable(By.ID, f"product_{product_id}").click()
        return self

    def is_no_result_visible(self) -> bool:
        el = self.driver.find_element(*self.NO_RESULT)
        return el.is_displayed()

    def is_filter_active(self, category: str) -> bool:
        filter_map = {
            "전체": self.FILTER_ALL,
            "전자기기": self.FILTER_ELECTRONICS,
            "패션": self.FILTER_FASHION,
            "식품": self.FILTER_FOOD,
        }
        el = self.find(*filter_map[category])
        return "active" in el.get_attribute("class")
