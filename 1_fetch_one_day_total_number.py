# python version is 3.6.10
# ref: https://buzzorange.com/techorange/2017/08/04/python-scraping/
# ref: https://leemeng.tw/beautifulsoup-cheat-sheet.html
# ref: https://www.cnblogs.com/wj-1314/p/9429816.html
# SARS data: https://www.who.int/csr/sars/country/en/

import urllib.request as urllib2
from bs4 import BeautifulSoup

from pdfminer.pdfparser import  PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfdevice import PDFDevice
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal,LAParams
from pdfminer.pdfpage import PDFTextExtractionNotAllowed

import re
import csv
import threading

from handle_path import handle_csv_path
from spinner import SpinnerThread

CSV_PATH = "covid19.csv"
FETCH_INDEX = 0
QUOTE_PAGE = "https://www.who.int/emergencies/diseases/novel-coronavirus-2019/situation-reports"


def remove_redundant_in_list(input_list):
    return list( dict.fromkeys(input_list) )


def get_pdf_links():
    page = urllib2.urlopen(QUOTE_PAGE)
    soup = BeautifulSoup(page, 'html.parser')
    
    links_tag = soup.find_all('div', {'class': 'sf-content-block content-block'})[10].find_all('a')
    
    links = list()
    for raw_link in links_tag:
        links.append("https://www.who.int" + raw_link.get('href'))
    
    links = remove_redundant_in_list(links)
    links.sort(reverse = True)
    
    for i in range(0, len(links)):
        print(str(i) + " " + links[i])
    
    return links


def get_pdf_filenames_from_links(links):
    filenames = list()
    for link in links:
        try:
            filenames.append("2020" + link.split("2020")[1].split('?')[0])
        except Exception as ex:
            print("link format is not right: " + link)
    
    return filenames


def get_dates_from_filenames(filenames):
    dates = list()
    for filename in filenames:
        date = filename[0:8]
        year = date[:4]
        month = date[4:6]
        day = date[6:]
        dates.append(year + "/" + month + "/" + day)
    
    return dates

def download_pdf(link, filename):
    filedata = urllib2.urlopen(link)
    datatowrite = filedata.read()
     
    with open(filename, 'wb') as f:
        f.write(datatowrite)

# WHO PDF format is changed since 2020/5/1 
def get_total(filename):
    path = open(filename, 'rb')
    parser = PDFParser(path)
    document = PDFDocument(parser)
    temp_total = -1

    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    else:
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr,laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr,device)

        check_total = False

        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)
            layout = device.get_result()
            for x in layout:
                if(isinstance(x,LTTextBoxHorizontal)):
                  results = str(x.get_text())
                  if "Subtotal for all regions" in results:
                    check_total = True
                  if check_total:
                    # print("results: " + results)
                    temp_results = re.search( r'(.*)\n', results, re.M|re.I).group(1)
                    temp_results = temp_results.replace(" ", "").replace("\\n", "")
                    try:
                      temp_num = int(temp_results)
                      if temp_num > temp_total:
                        temp_total = temp_num
                    except ValueError:
                      continue
    
    return temp_total

def append_total_number_to_csv(date, total):
    with open(CSV_PATH, 'a') as csv_file:
        data = [ date,  total ]
        print(data)
        writer = csv.writer(csv_file)
        writer.writerow(data)

CSV_PATH = handle_csv_path()
print("output csv to " + CSV_PATH + " later")

spinner_thread = SpinnerThread()
spinner_thread.start()

links = get_pdf_links()
filenames = get_pdf_filenames_from_links(links)
dates = get_dates_from_filenames(filenames)

download_pdf(links[FETCH_INDEX], filenames[FETCH_INDEX])
print("fetch total number of patient from PDF " + filenames[FETCH_INDEX])
total = get_total(filenames[FETCH_INDEX])
print("total: ", total)

append_total_number_to_csv(dates[FETCH_INDEX], total)

spinner_thread.join()