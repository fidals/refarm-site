from django.shortcuts import render, get_object_or_404
from .models import Page


def pages_list(request):
    """Simple all pages list"""
    pages = Page.objects.all()
    return render(request, 'blog/list.html', {'pages': pages})


def page_item(request, page_id):
    """Renders page on its own url"""
    page = get_object_or_404(Page, id=page_id)
    return render(request, 'blog/page.html', {'page': page})
