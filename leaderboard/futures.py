from enum import Enum


class TypeFilter(Enum):
    USD_M = "UM"
    COIN_M = "CM"

    def js_click(self):
        return f'document.querySelector("#{self.value} > div").click()'

    def click(self, driver):
        driver.execute_script(self.js_click())


class TimeFilter(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    TOTAL = "all"

    def js_click(self):
        return f'document.querySelector("#{self.value} > div").click()'

    def click(self, driver):
        driver.execute_script(self.js_click())
