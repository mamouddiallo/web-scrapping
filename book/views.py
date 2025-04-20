import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from django.shortcuts import render, redirect
from .models import Book
from django.shortcuts import get_object_or_404
from config.tasks import run_task


BASE_URL = "https://books.toscrape.com/"
IMAGES_DIR = "media/book_images"

# Mapping des étoiles
rating_map = {
    'One': 1,
    'Two': 2,
    'Three': 3,
    'Four': 4,
    'Five': 5
}

def book_index(request):
    books = Book.objects.filter(rating__gte=3)  # Filtrer les livres avec une note >= 3
    return render(request, 'book/index.html', {'books': books})

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'book/detail.html', {'book': book})

def scrape_books(request):
    Book.objects.all().delete()  # (optionnel) vider la table avant chaque scrap

    os.makedirs(IMAGES_DIR, exist_ok=True)
    page_url = BASE_URL + "catalogue/page-1.html"
    count = 0

    while page_url and count < 50:
        try:
            res = requests.get(page_url, timeout=10)
            res.raise_for_status()
        except Exception as e:
            print(f"Erreur lors du chargement de la page {page_url} : {e}")
            break

        soup = BeautifulSoup(res.text, 'html.parser')

        for article in soup.select('article.product_pod'):
            if count >= 50:
                break

            rating_class = article.p.get('class', [None, None])[1]
            rating = rating_map.get(rating_class, 0)
            if rating < 3:
                continue

            book_rel_url = article.h3.a['href'].replace('../../../', '')
            book_url = urljoin(BASE_URL + 'catalogue/', book_rel_url)

            try:
                detail = requests.get(book_url, timeout=10)
                detail.raise_for_status()
                detail_soup = BeautifulSoup(detail.text, 'html.parser')

                title = detail_soup.h1.text.strip()
                price = detail_soup.find('p', class_='price_color').text.strip()
                stock = detail_soup.find('p', class_='instock availability').text.strip()

                desc_tag = detail_soup.find('div', id='product_description')
                description = desc_tag.find_next_sibling('p').text.strip() if desc_tag else "Pas de description"

                img_rel_url = detail_soup.find('div', class_='item active').img['src']
                image_url = urljoin(book_url, img_rel_url)

                img_name = ''.join(c if c.isalnum() else '_' for c in title)[:100] + ".jpg"
                image_local_path = os.path.join(IMAGES_DIR, img_name)

                try:
                    img_data = requests.get(image_url, timeout=10).content
                    with open(image_local_path, 'wb') as handler:
                        handler.write(img_data)
                except Exception as e:
                    print(f"Erreur image {image_url}: {e}")
                    image_local_path = ""

                # Enregistrement en BDD
                Book.objects.create(
                    title=title,
                    price=price,
                    stock=stock,
                    description=description,
                    image_url=image_url,
                    image_local=f"book_images/{img_name}",
                    rating=rating  # Ajout de la note du livre
                )
                count += 1

            except Exception as e:
                print(f"Erreur lors du scraping du livre {book_url}: {e}")
                continue

        next_btn = soup.select_one('li.next > a')
        page_url = urljoin(page_url, next_btn['href']) if next_btn else None

def start(request):
    run_task.delay()
    return redirect('book:book_index')  # Redirige vers la page d'index après le scraping
