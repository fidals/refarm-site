from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .models import Post, get_crumbs


def posts_list(request):
    """Simple all pages list"""
    return render(request, 'blog/list.html', {
        'posts': Post.objects.all(),
        'breadcrumbs': get_crumbs(settings.CRUMBS['blog']),
    })


def post_item(request, post_id):
    """Renders page on its own url"""
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'blog/page.html', {
        'post': post,
        'breadcrumbs': get_crumbs(post),
    })
