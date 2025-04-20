from django.shortcuts import render, get_object_or_404, redirect
from quote.models import QuoteModel
from .jobs import scrape_quotes # Assure-toi que ton job est dans un fichier jobs.py
from config.tasks import run_quote

def list_quote(request):
    quotes = QuoteModel.objects.all().order_by('-created_at')
    return render(request, 'quote/list.html', {'quotes': quotes})

def detail(request, id):
    quote = get_object_or_404(QuoteModel, id=id)
    return render(request, 'quote/detail.html', {'quote': quote})

def start_job(request):
    run_quote.delay()  
    return redirect('quote:index')
