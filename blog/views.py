from typing import Generator
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.urlresolvers import reverse

from .models import Post, get_crumbs


def post_types(request):
    """List of posts, that belong to given type"""

    def get_type_data(id_: str, type_: str) -> dict:
        return {
            'id': id_,
            'name': type_['name'],
            'slug': reverse('blog:posts', args=(id_,)),
        }

    def get_post_types() -> Generator:
        for id_, type_ in settings.APP_BLOG_POST_TYPES.items():
            yield get_type_data(id_, type_)

    return render(request, 'blog/post_types.html', {
        'post_types': get_post_types(),
        'breadcrumbs': get_crumbs(settings.CRUMBS['blog']),
    })


def posts(request, type_=''):
    """List of posts, that belong to given type"""
    return render(request, 'blog/posts.html', {
        'posts': Post.objects.filter(type=type_),
        'breadcrumbs': get_crumbs(settings.CRUMBS['blog']),
    })


def post_item(request, slug_, type_):
    """Renders page on its own url"""
    post = get_object_or_404(Post, slug=slug_, type=type_)
    return render(request, 'blog/post.html', {
        'page': post,
        'breadcrumbs': get_crumbs(post),
    })
