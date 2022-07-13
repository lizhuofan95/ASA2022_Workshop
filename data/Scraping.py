import pandas as pd, re
from bs4 import BeautifulSoup
from selenium import webdriver
import numpy as np

driver = webdriver.Chrome(executable_path = "chromedriver.exe")

driver.get("https://ethw.org/Oral-History:List_of_all_Oral_Histories")
content = driver.page_source
soup = BeautifulSoup(content)

links = []

for link in soup.find_all('a', attrs={'href': re.compile("/Oral-History")}):
    links.append(link.get('href'))

links.index("/Oral-History:Henry_B._Abajian")

links[48:]

interviews = pd.DataFrame(columns = ['person', 'interview', 'bio', 'section', 'speaker', 'text'])

for link in links[48:]:
    driver.get("https://ethw.org" + link)
    content = driver.page_source
    soup = BeautifulSoup(content)
    row = [[link.split(':')[1],
        soup.find('span', {'id': 'About_the_Interview'}).find_next('p').get_text() if soup.find('span', {'id': 'About_the_Interview'}) is not None else '', 
        soup.find_all('h2')[0].find_next('p').get_text() if soup.find_all('h2') is not None else '', 
        p.find_previous('h3').find_next('span', {'class' : 'mw-headline'}).get_text() if p.find_previous('h3') is not None else '',
        p.find('b').get_text(), 
        p.findNext('p').get_text()
    ] for p in soup.find_all('p') if (p.find('b') is not None) and (p.findNext('p') is not None)]
    interviews = pd.concat([interviews, pd.DataFrame(row, columns = ['person', 'interview', 'bio', 'section', 'speaker', 'text'])], axis = 0)

interviews = interviews.replace(r'\n',' ', regex=True)

interviews['speaker'] = interviews['speaker'].replace(r':', '', regex=True)

interviews.to_csv("oralhistory.csv", sep = "\t", encoding = 'utf-8-sig')

interviews = pd.read_csv("oralhistory.csv", sep = "\t", encoding = 'utf-8-sig')

interviews = interviews.rename(columns = {'Unnamed: 0': 'rowid'})

interviews.to_excel("oralhistory.xlsx", encoding = 'utf-8-sig')


import pandas as pd, numpy as np

original = pd.read_excel("oralhistory.xlsx", index_col=0)

data = original.dropna()

data['code'] = ''

data.loc[data['section'].str.contains("childhood|background", case=False), 'code'] = "Background"

grouped = data.groupby("person")

grouped['code'].any()

data = grouped.filter(lambda x: x['code'].any())

data = data.groupby(['person']).head(n=80)

data = pd.read_excel("oralhistory_coded.xlsx", index_col = 0)

data.loc[data['Codes']==np.nan, 'Codes'] = ''

grouped = data.groupby("Document")

grouped['Codes'].any()

data = grouped.filter(lambda x: x['Codes'].count() > 15)

data.to_excel("oralhistory_coded_short.xlsx")