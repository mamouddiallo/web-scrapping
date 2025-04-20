# scraper/jobs.py

import requests
from bs4 import BeautifulSoup
from django.utils import timezone
from .models import ProduitKilimall
from celery import shared_task

@shared_task
def scraper_kilimall_view():
    url = "https://www.kilimall.co.ke/category/tvaudiovideo?id=2069&form=category"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {"message": "Erreur lors du chargement de la page", "status": response.status_code}

    soup = BeautifulSoup(response.text, "html.parser")

    produits_html = soup.find_all("div", class_="product-item")
    print(f"🔍 {len(produits_html)} produits trouvés")

    produits_ajoutes = []

    for produit in produits_html:
        try:
            a_tag = produit.find("a", href=True)
            lien = "https://www.kilimall.co.ke" + a_tag["href"]
            print(f"🧩 Lien trouvé : {lien}")

            if ProduitKilimall.objects.filter(lien=lien).exists():
                continue

            titre_tag = produit.find("div", class_="product-title")
            titre = titre_tag.get_text(strip=True) if titre_tag else "Sans titre"

            prix_tag = produit.find("span", class_="product-price")
            prix = prix_tag.get_text(strip=True).replace("KSh", "").replace(",", "") if prix_tag else "0"

            img_tag = produit.find("img")
            image = img_tag.get("data-src") or img_tag.get("src") if img_tag else ""

            produit_enregistre = ProduitKilimall.objects.create(
                titre=titre,
                prix=prix,
                lien=lien,
                image=image,
                date_ajout=timezone.now()
            )

            produits_ajoutes.append({
                "titre": produit_enregistre.titre,
                "prix": produit_enregistre.prix,
                "lien": produit_enregistre.lien,
                "image": produit_enregistre.image
            })
        except Exception as e:
            print(f"❌ Erreur produit : {e}")

    return {
        "message": f"{len(produits_ajoutes)} nouveaux produits ajoutés.",
        "produits": produits_ajoutes
    }
