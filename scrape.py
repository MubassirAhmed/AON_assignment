import pandas as pd
import numpy as np
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests


from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams, LTTextBoxHorizontal,LTTextContainer,LTChar
from pdfminer.converter import PDFPageAggregator

from PyPDF2 import PdfReader


from pathlib import Path
from typing import Iterable, Any

from pdfminer.high_level import extract_pages

import pdftotext

import fitz

import statistics

import spacy

from nltk.tokenize import sent_tokenize

import re

from pdf2image import convert_from_path
from PIL import Image

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





def get_drug_class_pdfminer(pdf_path):
	# PDF Miner
	document = open(pdf_path, 'rb')
	#Create resource manager
	rsrcmgr = PDFResourceManager()
	# Set parameters for analysis.
	laparams = LAParams()
	# Create a PDF page aggregator object.
	device = PDFPageAggregator(rsrcmgr, laparams=laparams)
	interpreter = PDFPageInterpreter(rsrcmgr, device)
	#for page in PDFPage.get_pages(document):
	page = list(PDFPage.get_pages(document))[0]
	interpreter.process_page(page)
	# receive the LTPage object for the page.
	layout = device.get_result()
	drug_class = ''
	print(layout)
	# for LTTextBox in layout:
	# 	print(LTTextBox.get_text())
	# # 	count = 0
	# 	for LTTextLine in LTTextBox:
	# 		count += 1
	# 	if count > 1 :
	# 		break
	# 	else:
	# 		drug_class = LTTextLine.get_text()
	# print(drug_class)




def get_drug_class_pdfminer_six(pdf_path):
	""" The rule based logic implemented:
		1. all of address is in a single text box
		2. no element before address element has more than one item in their textbox
		3. therefore the last element before the textbox with multi. items is the drug class element
		4. drug class element is always before the address element
	"""
	page = list(extract_pages(pdf_path))[0]
	drug_class = ''
	for LTTextBox in page:
		count = 0
		for LTTextLine in LTTextBox:
			count += 1
		if count > 1 :
			break
		else:
			drug_class = LTTextLine.get_text()
	print(drug_class)






def get_drug_class_PyPDF2():
	df = pd.read_csv('pdf_links.csv', dtype = str)
	for i in range(df.shape[0]):
		reader = PdfReader(df.loc[i,'DIN'] + ".pdf")
		page = reader.pages[0]
		print(page.extract_text())






def get_drug_class_pdftotext(path2):
	with open(path2, "rb") as f:
		pdf = pdftotext.PDF(f)
	print(pdf[0])
	print(r'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
	print(r'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')




def show_ltitem_hierarchy(o: Any, depth=0):
		"""Show location and text of LTItem and all its descendants"""
		if depth == 0:
		    print('element                        fontname             text')
		    print('------------------------------ -------------------- -----')
		print(
		    f'{get_indented_name(o, depth):<30.30s} '
		    f'{get_optional_fontinfo(o):<20.20s} '
		    f'{get_optional_text(o)}'
		)
		if isinstance(o, Iterable):
		    for i in o:
		        show_ltitem_hierarchy(i, depth=depth + 1)

def get_indented_name(o: Any, depth: int) -> str:
    """Indented name of class"""
    return '  ' * depth + o.__class__.__name__

def get_optional_fontinfo(o: Any) -> str:
    """Font info of LTChar if available, otherwise empty string"""
    if hasattr(o, 'fontname') and hasattr(o, 'size'):
        return f'{o.fontname} {round(o.size)}pt'
    return ''

def get_optional_text(o: Any) -> str:
    """Text of LTItem if available, otherwise empty string"""
    if hasattr(o, 'get_text'):
        return o.get_text().strip()
    return ''

def show_tree(pdf_path):
	path = Path(pdf_path).expanduser()
	pages = list(extract_pages(path))[0]
	show_ltitem_hierarchy(pages)




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



def _get_drug_class_PyMuPDF(file_path):
	with fitz.open(file_path) as pdf:
		first_page = list(pdf)[0]
		median_list = []
		nlp = spacy.load("en_core_web_sm")
		curated_blocks = []
		all_blocks = first_page.get_text('blocks')

		# Curating text boxes that are centre justified
		for block in all_blocks:
			# initialize
			x1 = round(block[0])
			x2 = round(block[2])
			text = block[4]
			text_length = len(block[4])
			index_block = block[5]
			midpoint = round( ( (x2 - x1) / 2) + x1 )
			print(str(index_block) + " - " + str(x1) + ", " + str(x2) + ", " + str(midpoint) + ", " + repr(text))
   
			# Select Center Justified textboxes + drop if 'page' in textbox
			if (midpoint > 860 and midpoint < 895 and text_length  > 3 and 'page' not in text.lower() ):
				curated_blocks.append(block)
				# print(str(index_block) + " - " + str(x1) + ", " + str(x2) + ", " + str(midpoint) + ", " + repr(text))

		# unpacking nested blocks
		temp = []
		for i in range(len(curated_blocks)):
			unpacked_strings = re.sub(r'\n+', '\n', curated_blocks[i][4]).strip().splitlines()
			while(" " in unpacked_strings):
				unpacked_strings.remove(" ")
			if unpacked_strings: # Because sometimes it can be an empty list (cuz one of the textblocks was just ' \n ')
				for string in unpacked_strings:
					temp.append([string][0])
		curated_blocks = temp

		# Edge cases: Ignore if last center justified bounding box is a sentence + ignore http links
		for i in range(len(curated_blocks)):
			textblock = curated_blocks[-(i + 1)]
			doc = nlp(textblock)

			pos_list =[token.pos_ for token in doc]
			if 'AUX' in pos_list:
				continue
	
			token_text = [token.text for token in doc]
			check_for_http = [1 for token in token_text if 'http' in token]
			if 1 in check_for_http:
				continue
			
			print(textblock)
			break

		# Notes:
		# (x0, y0, x1, y1, 'lines of the block', block_no, block_type)
		# x0: 50 is almost border left, and x1: 527 is almost border right

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
					break
   
     
if __name__ == '__main__':
	#get_pdf_urls(input(r'ListOfDINs copy.xlsx'))
	#download_pdfs()
	#get_drug_class_PyPDF2()
	#get_drug_class_pdfminer()
	#get_drug_class_pdftotext('02496844.pdf')
	#get_drug_class_PyMuPDF('OCR-02510839.pdf')
	#show_tree('02510839.pdf')
	df = pd.read_csv('pdf_links.csv', dtype = str)
	for i in range(df.shape[0]):
		print(df.loc[i, 'DIN'])
		# pdftoimage( df.loc[i, 'DIN'] + '.pdf' )
		# imagetopdf( df.loc[i, 'DIN'] + '.jpg' )
		get_drug_class_PyMuPDF( 'OCR-' + df.loc[i, 'DIN'] + '.pdf' )
	#imagetopdf('02524589.jpg')

	


	

		# with open('pdf_links.txt') as f:
		# 	urls = [link.rstrip() for link in f]
		# 	for url in urls:


		# for i in range(df.shape[0]):
		# 	try:
		# 		url = df.loc[i, 'PDF link']
		# 		filename = df.loc[i, 'DIN']
		# 		download_pdf(url, filename)
		# 	except:
		# 		print('unable to download ' + df.loc[i,'DIN'])


