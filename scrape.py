import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
import fitz
from pdf2image import convert_from_path
import pytesseract

def get_ProductMonograph_download_URL(DIN,product_name):
	options = Options()
	options.add_argument("--headless=new")
	options.add_argument("--window-size=1920,1200")
	DRIVER_PATH = '.chromedriver'
	driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)

	#Page 1, entering DIN and product name
	driver.get("https://health-products.canada.ca/dpd-bdpp/")
	#time.sleep(1)
	DIN_field = driver.find_element(By.ID, "din").send_keys(DIN)
	#time.sleep(1)
	product_field = driver.find_element(By.ID, "product").send_keys(product_name)
	#time.sleep(1)
	search = driver.find_element("xpath", "//input[@value='Search']").click()
	#time.sleep(1)
	#Page 2, choosing the first result
	try:
		Click_ProductInfo_HyperLink = driver.find_element("link text", DIN).click()
		#time.sleep(1)
	#Page 3, getting the pdf link
	except:
		pass

	finally:
		Product_Monograph_URL = driver.find_element(By.CLASS_NAME, 'glyphicon-paperclip').find_element(By.TAG_NAME, 'a').get_attribute('href')
		#time.sleep(1)
		driver.quit()
	return Product_Monograph_URL


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


def get_pdf_urls(df):
	for row in range(df.shape[0]):
		try:
			df.loc[row, r'PDF Link'] = get_ProductMonograph_download_URL(
											DIN = df.loc[row,'DIN'],
											product_name = df.loc[row,'Brand Name']
											)
			print('SUCCESS: collected pdf URL for ' + df.loc[row,'DIN'] + ' and record number ' + str(row))
		except:
			print('FAIL: could not collect pdf URL for ' + df.loc[row,'DIN'] + ' and record number ' + str(row))

	# Create txt file with links
	with open('pdf_links.csv', 'w') as f:
		f.write('DIN,Brand Name,PDF Link\n')
		for i in range(df.shape[0]):
			f.write(f"{df.loc[i,'DIN']},{df.loc[i,'Brand Name']},{df.loc[i,'PDF Link']}\n")



def download_pdfs():
	df = pd.read_csv('pdf_links.csv', dtype = str)
	for i in range(df.shape[0]):
		try:
			download(url = df.loc[i,'PDF Link'], file_name = df.loc[i,'DIN'])
			print('SUCCESS: downloaded product monograph for ' + df.loc[i,'DIN'] + ' and record number ' + str(i))
		except:
			print('FAIL: couldn\'t download product monograph for ' + df.loc[i,'DIN'] + ' and record number ' + str(i))


def download(url, file_name):
	""" PDF will be dowloaded into same dir as main.py
	"""
	headers = {"User-Agent": "Chrome/51.0.2704.103",}
    # Send GET request
	response = requests.get(url, headers=headers)
    # Save the PDF
	try:
	    f = open(file_name + '.pdf', "wb")
	    f.write(response.content)
	    f.close()
	except:
	    pass
	    #print(response.status_code)


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


def pdftoimage(file_path):
	convert_from_path(file_path)[0].save(file_path.replace('.pdf','')+'.jpg', 'JPEG')



def imagetopdf(file_path):
    pdf = pytesseract.image_to_pdf_or_hocr(file_path, extension='pdf')
    with open('OCR-' + file_path.replace('.jpg','') + '.pdf' , 'w+b') as f:
        f.write(pdf) # pdf type is bytes by default
        
     
def get_drug_class_PyMuPDF(file_path):
	with fitz.open(file_path) as pdf:
		first_page = list(pdf)[0]
		all_blocks = first_page.get_text('blocks')

		# Identify the first left-aligned textblock and printing the textbox immediately before 
		for i, block in enumerate(all_blocks):
			# initialize
			x1 = round(block[0])
			block_index = block[5]

			# 6 - 9 because this is where the drug class is usually found
			if block_index >= 6 and block_index <= 9:
				if x1 >= 100 and x1 <= 300:
					print(all_blocks[i-1][4].strip())
					return all_blocks[i-1][4].strip()
   		# Notes:
		# (x0, y0, x1, y1, 'lines of the block', block_no, block_type)
     
     
if __name__ == '__main__':
	#get_pdf_urls(input(r'ListOfDINs copy.xlsx'))
	#download_pdfs()
	df = pd.read_csv('pdf_links.csv', dtype = str)
	df['Drug Class'] = ''
	df = df.drop(columns='PDF Link')
	for i in range(df.shape[0]):
		print(df.loc[i, 'DIN'])
		#pdftoimage( df.loc[i, 'DIN'] + '.pdf' )
		#imagetopdf( df.loc[i, 'DIN'] + '.jpg' )
		df.loc[i , 'Drug Class'] = get_drug_class_PyMuPDF( 'OCR-' + df.loc[i, 'DIN'] + '.pdf' )
		print('\n')
	df.to_excel(r'List of DINS with Drug Class.xlsx')