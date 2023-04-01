from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

DIN = '02510839'
product_name = 'VYEPTI'


options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")

DRIVER_PATH = '.chromedriver'
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

driver.get("https://health-products.canada.ca/dpd-bdpp/")
DIN_field = driver.find_element(By.ID, "din").send_keys(DIN)
product_field = driver.find_element(By.ID, "product").send_keys(product_name)
search = driver.find_element("xpath", "//input[@value='Search']").click()

print(driver.page_source)

driver.quit()