from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def find(self, by, value):
        return self.wait.until(EC.presence_of_element_located((by, value)))

    def find_clickable(self, by, value):
        return self.wait.until(EC.element_to_be_clickable((by, value)))

    def find_all(self, by, value):
        self.wait.until(EC.presence_of_element_located((by, value)))
        return self.driver.find_elements(by, value)

    def is_visible(self, by, value, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
            return True
        except Exception:
            return False

    def get_text(self, by, value):
        return self.find(by, value).text

    def js(self, script, *args):
        return self.driver.execute_script(script, *args)

    def wait_for_url_contains(self, keyword, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            lambda d: keyword in d.current_url
        )
