import os
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .models import Product

OLABO_IMAGES_DIR = "media/olabo_images"
os.makedirs(OLABO_IMAGES_DIR, exist_ok=True)

PAGES = [
    "https://olabostore.ci/shop/",
    "https://olabostore.ci/shop/page/2/"
]

def get_description(link):
    try:
        res = requests.get(link)
        soup = BeautifulSoup(res.text, 'html.parser')
        description = []
        # Description courte
        desc_section = soup.select_one('div.woocommerce-product-details__short-description')
        if desc_section:
            for p in desc_section.find_all(['p', 'ul']):
                description.append(p.get_text(strip=True))
        return '\n'.join(description)
    except:
        return "Pas de description"

def scrape_olabo():
    Product.objects.all().delete()  # Nettoie la table avant de scraper

    for page_url in PAGES:
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        products = soup.select(".product-block")

        for product in products:
            try:
                name = product.select_one(".name a").get_text(strip=True)
                link = product.select_one(".name a")["href"]
                img_url = product.select_one("img")["src"]
                price_tag = product.select_one(".price .amount bdi")
                price = price_tag.get_text(strip=True) if price_tag else "Non précisé"

                availability = "Disponible" if "instock" in product.parent.get("class", []) else "Non disponible"

                description = get_description(link)

                img_name = img_url.split("/")[-1].split("?")[0]
                img_path = os.path.join(OLABO_IMAGES_DIR, img_name)
                img_full_url = urljoin(page_url, img_url)

                if not os.path.exists(img_path):
                    img_data = requests.get(img_full_url).content
                    with open(img_path, "wb") as f:
                        f.write(img_data)

                Product.objects.create(
                    name=name,
                    price=price,
                    availability=availability,
                    description=description,
                    image_url=img_full_url,
                    image_local=f"olabo_images/{img_name}"
                )
            except Exception as e:
                print(f"Erreur sur un produit : {e}")
                continue
