from bs4 import BeautifulSoup
import requests
from requests.api import head
import csv

source = requests.get('https://repository.uisi.ac.id/view/subjects/T1.html').text

soup = BeautifulSoup(source,'lxml')

csv_file = open('repository.csv', 'w')

csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Judul', 'Author'])

for div in soup.find_all('p'):

    judul = div.a.em.text
    print(judul)

    author = div.span.text
    print(author)

    print()

    csv_writer.writerow([judul,author])

csv_file.close

