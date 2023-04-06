# Unstructured Data to Structured Data

For this project I use Selenium to scrape Health Canada's database and collect the product monograph pdfs. I then convert the cover page to an image and then use Google's OCR Tesseract engine to convert the image into a searchable pdf. This cleans the cover pages and normalizes the bounding box coordinates of all text blocks in the product monographs pdfs. I then extract the drug class based on the fact that it's between the 6th and the 9th text block. I subset these textblocks and then look for the first left-aligned textbox. This reveals the textbox containing the drug class. The final output is a csv with the DIN, Product Name and Drug Class.

## Setup

1. Clone the repo by running:
```
git clone https://github.com/MubassirAhmed/AON_assignment.git
```

2. Install the required packages:
```
pip install -r requirements.txt
```

3. Install pyTesseract for your system:
For Mac OS
```
brew install tesseract
```

For Unix-based machine
```
sudo apt install tesseract-ocr
```

4. Execute the script
```
python main.py
```
