import os
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .models import Book

BOOK_IMAGES_DIR = "media/book_images"
os.makedirs(BOOK_IMAGES_DIR, exist_ok=True)

BOOK_BASE_URL = "https://books.toscrape.com/"
RATING_MAP = {
    'One': 1,
    'Two': 2,
    'Three': 3,
    'Four': 4,
    'Five': 5
}

def scrape_books():
    Book.objects.all().delete()  # Nettoie la table avant de scraper

    page_url = BOOK_BASE_URL + "catalogue/page-1.html"
    count = 0

    while page_url and count < 50:
        res = requests.get(page_url)
        soup = BeautifulSoup(res.text, 'html.parser')

        for article in soup.select('article.product_pod'):
            if count >= 50:
                break

            rating_class = article.p['class'][1]
            rating = RATING_MAP.get(rating_class, 0)
            if rating < 3:
                continue

            book_rel_url = article.h3.a['href'].replace('../../../', '')
            book_url = urljoin(BOOK_BASE_URL + 'catalogue/', book_rel_url)

            # Détail du livre
            detail = requests.get(book_url)
            detail_soup = BeautifulSoup(detail.text, 'html.parser')
            title = detail_soup.h1.text.strip()
            price = detail_soup.find('p', class_='price_color').text.strip()
            stock = detail_soup.find('p', class_='instock availability').text.strip()

            desc_tag = detail_soup.find('div', id='product_description')
            description = desc_tag.find_next_sibling('p').text.strip() if desc_tag else "Pas de description"

            img_rel_url = detail_soup.find('div', class_='item active').img['src']
            image_url = urljoin(book_url, img_rel_url)

            img_name = ''.join(c if c.isalnum() else '_' for c in title)[:100] + ".jpg"
            image_local_path = os.path.join(BOOK_IMAGES_DIR, img_name)

            try:
                img_data = requests.get(image_url).content
                with open(image_local_path, 'wb') as handler:
                    handler.write(img_data)
            except Exception as e:
                print(f"Erreur image {image_url}: {e}")
                image_local_path = ""

            # Enregistrement
            Book.objects.create(
                title=title,
                price=price,
                stock=stock,
                description=description,
                image_url=image_url,
                image_local=f"book_images/{img_name}"
            )
            count += 1

        next_btn = soup.select_one('li.next > a')
        page_url = urljoin(page_url, next_btn['href']) if next_btn else None
