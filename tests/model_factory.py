from blog.models import Post


def set_default_posts(tests_object):
    """Set several Post instances as tests_object fields"""

    tests_object.test_news_post = Post.objects.get_or_create(
        name='ShopElectro go to IPO only after 15-n investment rounds',
        type='news',
    )[0]

    tests_object.test_navigation_post = Post.objects.get_or_create(
        name='contacts',
        type='navigation'
    )[0]

    tests_object.test_article_post = Post.objects.get_or_create(
        name='Why Fenich called as new Steve Jobs',
        type='article'
    )[0]
