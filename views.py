from django.shortcuts import render

from .models import Page


def pages_list(request):
    """Simple all pages list"""
    pages = Page.objects.all()
    return render(request, 'list.html', {'pages': pages})


def page_item(request, page_id):
    """Renders page on its own url"""
    page = Page.objects.get(id=page_id)
    return render(request, 'page.html', {'page': page})
