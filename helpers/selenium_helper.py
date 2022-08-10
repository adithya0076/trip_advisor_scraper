from selenium.webdriver.common.by import By


class SeleniumHelper:
    def __init__(self):
        pass

    def find_xpath_element(self, driver, xpath, is_get_text=False):
        try:
            if is_get_text:
                return True, driver.find_element(by=By.XPATH, value=xpath).text
            else:
                return True, driver.find_element(by=By.XPATH, value=xpath)
        except:
            return False, None
