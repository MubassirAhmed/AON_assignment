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
import os, sys



def scrape_health_canada(DIN,product_name):
	# Setting up Selenium config
	options = Options()
	options.add_argument("--headless=new")
	options.add_argument("--window-size=1920,1200")
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
	
	# If redirected to Page 2, choosing the first result
	try:
		Click_ProductInfo_HyperLink = driver.find_element("link text", DIN).click()
		#time.sleep(1)
	
	# Page 3, getting the pdf link
	except:
		pass

	finally:
		Product_Monograph_URL = driver.find_element(By.CLASS_NAME, 'glyphicon-paperclip').find_element(By.TAG_NAME, 'a').get_attribute('href')
		#time.sleep(1)
		driver.quit()
	return Product_Monograph_URL



def cleanExcelfile(PATH_TO_XLSX):
	df = pd.read_excel(PATH_TO_XLSX)
	df = df.rename(columns=lambda x: x.strip())  # Clean up whitespace column names
	try:
		df = df.drop(columns = 'Drug Class')
	except:
		pass
	df = df.dropna()  # Drop rows with empty values
	for col in df.columns:  # Clean up whitespace in rows
		df[col] = df[col].astype(str).str.strip()
	# Fixing non-zero prefix in excel
	for i in range(df.shape[0]):
		if len(df.loc[i,'DIN']) < 8:
			df.loc[i,'DIN'] = '0' + df.loc[i,'DIN']
	return df



def scrape_productMonographs_URLs(df):
	# Calls the actual scraper 
	print('\n Scraping product monograph URLs...')
	for row in range(df.shape[0]):
		try:
			df.loc[row, r'PDF Link'] = scrape_health_canada(DIN = df.loc[row,'DIN'], product_name = df.loc[row,'Brand Name'])
			print('SUCCESS: scraped pdf URL for ' + df.loc[row,'DIN'] + ' and row number ' + str(row))
		except:
			pass
			print('FAIL: could not scrape pdf URL for ' + df.loc[row,'DIN'] + ' and row number ' + str(row))
	# Creates txt file with product monograph URLS (i.e. download links)
	with open('pdf_links.csv', 'w') as f:
		f.write('DIN,Brand Name,PDF Link\n')
		for i in range(df.shape[0]):
			f.write(f"{df.loc[i,'DIN']},{df.loc[i,'Brand Name']},{df.loc[i,'PDF Link']}\n")



def download_productMonographs():
	print('Downloading product mongraph pdfs locally (to same folder as script)...')
	df = pd.read_csv('pdf_links.csv', dtype = str)  # Read txt file with product monograph URLS (i.e. download links)
	# Call the actual downloader
	for i in range(df.shape[0]):
		try:
			download(url = df.loc[i,'PDF Link'], file_name = df.loc[i,'DIN'])
			print('SUCCESS: downloaded product monograph for ' + df.loc[i,'DIN'] + ' and row number ' + str(i))
		except:
			print('FAIL: couldn\'t download product monograph for ' + df.loc[i,'DIN'] + ' and row number ' + str(i))



def download(url, file_name):
	headers = {"User-Agent": "Chrome/51.0.2704.103",}
	response = requests.get(url, headers=headers)  # Send GET request
	# Save the PDF
	try:
		f = open(file_name + '.pdf', "wb")
		f.write(response.content)
		f.close()
	except:
		print(response.status_code)
	### Note: PDF will be dowloaded into same dir as scrape.py



def pdftoimage(file_path):
	# Converts first page of product monograph pdf to img
	doc = fitz.open(file_path)
	doc.select([0])
	doc.save('first_page-'+file_path)
	try:
		convert_from_path('first_page-'+file_path)[0].save(file_path.replace('.pdf','')+'.jpg', 'JPEG')
	except:
		print('Couldn\'t convert ' + file_path + ' to image')
	os.remove('first_page-' + file_path)
	#os.remove(file_path)



def OCRimage(imagefile):
	# Scans PDF's image with Google's OCR engine, to create a clean machine-readable first page
	try:
		pdf = pytesseract.image_to_pdf_or_hocr(imagefile, extension='pdf')
		with open('OCR-' + imagefile.replace('.jpg','') + '.pdf' , 'w+b') as f:
			f.write(pdf)
	except:
		print('Couldn\'t use OCR scan on ' + imagefile)
	os.remove(imagefile)   
	 
	 
	 
def get_drug_class_PyMuPDF(file_path):
	# Opens first page of PDF 
	with fitz.open(file_path) as pdf:
		first_page = list(pdf)[0]
		all_blocks = first_page.get_text('blocks')  # Extracts all textblocks
		result = ''
		
		# Identify the textblock of the 'Drug Class'
		### Note: It is assumed that the drug class is the last line of text that is center-justified
		print('Printing cleaned textblocks')
		for i, block in enumerate(all_blocks):
			x1 = round(block[0])
			block_index = block[5]
			print(str(round(block[0])) + " x-cordinate : " + block[4])
			# Check lines 6 to 9 because this is where the drug class is usually found
			if block_index >= 6 and block_index <= 9:
				if x1 >= 100 and x1 <= 300:   # textblock is left-aligned if x1 coordinate is in the 100s or 200s
					print('Collected: ' + all_blocks[i-1][4].strip())
					result = all_blocks[i-1][4].strip()   # Collect the textblock that appears right before the first left-aligned textblock
					break
		os.remove(file_path)
		return result
		### Notes: block object is a list of: (x0, y0, x1, y1, text, block_no, block_type)
	 
	 
	 
if __name__ == '__main__':
	# Parse CMD line arg
	file_path = r'ListOfDINs copy.xlsx'
	if len(sys.argv) > 1:
		file_path = sys.argv[1]
		
	# Collecting product monograph pdfs
	scrape_productMonographs_URLs(cleanExcelfile(file_path))
	download_productMonographs()
	
	# Extract Drug Class from product monographs
	df = pd.read_csv('pdf_links.csv', dtype = str)  #  
	df['Drug Class'] = ''
	df = df.drop(columns='PDF Link')
	for i in range(df.shape[0]):
		print('Extracting drug class from ' + df.loc[i, 'DIN'] + '...')
		pdftoimage( df.loc[i, 'DIN'] + '.pdf' )
		OCRimage( df.loc[i, 'DIN'] + '.jpg' )
		df.loc[i , 'Drug Class'] = get_drug_class_PyMuPDF( 'OCR-' + df.loc[i, 'DIN'] + '.pdf' )
		print('\n ############################################################# \n')

	try:
		df.to_csv('ListOfDINs With Drug Class.csv')  # Create csv with extracted drug class
		print("Output filed saved to 'ListOfDINs With Drug Class.csv' \n")
	except:
		print('Failed to save to output file \n')
	
	print('Script Complete!')
	