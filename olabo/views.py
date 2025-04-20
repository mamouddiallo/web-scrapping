from django.shortcuts import render, get_object_or_404
from .models import Product
from django.shortcuts import redirect
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
from config.tasks import run_olabo

# Dossier où les images seront stockées
IMG_DIR = 'media/olabo_images'
os.makedirs(IMG_DIR, exist_ok=True)

PAGES = [
    "https://olabostore.ci/shop/",
    "https://olabostore.ci/shop/page/2/"
]

def get_full_product_info(link):
    try:
        res = requests.get(link)
        soup = BeautifulSoup(res.text, 'html.parser')
        infos = []

        # Description courte complète
        short_desc = soup.select_one('div#tabs-list-description')
        if short_desc:
            infos.append("DESCRIPTION DU PRODUIT :")
            for elem in short_desc.find_all(['p', 'ul', 'li']):
                text = elem.get_text(strip=True)
                if text:
                    infos.append(text)

        # Autres onglets WooCommerce (ex: reviews, etc.)
        tabs = soup.select('div.woocommerce-Tabs-panel')
        for tab in tabs:
            tab_title = tab.get('id', 'Section')
            infos.append(f"\n{tab_title.upper()} :")
            for content in tab.find_all(['p', 'ul', 'li', 'table']):
                text = content.get_text(strip=True)
                if text:
                    infos.append(text)

        return '\n'.join(infos)

    except Exception as e:
        print(f"[get_full_product_info] Erreur: {e}")
        return "Aucune information détaillée trouvée"


# Vue pour afficher les détails d'un produit
def olabo_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'olabo/detail.html', {'product': product})

# Fonction pour récupérer les produits
def scrape_olabo_data():
    Product.objects.all().delete()  # Optionnel: supprimer les anciens produits
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

                description = get_full_product_info(link)

                img_name = img_url.split("/")[-1].split("?")[0]
                img_path = os.path.join(IMG_DIR, img_name)
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

# Vue pour démarrer le scraping des produits Olabo
def start_olabo_job(request):
    run_olabo.delay()
    return redirect('olabo:olabo_index')

# Vue pour afficher la liste des produits
def index(request):
    products = Product.objects.all()
    return render(request, 'olabo/index.html', {'products': products})
