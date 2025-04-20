from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
import requests
from bs4 import BeautifulSoup
from django.shortcuts import get_object_or_404
from config.tasks import run_ecommerce
import os
from .models import ProduitKilimall

from django.http import JsonResponse
from bs4 import BeautifulSoup
import requests
from django.utils import timezone
from decimal import Decimal  # pour conversion juste avant l'enregistrement

from urllib.parse import urljoin
from urllib.request import urlretrieve

from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time
from urllib.parse import urljoin
from selenium.webdriver.common.action_chains import ActionChains



def scraper_kilimall_view():
    url = "https://www.kilimall.co.ke/category/tvaudiovideo?id=2069&form=category"

    # Vider la base
    ProduitKilimall.objects.all().delete()

    # Créer le dossier pour les images
    folder_name = "media/images_kilimall"
    os.makedirs(folder_name, exist_ok=True)

    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(5)  # attendre le chargement initial

    # Scroll progressif par lots de produits
    SCROLL_PAUSE_TIME = 2
    MAX_SCROLL_ATTEMPTS = 20

    last_count = 0
    attempts = 0

    while attempts < MAX_SCROLL_ATTEMPTS:
        items = driver.find_elements(By.CSS_SELECTOR, "div.listing-item[data-v-60f88a43]")
        current_count = len(items)
        print(f"{current_count} produits visibles")

        if current_count == last_count:
            attempts += 1
        else:
            attempts = 0
            last_count = current_count

        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(SCROLL_PAUSE_TIME)

    print(f"Nombre total de produits après scroll : {last_count}")

    # Récupération des produits
    items = driver.find_elements(By.CSS_SELECTOR, "div.listing-item[data-v-60f88a43]")

    for i, item in enumerate(items):
        try:
            title = item.find_element(By.CSS_SELECTOR, "p.product-title").text.strip()
            price = item.find_element(By.CSS_SELECTOR, "div.product-price").text.strip()
            img_tag = item.find_element(By.CSS_SELECTOR, "div.product-image img")
            link_tag = item.find_element(By.CSS_SELECTOR, "a[href]")

            image_url = (
                img_tag.get_attribute("src")
                or img_tag.get_attribute("data-src")
                or img_tag.get_attribute("data-original")
            )

            if image_url.startswith("//"):
                image_url = "https:" + image_url
            elif not image_url.startswith("http"):
                image_url = "https://" + image_url

            product_url = urljoin(url, link_tag.get_attribute("href"))

            print(f"\nProduit {i + 1}")
            print(f"Titre : {title}")
            print(f"Prix : {price}")
            print(f"Image : {image_url}")
            print(f"URL : {product_url}")

            # Télécharger l'image via requests
            image_path = os.path.join(folder_name, f"product_{i}.jpg")
            response = requests.get(image_url)
            with open(image_path, "wb") as f:
                f.write(response.content)
            print(f"Image sauvegardée dans {image_path}")

            # Enregistrer dans la base
            produit = ProduitKilimall(
                titre=title,
                prix=price,
                image_url=image_url,
                product_url=product_url,
                date_ajout=timezone.now()
            )
            produit.save()
            print(f"Produit {i + 1} sauvegardé")

        except Exception as e:
            print(f"Erreur pour le produit {i + 1} : {e}")

    driver.quit()

scraper_kilimall_view()


# Vue pour démarrer le scraping des produits Olabo
def start_ecommerce_job(request):
    run_ecommerce.delay()
    return redirect('ecommerce:ecom_index')

# Vue pour afficher la liste des produits
def index(request):
    products = ProduitKilimall.objects.all()
    return render(request, 'ecommerce/index.html', {'products': products})

# Vue pour afficher les détails d'un produit
def ecommerce_detail(request, pk):
    products = ProduitKilimall.objects.all().order_by('-date_ajout')
    return render(request, 'ecommerce/detail.html', {'product': products})