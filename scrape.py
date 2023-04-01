from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

options = Options()
#options.headless = True
options.add_argument("--window-size=1920,1200")
DRIVER_PATH = '.chromedriver'
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

####################################################
####################################################


#Page 1, entering DIN and product name
DIN = '02510839'
product_name = 'VYEPTI'

driver.get("https://health-products.canada.ca/dpd-bdpp/")
DIN_field = driver.find_element(By.ID, "din").send_keys(DIN)
product_field = driver.find_element(By.ID, "product").send_keys(product_name)
search = driver.find_element("xpath", "//input[@value='Search']").click()


#Page 2, choosing the first instance of result
Click_ProductInfo_HyperLink = driver.find_element("link text", DIN).click()

#Page 3, getting the pdf link
Product_Monograph_URL = driver.find_element(By.CLASS_NAME, 'glyphicon-paperclip').find_element(By.TAG_NAME, 'a').get_attribute('href')
print(Product_Monograph_URL)
driver.quit()