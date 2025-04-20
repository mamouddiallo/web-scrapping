from book.jobs import scrape_books
from celery import shared_task
from  config.celery import app
from olabo.jobs import scrape_olabo
from quote.jobs import scrape_quotes
from ecommerce.jobs import scraper_kilimall_view

#@app.task
@shared_task
def run_task():
    scrape_books()
    
    
@shared_task
def run_olabo():
    scrape_olabo()
    
@shared_task
def run_quote():
    scrape_quotes()
    
@shared_task
def run_ecommerce():
    scraper_kilimall_view()
    
