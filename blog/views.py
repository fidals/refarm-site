from django.shortcuts import render, get_object_or_404
from .models import Post


def posts_list(request):
    """Simple all pages list"""
    return render(request, 'blog/list.html', {'posts': Post.objects.all()})


def post_item(request, post_id):
    """Renders page on its own url"""
    return render(request, 'blog/page.html', {
        'post': get_object_or_404(Post, id=post_id)
    })
