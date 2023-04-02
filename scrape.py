import pandas as pd
import numpy as np
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def get_ProductMonograph_download_URL(DIN,product_name):
	options = Options()
	options.headless = True
	options.add_argument("--window-size=1920,1200")
	DRIVER_PATH = '.chromedriver'
	driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

	#Page 1, entering DIN and product name
	driver.get("https://health-products.canada.ca/dpd-bdpp/")
	#time.sleep(2)
	DIN_field = driver.find_element(By.ID, "din").send_keys(DIN)
	#time.sleep(2)
	product_field = driver.find_element(By.ID, "product").send_keys(product_name)
	#time.sleep(2)
	search = driver.find_element("xpath", "//input[@value='Search']").click()
	#time.sleep(5)
	#Page 2, choosing the first result
	try:
		Click_ProductInfo_HyperLink = driver.find_element("link text", DIN).click()
		#time.sleep(5)
	#Page 3, getting the pdf link
	except:
		pass

	finally:
		Product_Monograph_URL = driver.find_element(By.CLASS_NAME, 'glyphicon-paperclip').find_element(By.TAG_NAME, 'a').get_attribute('href')
		#time.sleep(5)
		driver.quit()
	return Product_Monograph_URL


def dummy(DIN, Product_Name):
	return DIN + Product_Name


def get_pdf_urls(df):
	pdf_urls_list =[]
	for row in range(df.shape[0]):
		DIN = df.loc[row,'DIN']
		Product_Name = df.loc[row,'Brand Name']
		pdf_urls_list.append(get_ProductMonograph_download_URL(DIN, Product_Name))
		#pdf_urls_list.append(dummy(DIN, Product_Name))
	return pdf_urls_list
		

def input(PATH_TO_XLSX):
	df = pd.read_excel(PATH_TO_XLSX)
	df = df.rename(columns=lambda x: x.strip())  #Clean up whitespace column names
	df = df.drop(columns = 'Drug Class')
	df = df.dropna()
	for col in df.columns:  #Clean up whitespace in rows
	    df[col] = df[col].astype(str).str.strip()
	#fixing non-zero prefix in excel
	for i in range(df.shape[0]):
		if len(df.loc[i,'DIN']) < 8:
			df.loc[i,'DIN'] = '0' + df.loc[i,'DIN']
	return df


def main():
	pass
# 	createListOfDINsAutomaticallyFromPDF()
# 	get_list_of_DINs_and_productName()
	# df = input(r'ListOfDINs.xlsx')
	# print(df)
 	#pdf_urls_list = get_pdf_urls(df)
# 	createListOfPdfUrls()
# 	download_pdfs_locally()
# 	openPdfAndGrabDrugClassForEachPairOfDin()
# 	returnXLSofDINsProductNameAndDrugClass()

if __name__ == '__main__':
	#df = input(r'ListOfDINs copy.xlsx')
	#pdf_urls_list = get_pdf_urls(df)


