# python version is 3.6.10
# ref: https://buzzorange.com/techorange/2017/08/04/python-scraping/
# ref: https://leemeng.tw/beautifulsoup-cheat-sheet.html
# ref: https://www.cnblogs.com/wj-1314/p/9429816.html
# SARS data: https://www.who.int/csr/sars/country/en/

import re
import csv
import threading
import numpy as np
import pandas as pd
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

from handle_path import handle_csv_path
from spinner import SpinnerThread

CSV_PATH = "covid19.csv"
FETCH_INDEX = 0
QUOTE_PAGE = "https://www.who.int/emergencies/diseases/novel-coronavirus-2019/situation-reports"


def get_pdf_links_filenames_dates():
    page = urllib2.urlopen(QUOTE_PAGE)
    soup = BeautifulSoup(page, 'html.parser')
    
    links_tag = soup.find_all('div', {'class': 'sf-content-block content-block'})[10].find_all('a')
    
    all_links_filenames_dates = list()
    for raw_link in links_tag:
        link = "https://www.who.int" + raw_link.get('href')
        filename = get_pdf_filename_from_link(link)
        date = get_date_from_filename(filename)
        all_links_filenames_dates.append([link, filename, date])
    
    all_links_filenames_dates = np.unique(all_links_filenames_dates, axis=0)
    all_links_filenames_dates = sorted(all_links_filenames_dates, key=lambda l:l[2], reverse=True)
    
    all_datas_pd = pd.DataFrame(all_links_filenames_dates, columns = ['links', 'filenames', 'dates'])
    print(all_datas_pd)
    return all_datas_pd

def get_pdf_filename_from_link(link):
    try:
        filename = "2020" + link.split("2020")[1].split('?')[0]
    except Exception as ex:
        print("link format is not right: " + link)
        filename = ""
    
    return filename

def get_date_from_filename(filename):
    date = filename[0:8]
    year = date[:4]
    month = date[4:6]
    day = date[6:]
    
    date_str = year + "/" + month + "/" + day
    return date_str


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

all_datas_pd = get_pdf_links_filenames_dates()
download_link = all_datas_pd['links'][FETCH_INDEX]
download_filename = all_datas_pd['filenames'][FETCH_INDEX]
download_date = all_datas_pd['dates'][FETCH_INDEX]
download_pdf(download_link, download_filename)
print("fetch total number of patient from PDF " + download_filename)
total = get_total(download_filename)
print("total: ", total)

append_total_number_to_csv(download_date, total)

spinner_thread.join()
