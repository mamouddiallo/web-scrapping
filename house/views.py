from django.shortcuts import render

# Create your views here.

def house_index(request):
    return render(request, 'house/index.html')
