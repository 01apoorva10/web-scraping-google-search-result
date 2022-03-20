from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
from bs4 import BeautifulSoup
import requests
import mysql.connector
import pandas as pd

WEBSITE_LINKS = set()
NO_OF_PAGES = 2
LINKS_DESC_DICT = {}
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}


"""
CREATE DATABASE.
"""
conn = mysql.connector.connect(host="localhost", user="root", passwd="123mysqladmin")
cursor = conn.cursor()
cursor.execute('''CREATE DATABASE IF NOT EXISTS gscrape''')


"""
Selenium Webdriver to simulate search query.
"""
service = Service(executable_path=r'C:\chromedriver.exe')   # creating object of the service class
driver = webdriver.Chrome(service=service)
driver.maximize_window()
driver.delete_all_cookies()
driver.get("https://www.google.com/")
query = "what is super computer"
driver.find_element(By.NAME, "q").send_keys(query)
time.sleep(3)
driver.find_element(By.CLASS_NAME, "gNO89b").click()


"""
Get website links from first page.
"""
for page in range(1, NO_OF_PAGES):
    url = "http://www.google.com/search?q=" + query + "&start=" +str((page - 1) * 10)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # soup = BeautifulSoup(r.text, 'html.parser')
    search = soup.find_all('div', class_="yuRUbf")
    for h in search:
        WEBSITE_LINKS.add(h.a.get('href'))

#print(WEBSITE_LINKS)
final_links = pd.DataFrame(WEBSITE_LINKS)
#print(final_links)

"""
INSERTING links INTO THE DATABASE TABLE LINKSONLY.
"""
conn = mysql.connector.connect(host="localhost", user="root", db="gscrape",passwd = "123mysqladmin")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS LINKSONLY(name VARCHAR(255) UNIQUE)''')

for i, row in final_links.iterrows():
    sql = "INSERT INTO LINKSONLY(name)" "VALUES (%s)"
    cursor.execute(sql, tuple(row))
    conn.commit()


"""
TEXT SCRAPING OF THE CORRESPONDING LINKS.
"""
def remove_tags(html: object):
    """
    Returns parsed contents of a website.

    params:
    html(bytes object): Raw html page of a website.

    return:
    soup(bs4 object): returns parsed html content.

    """
    soup = BeautifulSoup(html, "html.parser")
    content = soup.text

    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)

"""
Get a dict containing links with corresponding website content.
"""
for link in WEBSITE_LINKS:
    page = requests.get(link, headers=HEADERS)

    # Print the extracted data
    #print("\n")
    #print(remove_tags(page.content))
    LINKS_DESC_DICT[link] = remove_tags(page.content)


#print(len(LINKS_DESC_DICT))
rows = []
rows.append(LINKS_DESC_DICT)

final_links_desc = pd.DataFrame(list(LINKS_DESC_DICT.items()), columns=[0,1])
print(final_links_desc)

"""
INSERTING links INTO THE DATABASE TABLE LINKS_WITH_DESC.
"""
conn = mysql.connector.connect(host="localhost", user="root", db="gscrape", passwd="123mysqladmin")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS LINKS_WITH_DESC(name VARCHAR(255) UNIQUE, description LONGTEXT)''')

for i, row in final_links_desc.iterrows():
    #print(row)
    sql = "INSERT INTO LINKS_WITH_DESC(name,description)" "VALUES (%s,%s)"
    cursor.execute(sql, tuple(row))
    conn.commit()

