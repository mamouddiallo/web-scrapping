from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

from quote.forms.quote_form import QuoteForm
from quote.models import TagModel


def scrape_quotes():
   with requests.Session() as session:
       url = "https://quotes.toscrape.com"

       page_number = 1

       next_page = True

       while next_page:
           response = session.get(f"{url}/page/{page_number}/")
           # print(response.text)

           if response.status_code != 200:
               print(f"Erreur: La page {page_number} est introuvable.")
               break

           soup = BeautifulSoup(response.text, "html.parser")
           # print(soup)

           quotes = soup.find_all('div', class_='quote')

           next_button = soup.find('li', class_='next')
           # print(quotes)

           for quote in quotes:
               citation = quote.find('span', class_='text').text
               # print(text)
               author = quote.find('small', class_='author').text
               tags = [tag.text for tag in quote.find_all('a', class_='tag')]

               quote_url = quote.find_all('a')[0]['href']
               quote_url_abs = urljoin(url,quote_url)

               response = session.get(quote_url_abs)
               soup = BeautifulSoup(response.text,'html.parser')
               author_born_date = soup.find('span', class_='author-born-date').text
               author_description = soup.find('div',class_='author-description').text


               tag_instances = []

               for tag in tags:
                    tag_instance = TagModel.objects.get_or_create(name=tag)
                    tag_instances.append(tag_instance)

               quote_form = QuoteForm(
                   {
                       'text': author_description,
                       'quote': citation,
                       'author': author,
                       #'tags':tag_instance
                   })


               if quote_form.is_valid():
                   quote_instance = quote_form.save()
                   for tag in tag_instances:
                       quote_instance.tags.add(tag[0].id)


           if next_button:
               page_number += 1
           else:
               next_page = False




