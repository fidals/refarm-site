from django.db.models.aggregates import Count
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from pages.views import CustomPageView
from pages.models import ModelPage


class CategoryTree(CustomPageView):
    """Render category tree structure."""

    template_name = 'catalog/catalog.html'
    category_model = None

    def get_context_data(self, **kwargs):
        assert self.category_model, 'Need define category_model field'
        context = super(CategoryTree, self).get_context_data(**kwargs)

        return {
            **context,
            'nodes': self.category_model.objects.all()
        }


class CategoryPage(DetailView):

    queryset = ModelPage.objects.all()
    template_name = 'catalog/category.html'
    context_object_name = 'page'

    def get_context_data(self, **kwargs):
        context = super(CategoryPage, self).get_context_data(**kwargs)
        model = self.object.model
        return {
            **context,
            'category': model,
            'children': model.get_children(),
            'products': model.products.all(),
        }


class ProductPage(DetailView):

    template_name = 'catalog/product.html'
    context_object_name = 'product'
    pk_url_kwarg = 'product_id'

    def get_context_data(self, **kwargs):
        context = super(ProductPage, self).get_context_data(**kwargs)

        return {
            **context,
            'page': context[self.context_object_name].page,
        }


class AbstractProductWithoutContent(ListView):

    model = None
    template_name = 'catalog/products_without_content.html'
    context_object_name = 'products'
    title = None

    def get_context_data(self, **kwargs):
        context = super(AbstractProductWithoutContent, self).get_context_data(**kwargs)
        return {
            **context,
            'title': self.title,
            'total_count': self.model.objects.count(),
        }


class ProductsWithoutImages(AbstractProductWithoutContent):

    title = 'Без фотографий'

    def get_queryset(self):
        queryset = super(ProductsWithoutImages, self).get_queryset()
        return queryset.annotate(images_count=Count('page__images')).filter(images_count=0)


class ProductsWithoutText(AbstractProductWithoutContent):

    title = 'Без описаний'

    def get_queryset(self):
        queryset = super(ProductsWithoutText, self).get_queryset()
        return queryset.filter(page__content='')
